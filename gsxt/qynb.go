package main

import (
	"time"
)

type QynbList struct {
	No        string
	Uri       string
	Yname     string
	IssueTime time.Time

	//bridge info
	Bridge interface{}
}

func NewQybList(no, uri, yname string, issueTime time.Time) *QynbList {
	return &QynbList{
		No:        no,
		Uri:       uri,
		Yname:     yname,
		IssueTime: issueTime,
	}
}

func (p *QynbList) ToQynDetailUrl() string {
	if len(p.Uri) <= 0 {
		return ""
	}
	return "http://qyxy.baic.gov.cn" + p.Uri
}
