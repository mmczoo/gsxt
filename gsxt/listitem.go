package main

import (
	"fmt"
	"time"

	"github.com/xlvector/dlog"
)

type ListItem struct {
	RegName      string
	RegId        string
	RegNo        string
	CreditTocket string
	IssueTime    time.Time
}

func (p *ListItem) ToURL() string {
	//预测二十秒后调度
	now := time.Now().Add(20)
	msec := now.UnixNano() / int64(time.Millisecond)

	url := fmt.Sprintf("http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!openEntInfo.dhtml?entId=%s&credit_ticket=%s&entNo=%s&type=ccycDiv&timeStamp=%d",
		p.RegId, p.CreditTocket, p.RegNo, msec)

	return url
}

func (p *ListItem) GenQynbURL() string {
	now := time.Now().Add(20)
	msec := now.UnixNano() / int64(time.Millisecond)

	url := fmt.Sprintf("http://qyxy.baic.gov.cn/qynb/entinfoAction!qyxx.dhtml?entid=a1a1a1a0223ae51601223e22ac4131c3&clear=true&timeStamp=%d", msec)
	return url
}
func (p *ListItem) ToQynbList() string {
	//预测二十秒后调度
	now := time.Now().Add(20)
	msec := now.UnixNano() / int64(time.Millisecond)

	url := fmt.Sprintf("http://qyxy.baic.gov.cn/qynb/entinfoAction!qyxx.dhtml?entid=%s&clear=true&timeStamp=%d",
		p.RegId, msec)

	return url
}

func NewListItem(name, id, no, ct string, it time.Time) *ListItem {
	return &ListItem{
		RegName:      name,
		RegId:        id,
		RegNo:        no,
		CreditTocket: ct,
		IssueTime:    it,
	}
}

func (p *Model) InsertListitem(item *ListItem) {
	dlog.Info("insert item: %v", item.RegNo)
	p.listitemCache = append(p.listitemCache, item)

	if len(p.listitemCache) >= LISTITEM_CACHE_SIZE {
		p.InsertListitems()
	}
}

func (p *Model) InsertListitems() error {
	l := len(p.listitemCache)
	dlog.Info("insert items: %d", l)
	if l <= 0 {
		return nil
	}
	ret := p.db.InsertBatch(p.listitemCache[0:l], true)
	if ret != nil {
		dlog.Error("insertitem: %s", ret)
	}
	p.listitemCache = p.listitemCache[0:0]
	return ret
}
