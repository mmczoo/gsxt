package main

import (
	"container/list"
	"encoding/json"
	"os"
	"path/filepath"

	"github.com/xlvector/dlog"
)

type LinkMgr struct {
	queue *list.List

	tryMax int

	linkFile *os.File
}

func NewLinkMgrWithFileName(fn string) *LinkMgr {
	lm := &LinkMgr{
		queue:  list.New(),
		tryMax: 3,
	}

	lm.linkFile = os.Stdout
	if len(fn) > 0 {
		cwd, err := os.Getwd()
		if err != nil {
			dlog.Info("linkFile: getwd fail! %s", err)
			return lm
		}
		absdir := filepath.Join(cwd, "data")
		err = os.MkdirAll(absdir, 0777)
		if err != nil {
			dlog.Info("linkFile: mkdir fail! %s", err)
			return lm
		}
		absfn := filepath.Join(absdir, fn)
		f, err := os.OpenFile(absfn, os.O_RDWR|os.O_APPEND|os.O_CREATE, 0644)
		if err != nil {
			dlog.Info("linkFile: openfile fail! %s", err)
			return lm
		}
		lm.linkFile = f
	}
	return lm
}

func NewLinkMgr() *LinkMgr {
	return NewLinkMgrWithFileName("links.rec")
}

func (p *LinkMgr) GetLink() *Link {
	e := p.queue.Front()
	if e == nil {
		return nil
	}
	p.queue.Remove(e)
	l, ok := e.Value.(*Link)
	if ok {
		return l
	}

	return nil
}

func (p *LinkMgr) AddLink(link *Link) {
	if link == nil {
		return
	}
	if link.Count >= 3 {
		dlog.Info("trymax: %+v", link)
		p.RecordLink(link)
		return
	}
	p.queue.PushBack(link)
}

func (p *LinkMgr) Len() int {
	return p.queue.Len()
}

func (p *LinkMgr) RecordLink(link *Link) {
	data, err := json.Marshal(link)
	if err != nil {
		dlog.Error("recordlink fail: %+v %s", link, err)
		return
	}
	p.linkFile.Write(data)
	p.linkFile.WriteString("\n")
}
