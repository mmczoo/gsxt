package main

import (
	"flag"
	"net"
	"net/http"
	"runtime"

	"github.com/xlvector/dlog"
)

func main() {
	runtime.GOMAXPROCS(4)

	port := flag.String("p", "8080", "port")
	flag.Parse()

	sr := NewDownloaderServer()
	http.Handle("/", sr)
	l, e := net.Listen("tcp", ":"+*port)
	if e != nil {
		dlog.Error("listen fail! %s", e)
		return
	}
	http.Serve(l, nil)
}
