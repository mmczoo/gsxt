package main

import (
	"encoding/base64"
	"fmt"
	"net/http"
	"strings"

	"github.com/xlvector/dlog"
)

type ScanHTTPSServer struct {
	model *Model
}

func NewScanHTTPSServer(m *Model) *ScanHTTPSServer {
	if m == nil {
		return nil
	}

	return &ScanHTTPSServer{
		model: m,
	}
}

func decrypt(arg string) ([]byte, error) {
	return base64.StdEncoding.DecodeString(arg)
}

func (p *ScanHTTPSServer) dealwith(px string) bool {
	tmp := strings.Split(px, "&")
	if len(tmp) != 3 {
		return false
	}
	proxy := fmt.Sprintf("%s://%s:%s", tmp[2], tmp[0], tmp[1])
	dlog.Info("px== %s", proxy)
	go p.model.SavePx(proxy, tmp[2])
	return true
}

func (p *ScanHTTPSServer) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	if r.Method != "GET" {
		//fmt.Fprintf(w, "HE")
		w.WriteHeader(500)
		return
	}
	r.ParseForm()

	arg, ok := r.Form["arg"]
	if !ok {
		//fmt.Fprintf(w, "HE")
		w.WriteHeader(501)
		return
	}
	ppt, err := decrypt(arg[0])
	if err != nil {
		w.WriteHeader(502)
		return
	}
	dlog.Info("==req: %v %v", string(ppt), r.RemoteAddr)

	ret := p.dealwith(string(ppt))
	if !ret {
		w.WriteHeader(503)
		return
	}
	//1.1.1.1&999&socks5
	fmt.Fprintf(w, "G")
}
