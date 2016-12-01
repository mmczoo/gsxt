package main

import (
	"errors"
	"regexp"
	"strconv"
	"time"

	"github.com/xlvector/dlog"
)

type Extractor struct {
	reQueryNum  *regexp.Regexp
	reQueryItem *regexp.Regexp
	reBaseInfo  *regexp.Regexp
	reBaseInfo2 *regexp.Regexp
}

func NewExtractor() *Extractor {
	return &Extractor{
		reQueryNum:  regexp.MustCompile(`共(\d+)页.*?记录总数(\d+)条`),
		reQueryItem: regexp.MustCompile(`openEntInfo\('(.*)','(.*)','(.*)', '(.*)'\)(?:[\s\S]*?)<td(?:[\s\S]*?)<td.*>(.*)</td>`),
		reBaseInfo:  regexp.MustCompile(`<th.*>(?:统一社会信用代码|注册号)</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th>名称</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th>类型</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th.*>法定代表人</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>注册资本</th>(?:[\s\S]*)<td>([\s\S]*)</td>(?:[\s\S]*)<th.*>成立日期</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>住所</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th>营业期限自</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>营业期限至</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>经营范围</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th.*>登记机关</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>核准日期</th>(?:[\s\S]*)<td>(.*?)</td>(?:[\s\S]*)<th>登记状态</th>(?:[\s\S]*)<td>(.*?)</td>`),
		reBaseInfo2: regexp.MustCompile(`<th.*>(?:统一社会信用代码|注册号)</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th>名称</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th>类型</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th.*>负责人</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>经营场所</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th>营业期限自</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>营业期限至</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>经营范围</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th.*>登记机关</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>核准日期</th>(?:[\s\S]*)<td>(.*?)</td>(?:[\s\S]*)<th.*>登记状态</th>(?:[\s\S]*)<td>(.*?)</td>(?:[\s\S]*)<th.*>成立日期</th>(?:[\s\S]*)<td>(.*?)</td>`),
	}
}

func (p *Extractor) QueryNum(page string) (int, int, error) {
	if len(page) <= 10 {
		return 0, 0, errors.New("parameter short!")
	}
	ret := p.reQueryNum.FindStringSubmatch(page)
	if len(ret) == 3 {
		pagenum, err := strconv.Atoi(ret[1])
		if err != nil {
			return 0, 0, err
		}
		itemnum, err := strconv.Atoi(ret[2])
		if err != nil {
			return 0, 0, err
		}

		return pagenum, itemnum, nil
	}
	return 0, 0, errors.New("no match!")
}

func (p *Extractor) QueryListPage(page string) []*ListItem {
	if len(page) <= 10 {
		return nil
	}
	ret := p.reQueryItem.FindAllStringSubmatch(page, -1)
	if ret == nil {
		return nil
	}
	dlog.Info("match: %d", len(ret))

	li := make([]*ListItem, 0, len(ret))
	for _, item := range ret {

		it, err := time.Parse("2006年01月02日", item[5])
		if err != nil {
			dlog.Warn("parse issue time fail! %+v", item)
			continue
		}

		li = append(li, NewListItem(item[1], item[2], item[3], item[4], it))
	}

	return li
}

func (p *Extractor) QueryBaseInfo(page string) *BaseInfo {
	if len(page) <= 10 {
		return nil
	}
	ret := p.reBaseInfo.FindStringSubmatch(page)
	if len(ret) > 1 {
		return NewBaseInfo(ret[1], ret[2], ret[3], ret[4],
			ret[5], ret[6], ret[7], ret[8],
			ret[9], ret[10], ret[11], ret[12], ret[13])
	}

	ret = p.reBaseInfo2.FindStringSubmatch(page)
	if len(ret) > 1 {
		return NewBaseInfo(ret[1], ret[2], ret[3], ret[4],
			"", ret[12], ret[5], ret[6], ret[7], ret[8],
			ret[9], ret[10], ret[11])
	}

	return nil

}

//key info in page or not
func (p *Extractor) CheckPage(page []byte, link *Link) bool {
	return true
}
