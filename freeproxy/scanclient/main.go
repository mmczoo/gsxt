package main

import (
	"flag"
	"net/http"
	"strconv"

	"github.com/xlvector/dlog"
)

func main() {
	fn := flag.String("f", "config.json", "config file")
	flag.Parse()

	cfg := NewConfig(*fn)
	m := NewModel(cfg)

	h := NewStatistic(m)

	rc := NewRClient(h, cfg)
	go rc.Run()

	for i := 9000; i < 9010; i++ {
		err := http.ListenAndServe(":"+strconv.Itoa(i), h)
		dlog.Info("list: %v", err)
		if err == nil {
			break
		}
	}

}
