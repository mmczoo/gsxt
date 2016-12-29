package main

import (
	"encoding/json"
	//	"fmt"
	"net/http"
)

type Statistic struct {
	model *Model

	AddrsReq int64
	BReq     int64
	CReq     int64

	ScanNum int64
}

func NewStatistic(m *Model) *Statistic {
	return &Statistic{
		model: m,
	}
}

func (p *Statistic) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	data, _ := json.Marshal(map[string]int64{
		"addrs": p.AddrsReq,
		"b":     p.BReq,
		"c":     p.CReq,
		"scan":  p.ScanNum,
	})
	w.Write(data)
}
