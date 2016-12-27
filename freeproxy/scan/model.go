package main

import (
	"log"

	"github.com/seefan/gossdb"
	"github.com/xlvector/dlog"
)

var proxy_pool_name = "useful_proxy_queue"

type Model struct {
	pool   *gossdb.Connectors
	client *gossdb.Client

	conf *Config
}

func NewModel(conf *Config) *Model {
	if conf == nil {
		log.Fatal("config fail!")
		return nil
	}

	pool, err := gossdb.NewPool(&gossdb.Config{
		Host:             conf.Host,
		Port:             conf.Port,
		MinPoolSize:      5,
		MaxPoolSize:      50,
		AcquireIncrement: 5,
	})
	if err != nil {
		log.Fatal(err)
		return nil
	}

	c, err := pool.NewClient()
	if err != nil {
		log.Fatal(err)
		return nil
	}

	return &Model{
		pool:   pool,
		client: c,
		conf:   conf,
	}
}

func (p *Model) SavePx(px string) (int64, error) {
	sz, err := p.client.Qpush(proxy_pool_name, px)
	dlog.Info("savepx: %d %v %v", sz, err, px)

	return sz, err
}
