package main

import (
	"flag"
	"fmt"
	"log"

	"net/http"
	_ "net/http/pprof"
)

func main() {
	fmt.Println("gsxt bj start.....")

	cf := flag.String("f", "config.json", "config file")
	flag.Parse()

	cfg := NewConfig(*cf)
	if cfg == nil {
		fmt.Println("config file wrong!")
		return
	}

	s := NewScheduler(cfg, GSXT_BJ_EXCET_URL, TMPL_GSXT_BJ)
	go s.Start()

	log.Fatalln(http.ListenAndServe(cfg.HostPort, s))
}
