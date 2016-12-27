package main

import (
	"fmt"
	"net/http"
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

func (p *ScanHTTPSServer) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w,
		"Hi, This is an example of https service in golang!")
}
