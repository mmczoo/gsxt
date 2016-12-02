package main

import (
	"strconv"
	"testing"
)

func TestDownload(t *testing.T) {
	headers := map[string]string{
		"Host":                      "qyxy.baic.gov.cn",
		"Connection":                "keep-alive",
		"Cache-Control":             "max-age=0",
		"Accept":                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
		"Origin":                    "http://qyxy.baic.gov.cn",
		"Upgrade-Insecure-Requests": "1",
		"User-Agent":                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36",
		"Content-Type":              "application/x-www-form-urlencoded",
		"Referer":                   "http://qyxy.baic.gov.cn/dito/ditoAction!ycmlFrame.dhtml?clear=true",
		"Accept-Encoding":           "gzip, deflate",
		"Accept-Language":           "zh-CN,zh;q=0.8",
		//"Cookie":                    "JSESSIONID=sMktYQnRXpLgQ2Q6b2hzJtZTxrD9ZPHZZM6R2QGgqS90JQxm6bCz!-331494942; CNZZDATA1257386840=399229577-1478569797-http://gsxt.saic.gov.cn/|1480649206",
	}

	curpage := 2
	postdata := map[string]string{
		"querystr": "请输入企业名称或注册号",
		"pageNos":  strconv.Itoa(curpage),
		"pageNo":   strconv.Itoa(curpage),
		"pageSize": "10",
		"clear":    "",
	}

	cfg := NewConfig("config.json")
	p := NewScheduler(cfg, GSXT_BJ_EXCET_URL, TMPL_GSXT_BJ)

	link := NewLinkPost(GSXT_BJ_EXCET_URL, TMPL_GSXT_BJ, postdata)

	data, err := p.downloader.Post(link.URL, postdata, headers)

	t.Log(err)
	t.Log(string(data))
}
