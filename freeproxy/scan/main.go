package main

import (
	"flag"
	"log"
	"net/http"
)

func main() {
	fn := flag.String("f", "config.json", "config file")
	flag.Parse()

	cfg := NewConfig(*fn)
	m := NewModel(cfg)

	h := NewScanHTTPServer(m)

	log.Fatal(http.ListenAndServe(cfg.HttpBind, h))
	/*
		}()
		go func() {
			h := NewScanHTTPServer(m)
			http.ListenAndServe(":8080", h)
		}()

		hs := NewScanHTTPSServer(m)
		http.ListenAndServeTLS(":8043", "server.crt",
			"server.key", hs)
	*/

}
