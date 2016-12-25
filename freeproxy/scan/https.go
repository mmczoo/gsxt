package main

import (
	"fmt"
	"net/http"
)

type ScanHTTPSServer struct {
}

func (p *ScanHTTPSServer) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w,
		"Hi, This is an example of https service in golang!")
}
