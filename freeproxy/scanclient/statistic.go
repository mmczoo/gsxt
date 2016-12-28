package main

import "net/http"

type Statistic struct {
	model *Model
}

func NewStatistic(m *Model) *Statistic {
	return &Statistic{
		model: m,
	}
}

func (p *Statistic) ServeHTTP(w http.ResponseWriter, r *http.Request) {
}
