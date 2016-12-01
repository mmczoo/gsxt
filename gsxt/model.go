package main

import (
	"time"

	"github.com/xlvector/go-orm"
)

type Model struct {
	db *orm.ORM

	baseinfoCache []interface{}
	listitemCache []interface{}
}

const BASEINFO_CACHE_SIZE = 512
const LISTITEM_CACHE_SIZE = 512

const CACHE_MONITOR_INTERVAL = 20 * time.Second

func NewModel(s string) *Model {
	m := &Model{
		db:            orm.NewORM(s),
		baseinfoCache: make([]interface{}, 0, BASEINFO_CACHE_SIZE*2),
		listitemCache: make([]interface{}, 0, LISTITEM_CACHE_SIZE*2),
	}

	go m.cacheMonitor()

	return m
}

func (p *Model) cacheMonitor() {
	tc := time.NewTicker(CACHE_MONITOR_INTERVAL)

	for {
		<-tc.C
		if len(p.baseinfoCache) > 0 {
			p.InsertBaseInfos()
		}

		if len(p.listitemCache) > 0 {
			p.InsertListitems()
		}
	}
}
