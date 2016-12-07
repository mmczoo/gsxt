package main

import (
	"bytes"
	"io/ioutil"
	"os"
	"regexp"
	"testing"
	"time"
)

func TestQueryNum(t *testing.T) {
	e := NewExtractor()

	f, err := os.Open("listpage.html")
	if err != nil {
		t.Error("open fail")
	}
	defer f.Close()

	data, err := ioutil.ReadAll(f)
	if err != nil {
		t.Error("read fail")
	}

	pn, in, err := e.QueryNum(string(data))
	t.Logf("%d %d %v", pn, in, err)

}

func TestListPage(t *testing.T) {
	e := NewExtractor()

	f, err := os.Open("listpage.html")
	if err != nil {
		t.Error("open fail")
	}
	defer f.Close()

	data, err := ioutil.ReadAll(f)
	if err != nil {
		t.Error("read fail")
	}

	/*
		data := `<tr style="background:#f6f7fb;">
		             <td style="text-align:center;"><a href="#"  onclick="openEntInfo('北京安客居房地产经纪有限公司','20e38b8c50c7cece0150d578b2802f56','110114020127903', 'AB2D31722C08BD6108C1DBA1B5EEAB76');">北京安客居房地产经纪有限公司</a></td>
										                                <td style="text-align:center;">110114020127903</td>
																		                                <td style="text-align:center;">2016年11月25日</td>
																										                        </tr>`
	*/

	li := e.QueryListPage(string(data))
	for i, v := range li {
		t.Logf("%d %+v", i, v)
	}
}

func TestToURL(t *testing.T) {
	li := NewListItem("a", "b", "c", "d", time.Now())

	t.Logf("%s\n", li.ToURL())
}

func TestDetailPage(t *testing.T) {
	//e := NewExtractor()

	f, err := os.Open("baseinfo.html")
	if err != nil {
		t.Error("open fail")
	}
	defer f.Close()

	data, err := ioutil.ReadAll(f)
	if err != nil {
		t.Error("read fail")
	}

	pos := bytes.Index(data, []byte("基本信息"))
	if pos < 0 {
		t.Error("not baseinifo")
		return
	}
	t.Log(pos)
	//rep := regexp.MustCompile(`<tr>(?:[\s\S]*)<th.*>注册号</th>(?:[\s\S]*)<td.*>(.*?)</td>(?:[\s\S]*)<th>名称</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th>类型</th>(?:[\s\S]*)<td>有限责任公司(自然人独资)</td>(?:[\s\S]*)<th.*>法定代表人</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>注册资本</th>(?:[\s\S]*)<td>([\s\S]*)</td>(?:[\s\S]*)<th.*>成立日期</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>住所</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th>营业期限自</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>营业期限至</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>经营范围</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th.*>登记机关</th>(?:[\s\S]*)<td>(.*?)</td>(?:[\s\S]*)<th>核准日期</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>登记状态</th>(?:[\s\S]*)<td>(.*)</td>`)
	rep := regexp.MustCompile(`<th.*>统一社会信用代码</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th>名称</th>(?:[\s\S]*)<td width="30%">(.*)</td>(?:[\s\S]*)<th>类型</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th.*>法定代表人</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>注册资本</th>(?:[\s\S]*)<td>([\s\S]*)</td>(?:[\s\S]*)<th.*>成立日期</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>住所</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th>营业期限自</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>营业期限至</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>经营范围</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th.*>登记机关</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>核准日期</th>(?:[\s\S]*)<td>(.*?)</td>(?:[\s\S]*)<th>登记状态</th>(?:[\s\S]*)<td>(.*?)</td>`)

	ret := rep.FindStringSubmatch(string(data[pos:]))
	t.Logf("%v", ret)

}

func TestDetailPage2(t *testing.T) {
	//e := NewExtractor()

	f, err := os.Open("baseinfo2.html")
	if err != nil {
		t.Error("open fail")
	}
	defer f.Close()

	data, err := ioutil.ReadAll(f)
	if err != nil {
		t.Error("read fail")
	}

	pos := bytes.Index(data, []byte("基本信息"))
	if pos < 0 {
		t.Error("not baseinifo")
		return
	}
	t.Log(pos)
	//rep := regexp.MustCompile(`<th.*>(?:统一社会信用代码|注册号)</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th>名称</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th>类型</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th.*>负责人</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>经营场所</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th>营业期限自</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>营业期限至</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>经营范围</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th.*>登记机关</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>核准日期</th>(?:[\s\S]*)<td>(.*?)</td>(?:[\s\S]*)<th>登记状态</th>(?:[\s\S]*)<td>(.*?)</td>`)

	//rep := regexp.MustCompile(`<th.*>(?:统一社会信用代码|注册号)</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th>名称</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th>类型</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th.*>负责人</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>经营场所</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th>营业期限自</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>营业期限至</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>经营范围</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th.*>登记机关</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>核准日期</th>(?:[\s\S]*)<td>(.*?)</td>(?:[\s\S]*)<th>登记状态</th>(?:[\s\S]*)<td>(.*?)</td>(?:[\s\S]*)<td>(.*?)</td>(?:[\s\S]*)<th>成立日期</th>(?:[\s\S]*)<td>(.*?)</td>`)
	rep := regexp.MustCompile(`<th.*>(?:统一社会信用代码|注册号)</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th>名称</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th>类型</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th.*>负责人</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>经营场所</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th>营业期限自</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>营业期限至</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>经营范围</th>(?:[\s\S]*)<td.*>(.*)</td>(?:[\s\S]*)<th.*>登记机关</th>(?:[\s\S]*)<td>(.*)</td>(?:[\s\S]*)<th>核准日期</th>(?:[\s\S]*)<td>(.*?)</td>(?:[\s\S]*)<th.*>登记状态</th>(?:[\s\S]*)<td>(.*?)</td>(?:[\s\S]*)<th.*>成立日期</th>(?:[\s\S]*)<td>(.*?)</td>`)
	ret := rep.FindStringSubmatch(string(data[pos:]))
	t.Logf("%v", ret)

}

func TestQynbList(t *testing.T) {
	data := `<h2 id="qiyeTitle" style="text-align:center;">企业公示信息由该企业提供，企业对其公示信息的真实性、合法性负责</h2>
    <div id="qiyenianbao">
		<table  cellpadding="0" cellspacing="0" class="detailsList">
		<tr><th colspan="4" style="text-align:center;">企业年报</th></tr>
        <tr width="95">
		  <th width="5" style="text-align:center;">序号</th>
          <th width="55" style="text-align:center;">报送年度</th>
          <th width="40" style="text-align:center;">发布日期</th>
        </tr>
         
         <tr>
		  	<td style="text-align:center;">1</td>
		  	
			<td style="text-align:left;"><a href='/qynb/entinfoAction!qynbxx.dhtml?cid=ca48c1a70dfc47bba954aa034b6be300&entid=20e38b8c4ed2e027014efbe954a751b8&credit_ticket=65B3BD731BE5629884C9170BF2DF9B76' target="_blank">2015年度</a></td>
			
			<td style="text-align:center;">2016-06-26&nbsp;</td>
        </tr>
			
	</table>
 </div>
</body>
</html>`
	rep := regexp.MustCompile(`企业年报(?:[\s\S]*)<td.*>(\d+)</td>(?:[\s\S]*)<a href='(.*)'.*>(.*)</a></td>(?:[\s\S]*)<td.*>(.*?)</td>`)
	ret := rep.FindStringSubmatch(string(data))
	t.Logf("%v", ret)
}

func TestQynbList2(t *testing.T) {
	data := `<h2 id="qiyeTitle" style="text-align:center;">企业公示信息由该企业提供，企业对其公示信息的真实性、合法性负责</h2>
    <div id="qiyenianbao">
		<table  cellpadding="0" cellspacing="0" class="detailsList">
		<tr><th colspan="4" style="text-align:center;">企业年报</th></tr>
        <tr width="95">
		  <th width="5" style="text-align:center;">序号</th>
          <th width="55" style="text-align:center;">报送年度</th>
          <th width="40" style="text-align:center;">发布日期</th>
        </tr>
         
         <tr>
		  	<td style="text-align:center;">1</td>
		  	
			<td style="text-align:left;"><a href='/qynb/entinfoAction!qynbxx.dhtml?cid=ca48c1a70dfc47bba954aa034b6be300&entid=20e38b8c4ed2e027014efbe954a751b8&credit_ticket=65B3BD731BE5629884C9170BF2DF9B76' target="_blank">2015年度</a></td>
			
			<td style="text-align:center;">2016-06-26&nbsp;</td>
        </tr>
			
	</table>
 </div>
</body>
</html>`

	e := NewExtractor()
	ret := e.QueryQynb(string(data))
	for _, v := range ret {
		t.Logf("%#v", v)
	}
}
