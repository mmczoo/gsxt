package main

import "net/http"

type DownloadServer struct {
}

func NewDownloaderServer() *DownloadServer {
	return &DownloadServer{}
}

func (p *DownloadServer) ServeHTTP(w http.ResponseWriter, req *http.Request) {
}
