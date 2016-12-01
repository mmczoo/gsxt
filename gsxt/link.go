package main

type Link struct {
	URL      string            `json:"url"`
	Tmpl     string            `json:"tmpl"`
	Method   string            `json:"method"`
	PostData map[string]string `json:"postdata"`

	//用户自己操作数据
	CustomeCode int         `json:"customecode"`
	CustomeData interface{} `json:"customecontent"`
	//尝试下载次数
	Count int `json:"count"`
}

const (
	HTTP_METHOD_GET  = "GET"
	HTTP_METHOD_POST = "POST"
)

func NewLink(url string, tmpl string) *Link {
	return &Link{
		URL:    url,
		Tmpl:   tmpl,
		Method: HTTP_METHOD_GET,
		Count:  0,
	}
}

func NewLinkPost(url string, tmpl string, pd map[string]string) *Link {
	return &Link{
		URL:      url,
		Tmpl:     tmpl,
		Method:   HTTP_METHOD_POST,
		PostData: pd,
		Count:    0,
	}
}
