# -*- coding:utf8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
import re
import time
import json
import shutil
import md5
import random
import logging as mylog
#mylog.basicConfig(level=mylog.DEBUG,
mylog.basicConfig(level=mylog.INFO,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
import cPickle as pickle
from urlparse import urlparse
import random

import requests
from bs4 import BeautifulSoup
#import MySQLdb

class SogouWeixin(object):
    htmlheaders = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            "Cookie":"sig=sig=h01aa3cb2aef4892e9cf3846c91c2f48d7f7f4c9080da63f5b904a3699a5eb31641fa44f33124fab222",
            'Upgrade-Insecure-Requests': '1',
            'Connection': "keep-alive",
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:49.0) Gecko/20100101 Firefox/49.0'
            }
    weiheahers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            "Host": "mp.weixin.qq.com",
            'Upgrade-Insecure-Requests': '1',
            'Connection': "keep-alive",
            "Cookie":"sig=sig=h01aa3cb2aef4892e9cf3846c91c2f48d7f7f4c9080da63f5b904a3699a5eb31641fa44f33124fab222",
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:49.0) Gecko/20100101 Firefox/49.0'
            }

    turl = u"http://weixin.sogou.com/weixin?type=1&query=%s&ie=utf8&_sug_=n&_sug_type_="

    def __init__(self):
        s = requests.session()
        s.headers.update(self.htmlheaders)
        self.ss = s
        self.pubarturl = []
        #self.pubnumre = re.compile('<a.*?href="(http://mp.weixin.qq.com/profile?src=3.*?)">')
        self.pubnumre = re.compile('<a.*?href="(http://mp\.weixin\.qq\.com/profile\?src=3.*?)">')
        self.articlere = re.compile('"content_url":"(/s\?.*?)"')
        self.basearticleurl = "http://mp.weixin.qq.com"
        self.lasturl = ""

    def crawlArticle(self, url):
        self.weiheahers["Referer"] = self.lasturl
        r = self.ss.get(url)
        #print r.content
        self.parseArticle(r.content, url)

    def _genFileName(self):
        t = time.localtime()
        strt = '%d-%d-%d-%d' % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour)
        dr =os.path.join('data', strt)
        if not os.path.exists(dr):
            os.makedirs(dr)
        nm = 'article_%d.html' % (t.tm_min)
        fn = os.path.join(dr, nm)
        return fn

    def parseArticle(self, data, url):
        fn = self._genFileName()
        with open(fn, "w+") as f:
            f.write(data)
            f.write("\n<!--" + url + "-->")

    def crawlPubnum(self, url):
        print url
        self.weiheahers["Referer"] = self.lasturl
        self.ss.headers.update(self.weiheahers)
        r = self.ss.get(url)
        self.lasturl =url
        #print r.content
        ret = self.articlere.findall(r.content)
        print "article", len(ret)
        for uri in ret:
            uri = uri.replace("amp;", "")
            url = self.basearticleurl + uri
            self.pubarturl.append(url)
        for url in self.pubarturl:
            ts = random.randint(2, 9)
            time.sleep(ts)
            self.crawlArticle(url)

    def crawl(self, pubname):
        url = self.turl % pubname
        try:
            r = self.ss.get(url)
        except Exception as e:
            mylog.error('fail== %s %s' % (url, e))
            return
        if r.status_code != 200:
            mylog.info('fail== %s' % url)
            return
        ret = self.pubnumre.search(r.content, re.S)
        if ret:
            pubnumurl = ret.group(1)
            pubnumurl = pubnumurl.replace("amp;", "")
            self.lasturl = url
            time.sleep(random.randint(1, 13))
            self.crawlPubnum(pubnumurl)

    def run(self):
        pubnames = [u"有书", u"第一财经资讯", u"幻方秋叶PPT", u"最爱大北京", u"金融投资家俱乐部", u"CTA基金网", u"哈佛家训", u"精致佳人", u"和孩子一起玩音乐", u"市县领导参阅", u"好音乐111", u"大数据文摘", u"CSDN", u"深夜读物", u"并发编程网"]
        pubnames = [ u"我们的精彩人生", u"中国资本联盟"]
        for pn in pubnames:
            self.crawl(pn)
            time.sleep(random.randint(240,600))

if __name__ == '__main__':
    d = SogouWeixin()
    d.run()



