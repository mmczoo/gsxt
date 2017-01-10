package main

import (
	"bytes"
	"crypto/tls"
	"errors"
	"fmt"
	"net"
	"net/http"
	"net/url"
	"runtime/debug"
	"strings"
	"time"

	"golang.org/x/net/proxy"

	"encoding/base64"

	hproxy "github.com/mmczoo/gotools/proxy"
	"github.com/xlvector/dlog"
)

type RClient struct {
	st  *Statistic
	cfg *Config

	pxch chan *hproxy.Proxy
}

func NewRClient(st *Statistic, cfg *Config) *RClient {
	return &RClient{
		st:   st,
		cfg:  cfg,
		pxch: make(chan *hproxy.Proxy, 4096),
	}
}

const (
	IP_CLASS_B = 2
	IP_CLASS_C = 3
)

func genArg(px *hproxy.Proxy) string {
	//1.1.1.1:999&socks5
	if px == nil {
		return ""
	}
	host, port := px.HostPort()
	return base64.StdEncoding.EncodeToString([]byte(fmt.Sprintf("%s&%s&%s", host, port, px.Type)))
	//return base64.StdEncoding.EncodeToString([]byte(fmt.Sprintf("%s&%s", px.IP, px.Type)))

}

//notice: check ptype ipr
func (p *RClient) GenIPS(ptype, ipr string, ports []int, ipclass int) {
	dots := strings.Split(ipr, ".")
	switch ipclass {
	case IP_CLASS_C:
		if len(dots) < 3 {
			return
		}
		for _, port := range ports {
			for i := 254; i > 0; i-- {
				tmp := fmt.Sprintf("%s://%s.%s.%s.%d:%d", ptype, dots[0], dots[1], dots[2], i, port)
				px := hproxy.NewProxy(tmp)
				if px != nil {
					p.st.CReq++
					p.pxch <- px
				}
			}
		}
	case IP_CLASS_B:
		if len(dots) < 2 {
			return
		}
		for _, port := range ports {
			for i := 255; i > 0; i-- {
				for j := 254; j > 0; j-- {
					tmp := fmt.Sprintf("%s://%s.%s.%d.%d:%d", ptype, dots[0], dots[1], i, j, port)
					px := hproxy.NewProxy(tmp)
					if px != nil {
						p.st.BReq++
						p.pxch <- px
					}
				}
			}
		}
	default:
		return
	}
}

func gdail(netw, addr string) (net.Conn, error) {
	timeout := time.Duration(3) * time.Second
	deadline := time.Now().Add(timeout)
	c, err := net.DialTimeout(netw, addr, timeout)
	if err != nil {
		return nil, err
	}
	c.SetDeadline(deadline)
	tcp_conn := c.(*net.TCPConn)
	tcp_conn.SetKeepAlive(false)
	return tcp_conn, nil
}

func getTransport(p *hproxy.Proxy) *http.Transport {
	if p == nil {
		return nil
	}

	transport := &http.Transport{
		DisableKeepAlives:     true,
		ResponseHeaderTimeout: time.Second * 15,
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: true,
			MaxVersion:         tls.VersionTLS12,
			MinVersion:         tls.VersionTLS10,
			CipherSuites: []uint16{
				tls.TLS_RSA_WITH_RC4_128_SHA,
				tls.TLS_RSA_WITH_3DES_EDE_CBC_SHA,
				tls.TLS_RSA_WITH_AES_128_CBC_SHA,
				tls.TLS_RSA_WITH_AES_256_CBC_SHA,
				tls.TLS_ECDHE_ECDSA_WITH_RC4_128_SHA,
				tls.TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA,
				tls.TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA,
				tls.TLS_ECDHE_RSA_WITH_RC4_128_SHA,
				tls.TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA,
				tls.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA,
				tls.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA,
				tls.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,
				tls.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,
			},
		},
	}

	if p.Type == "socks5" {
		var auth *proxy.Auth
		if len(p.Username) > 0 && len(p.Password) > 0 {
			auth = &proxy.Auth{
				User:     p.Username,
				Password: p.Password,
			}
		} else {
			auth = &proxy.Auth{}
		}
		forward := proxy.FromEnvironment()
		dialSocks5Proxy, err := proxy.SOCKS5("tcp", p.IP, auth, forward)
		if err != nil {
			dlog.Warn("SetSocks5 Error:%s", err.Error())
			return nil
		}
		transport.Dial = dialSocks5Proxy.Dial
	} else if p.Type == "http" || p.Type == "https" {
		transport.Dial = gdail
		proxyUrl, err := url.Parse(p.String())
		if err == nil {
			transport.Proxy = http.ProxyURL(proxyUrl)
		} else {
			return nil
		}
	} else if p.Type == "socks4" {
		surl := "socks4://" + p.IP
		rsurl, err := url.Parse(surl)
		if err != nil {
			dlog.Warn("socks4 url parse: %v", err)
			return nil
		}
		forward := proxy.FromEnvironment()
		dialersocks4, err := proxy.FromURL(rsurl, forward)
		if err != nil {
			dlog.Warn("SetSocks4 Error:%s", err.Error())
			return nil
		}
		transport.Dial = dialersocks4.Dial
	}

	return transport
}

func (p *RClient) scan(i int) {
	var gclient = http.Client{
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			//dlog.Warn("Redirct: %s %v", req.URL.String(), req.Header)
			return errors.New("Redirect!")
		},
	}
	linkbase := p.cfg.PubHttp

	for {
		px := <-p.pxch
		/*
			arg := genArg(px)
			if len(arg) <= 0 {
				continue
			}
		*/
		//dlog.Println(px, arg)
		transport := getTransport(px)
		//dlog.Info("== %v %v", px, arg)

		if transport == nil {
			continue
		}

		gclient.Transport = transport
		//link := linkbase + "?arg=" + arg
		link := linkbase
		//dlog.Info("== %v %s", px, link)
		reqest, err := http.NewRequest("GET", link, nil)
		if err != nil {
			continue
		}
		reqest.Header.Add("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36")
		resp, _ := gclient.Do(reqest)
		if resp != nil && resp.Body != nil {
			p.st.ScanNum++
			buf := make([]byte, 256)
			_, err := resp.Body.Read(buf)
			if err == nil {
				fmt.Println(string(buf))
				if bytes.Contains(buf, []byte(p.cfg.Contain)) {
					fmt.Println("====", px.String())
				}
			}
			resp.Body.Close()
		}
	}
}

func (p *RClient) runAddrs() {
	defer func() {
		if r := recover(); r != nil {
			dlog.Println("ERROR: ", r)
			debug.PrintStack()
			go p.Run()
		}
	}()

	if len(p.cfg.Addrs) <= 0 {
		return
	}

	if p.cfg.AddrsIntv <= 60 {
		p.cfg.AddrsIntv = 60
	}
	if len(p.cfg.AddrsProtocl) == 0 {
		p.cfg.AddrsProtocl = append(p.cfg.AddrsProtocl, "http")
	}

	dlog.Info("-----run addrs")
	t := time.NewTicker(time.Duration(p.cfg.AddrsIntv) * time.Second)
	for {
		p.st.AddrsTimes++
		if len(p.cfg.Addrs) >= 0 {
			for _, ptype := range p.cfg.AddrsProtocl {
				for _, addr := range p.cfg.Addrs {
					px := hproxy.NewProxy(ptype + "://" + addr)
					if px != nil {
						p.st.AddrsReq++
						p.pxch <- px
					}
				}
			}
		}
		<-t.C
	}
}

func (p *RClient) runB() {
	defer func() {
		if r := recover(); r != nil {
			dlog.Println("ERROR: ", r)
			debug.PrintStack()
			go p.Run()
		}
	}()
	if len(p.cfg.BIp) <= 0 {
		return
	}

	if p.cfg.BIntv <= 60 {
		p.cfg.BIntv = 60
	}
	if len(p.cfg.BProtocl) == 0 {
		p.cfg.BProtocl = append(p.cfg.BProtocl, "http")
	}

	if len(p.cfg.BPorts) == 0 {
		p.cfg.BPorts = append(p.cfg.BPorts, 8080)
	}

	dlog.Info("-----run B")
	t := time.NewTicker(time.Duration(p.cfg.BIntv) * time.Second)
	for {
		p.st.BTimes++
		for _, pytpe := range p.cfg.BProtocl {
			for _, ip := range p.cfg.BIp {
				p.GenIPS(pytpe, ip, p.cfg.BPorts, IP_CLASS_B)
			}
		}
		<-t.C
	}
}

func (p *RClient) runC() {
	defer func() {
		if r := recover(); r != nil {
			dlog.Println("ERROR: ", r)
			debug.PrintStack()
			go p.Run()
		}
	}()
	if len(p.cfg.CIp) <= 0 {
		return
	}

	if p.cfg.CIntv <= 60 {
		p.cfg.CIntv = 60
	}
	if len(p.cfg.CProtocl) == 0 {
		p.cfg.CProtocl = append(p.cfg.CProtocl, "http")
	}

	if len(p.cfg.CPorts) == 0 {
		p.cfg.CPorts = append(p.cfg.CPorts, 8080)
	}

	dlog.Info("-----run C, %d", len(p.cfg.CIp))

	t := time.NewTicker(time.Duration(p.cfg.CIntv) * time.Second)
	for {
		p.st.CTimes++
		for _, pytpe := range p.cfg.CProtocl {
			for _, ip := range p.cfg.CIp {
				p.GenIPS(pytpe, ip, p.cfg.CPorts, IP_CLASS_C)
			}
		}

		<-t.C
	}
}

func (p *RClient) Run() {
	conc := p.cfg.AddrsQPS + p.cfg.BQPS + p.cfg.CQPS
	if conc < 10 {
		conc = 10
	}

	for i := 0; i < conc; i++ {
		go p.scan(i)
	}

	go p.runAddrs()
	go p.runB()
	go p.runC()
}
