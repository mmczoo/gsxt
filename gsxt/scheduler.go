package main

import (
	"encoding/gob"
	"encoding/json"
	"errors"
	"fmt"
	"math/rand"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/mmczoo/gotools/download"
	"github.com/mmczoo/gotools/utils"
	"github.com/xlvector/dlog"
)

const START_PAGENO = 1

type Scheduler struct {
	startLink  *Link
	lmgr       *LinkMgr
	extractor  *Extractor
	downloader *download.Downloader
	model      *Model

	cfg *Config

	//assist
	pageNum int
	itemNum int

	curPage int
}

type persistData struct {
	CurPage int
}

func (p *Scheduler) Serial(file string) error {
	pd := &persistData{}

	fp, err := os.Create(file)
	if err != nil {
		return err
	}
	pd.CurPage = p.curPage
	enc := gob.NewEncoder(fp)
	err = enc.Encode(pd)
	if err != nil {
		return err
	}
	return nil
}

func (p *Scheduler) persist() {
	pfn := p.cfg.PersistFile
	if len(pfn) == 0 {
		return
	}

	t := time.NewTicker(time.Duration(p.cfg.PersistIntv) * time.Second)
	for {
		<-t.C
		err := p.Serial(pfn)
		if err != nil {
			dlog.Error("serial: fail! %s", err)
		}
	}
}

func Unserial(file string) (*persistData, error) {
	fp, err := os.Open(file)
	if err != nil {
		return nil, err
	}
	pd := new(persistData)
	dec := gob.NewDecoder(fp)
	err = dec.Decode(&pd)
	if err != nil {
		return nil, err
	}

	return pd, nil
}

func NewScheduler(cfg *Config, startUrl string, tmpl string) *Scheduler {
	s := &Scheduler{
		startLink:  NewLink(startUrl, tmpl),
		lmgr:       NewLinkMgr(),
		downloader: download.NewDownloaderWithJar(3, true),
		extractor:  NewExtractor(),
		cfg:        cfg,
		model:      NewModel(cfg.MysqlApi),
	}
	s.startLink.CustomeCode = LINK_CC_BJGXST_STARTURL

	if len(cfg.PersistFile) != 0 {

		pd, err := Unserial(cfg.PersistFile)
		if err == nil {
			s.curPage = pd.CurPage
			goto lab_ret
		}
	}
	s.curPage = START_PAGENO

lab_ret:
	return s
}

//if return nil, not have next
func (p *Scheduler) nextPageLink() *Link {
	if p.curPage > p.pageNum {
		return nil
	}

	curpage := p.curPage
	c := rand.Intn(4) + 1
	if c > curpage {
		c = 1
	}
	postdata := map[string]string{
		"querystr": "请输入企业名称或注册号",
		"pageNos":  strconv.Itoa(curpage),
		"pageNo":   strconv.Itoa(curpage - c),
		"pageSize": "10",
		"clear":    "",
	}
	link := NewLinkPost(GSXT_BJ_EXCET_URL, TMPL_GSXT_BJ, postdata)
	link.CustomeCode = LINK_CC_BJGXST_EXCEPT_LIST
	p.curPage += 1
	return link
}

func (p *Scheduler) Start() {
	//get pagenum
	p.lmgr.AddLink(p.startLink)

	go p.persist()

	headers := map[string]string{
		"Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
		"Host":            "qyxy.baic.gov.cn",
		"Accept-Encoding": "gzip, deflate",
		"Accept-Language": "zh-CN,zh;q=0.8",
		"Referer":         "http://qyxy.baic.gov.cn/dito/ditoAction!ycmlFrame.dhtml?clear=true",
		"Origin":          "http://qyxy.baic.gov.cn",
		"Content-Type":    "application/x-www-form-urlencoded",
		"User-Agent":      "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36",
	}
	for {
		link := p.lmgr.GetLink()
		if link == nil {
			l := p.nextPageLink()
			if l == nil {
				fmt.Println("end gxst bj.......")
				break
			}
			link = l
			fmt.Println(link)
		}

		time.Sleep(time.Duration(rand.Intn(5)+4) * time.Second)

		var data []byte
		var err error
		if link.Method == HTTP_METHOD_GET {
			data, err = p.downloader.Get(link.URL, headers)
		} else if link.Method == HTTP_METHOD_POST {
			data, err = p.downloader.Post(link.URL, link.PostData, headers)
		} else {
			data = []byte("")
			err = errors.New("no method")
			dlog.Error("nomethod: %+v", link)
			continue
		}

		if err != nil {
			dlog.Warn("downloaderror: %v %s", link, err)
			link.Count += 1
			p.lmgr.AddLink(link)
		}

		switch link.CustomeCode {
		case LINK_CC_BJGXST_STARTURL:
			p.procBjgxstStartURL(data, link)
		case LINK_CC_BJGXST_EXCEPT_LIST:
			p.procBjgxstExceptList(data, link)
		case LINK_CC_BJGXST_EXCEPT_DETAIL:
			p.procBjgxstBaseInfo(data, link)
		case LINK_CC_BJGXST_QYNB_LIST:
			p.procBjgxstQynbList(data, link)
		case LINK_CC_BJGXST_QYNB_DETAIL:
			p.procBjgxstQynbDetail(data, link)
		}
	}
}

func (p *Scheduler) procBjgxstStartURL(data []byte, link *Link) {
	pageNum, itemNum, err := p.extractor.QueryNum(string(data))
	if err != nil {
		dlog.Warn("extractnum: %v %s", link, err)
		link.Count += 1
		p.lmgr.AddLink(link)
		return
	}
	dlog.Info("pageNum:%d itemNum:%d", pageNum, itemNum)
	p.pageNum = pageNum
	p.itemNum = itemNum

	p.procBjgxstExceptList(data, link)
}

func (p *Scheduler) procBjgxstExceptList(data []byte, link *Link) {
	lis := p.extractor.QueryListPage(string(data))
	if len(lis) == 0 {
		dlog.Warn("extractlistpage fail: %v", link)
		link.Count += 1
		p.lmgr.AddLink(link)
		return
	}

	for _, v := range lis {
		l := NewLink(v.ToURL(), TMPL_GSXT_BJ)
		l.CustomeCode = LINK_CC_BJGXST_EXCEPT_DETAIL
		l.CustomeData = v
		p.lmgr.AddLink(l)
		p.model.InsertListitem(v)
		//dlog.Info("%d %+v\n", i, v)
	}

	for _, v := range lis {
		l := NewLink(v.ToQynbList(), TMPL_GSXT_BJ)
		l.CustomeCode = LINK_CC_BJGXST_QYNB_LIST
		l.CustomeData = v
		p.lmgr.AddLink(l)
	}

	l := p.nextPageLink()
	if l != nil {
		p.lmgr.AddLink(l)
	}
}

func (p *Scheduler) procBjgxstBaseInfo(data []byte, link *Link) {
	binfo := p.extractor.QueryBaseInfo(string(data))
	//fmt.Printf("%+v\n", binfo)
	if binfo == nil {
		dlog.Warn("querybaseinfo: fail")
		p.saveBaseInfoFail(data, link)
		return
	}

	p.model.InsertBaseInfo(binfo)
}

func (p *Scheduler) procBjgxstQynbList(data []byte, link *Link) {
	qynbs := p.extractor.QueryQynb(string(data))
	if qynbs == nil {
		dlog.Warn("querybaseinfo: fail")
		return
	}
	for _, v := range qynbs {

		l := NewLink(v.ToQynDetailUrl(), TMPL_GSXT_BJ)
		l.CustomeCode = LINK_CC_BJGXST_QYNB_DETAIL
		v.Bridge = link.CustomeData
		l.CustomeData = v

		p.lmgr.AddLink(l)
	}

}

func (p *Scheduler) procBjgxstQynbDetail(data []byte, link *Link) {
}

func (p *Scheduler) saveBaseInfoFail(data []byte, link *Link) {
	now := time.Now()

	dirs := make([]string, 0, GSXT_DIR_LEVEL_NUM)
	dirs = append(dirs, GSXT_DIR_ONE)
	dirs = append(dirs, GSXT_DIR_SEC)
	dirs = append(dirs, GSXT_DIR_CJ)
	dirs = append(dirs, now.Format("20060102"))

	category := "pn"
	idt := strconv.Itoa(p.curPage)
	switch link.CustomeCode {
	case LINK_CC_BJGXST_STARTURL:
	case LINK_CC_BJGXST_EXCEPT_LIST:
	case LINK_CC_BJGXST_EXCEPT_DETAIL:
		category = "bi"
		idt = link.CustomeData.(*ListItem).RegNo
	}

	fn := fmt.Sprintf("%s_%s_%d.html", category, idt, link.Count)
	rfn, err := utils.GenFilePath(fn, dirs...)
	if err != nil {
		dlog.Info("genfile: fail! %v %v %v", fn, dirs, err)
		return
	}

	ld, err := json.Marshal(link)
	if err != nil {
		dlog.Info("bsavejson: fail! %v %v %v", fn, dirs, err)
		return
	}

	err = utils.SaveFile(rfn, data, []byte(HTML_COMMENT_BEGIN), ld, []byte(HTML_COMMENT_END))
	if err != nil {
		dlog.Info("savefile: fail! %v %v %v", fn, dirs, err)
		return
	}
}

func (p *Scheduler) ServeHTTP(resp http.ResponseWriter, req *http.Request) {
	return
}
