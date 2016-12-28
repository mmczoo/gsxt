package main

import (
	"fmt"
	"runtime/debug"
	"strings"
	"time"

	"github.com/xlvector/dlog"
)

type RClient struct {
	st  *Statistic
	cfg *Config

	pxch chan string
}

func NewRClient(st *Statistic, cfg *Config) *RClient {
	return &RClient{
		st:   st,
		cfg:  cfg,
		pxch: make(chan string, 4096),
	}
}

const (
	IP_CLASS_B = 2
	IP_CLASS_C = 3
)

//notice: check ptype ipr
func (p *RClient) GenIPS(ptype, ipr string, ports []string, ipclass int) {
	dots := strings.Split(ipr, ".")
	switch ipclass {
	case IP_CLASS_C:
		if len(dots) < 3 {
			return
		}
		for _, port := range ports {
			for i := 255; i > 0; i-- {
				tmp := fmt.Sprintf("%s://%s.%s.%s.%d:%s", ptype, dots[0], dots[1], dots[2], i, port)
				p.pxch <- tmp
			}
		}
	case IP_CLASS_B:
		if len(dots) < 2 {
			return
		}
		for _, port := range ports {
			for i := 255; i > 0; i-- {
				for j := 255; j > 0; j-- {
					tmp := fmt.Sprintf("%s://%s.%s.%d.%d:%s", ptype, dots[0], dots[1], i, j, port)
					p.pxch <- tmp
				}
			}
		}
	default:
		return
	}
}

func (p *RClient) scan(i int) {
	for {
		px := <-p.pxch
		fmt.Println(px)
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

	t := time.NewTicker(time.Duration(p.cfg.AddrsIntv) * time.Second)
	for {
		<-t.C
		if len(p.cfg.Addrs) >= 0 {
			for _, ptype := range p.cfg.AddrsProtocl {
				for _, addr := range p.cfg.Addrs {
					p.pxch <- ptype + "://" + addr
				}
			}
		}
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

}

func (p *RClient) runC() {
	defer func() {
		if r := recover(); r != nil {
			dlog.Println("ERROR: ", r)
			debug.PrintStack()
			go p.Run()
		}
	}()
}

func (p *RClient) Run() {
	conc := p.cfg.AddrsQPS + p.cfg.BQPS + p.cfg.CQPS
	if conc < 100 {
		conc = 100
	}

	for i := 0; i < conc; i++ {
		go p.scan(i)
	}

}
