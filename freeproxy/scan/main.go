package main

import (
	"net/http"
)

func main() {
	go func() {
		h := &ScanHTTPServer{}
		http.ListenAndServe(":8080", h)

	}()

	hs := &ScanHTTPSServer{}
	http.ListenAndServeTLS(":8043", "server.crt",
		"server.key", hs)

}
