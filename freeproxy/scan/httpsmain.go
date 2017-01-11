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

	hs := NewScanHTTPSServer(m)

	log.Fatal(http.ListenAndServeTLS(cfg.HttpBind, "server.crt",
		"server.key", hs))

}
