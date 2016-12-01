package main

import "testing"

func TestLinkMgr(t *testing.T) {
	lm := NewLinkMgr()

	a := NewLink("baidu.com", "baidu")
	b := NewLinkPost("goole.com", "goole", nil)

	lm.AddLink(a)
	lm.AddLink(b)

	t.Logf("lm: %d\n", lm.Len())

	t.Logf("link:%v", lm.GetLink())
	t.Logf("link:%v", lm.GetLink())

	t.Logf("lm: %d\n", lm.Len())

}
