# -*- coding:utf8 -*-

import Queue 
import time
import logging as mylog
mylog.basicConfig(level=mylog.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')


import requests
import gevent
from gevent import monkey; monkey.patch_socket()

import sys
sys.path.insert(0, ".")
from bfilter import Filter 
from errortry import ErrorTry


PAGE_TYPE_LIST = 1
PAGE_TYPE_DETAIL = 2


class Crawler(object):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding":"gzip, deflate, sdch, br",
        "Accept-Language":"zh-CN,zh;q=0.8",
        "Cache-Control":"no-cache",
        "Connection":"keep-alive",
        #"Host":"www.baidu.com",
        "Pragma":"no-cache",
        "Upgrade-Insecure-Requests":"1",
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
            }

    def __init__(self, name, fbloom=None, errtry=None,concurent=5):
        self.concurent = concurent
        self.tasks = Queue.Queue(maxsize=1000000)
        self.details = Queue.Queue(maxsize=10) 
        self.tmpl = name
        self.ss = requests.session()
        self.proxies = {}

        day = time.strftime("%Y%m%d", time.localtime())
        if not fbloom:
            fn = day + "_filter.bloom"
            self.bfilter = Filter(fname=fn)
        else:
            self.bfilter = fbloom

        if not errtry:
            fn = day + "_errtry.bloom"
            self.errortry = ErrorTry(fname=fn)
        else:
            self.errortry = errtry


    def downloadFail(self, url, pagetype):
        if self.errortry.isTry(url):
            if pagetype == PAGE_TYPE_LIST:
                self.addListUrl(url)
            elif pagetype == PAGE_TYPE_DETAIL:
                self.addDetailUrl(url)

    #need code for real crawler
    def initTasks(self):
        pass

    #need code for real crawler
    #ret: True success  False: try get
    def procListPage(self, data, url):
        pass

    #need code for real crawler
    #ret: True success  False: try get
    def procDetailPage(self, data, url):
        pass

    def addListUrl(self, url):
        if not url:
            return 
        self.tasks.put(url)

    def addDetailUrl(self, url):
        if not url:
            return 
        self.details.put(url)


    def crawlList(self, url):
        hurl = url
        try:
            r = self.ss.get(hurl, verify=False, headers=self.headers, proxies=self.proxies)
        except Exception as e:
            mylog.error("crawl fail: %s %s" % (e, url))
            self.downloadFail(url, PAGE_TYPE_LIST)
            return
        if r.status_code != 200:
            mylog.error("crawl fail: %s %s" % (r.status_code, url))
            self.downloadFail(url, PAGE_TYPE_LIST)
            return
        if not self.procListPage(r.content, url):
            mylog.error("proc fail: %s", url)
            self.downloadFail(url, PAGE_TYPE_LIST)
        else:
            self.bfilter.add(url)


    def crawlDetail(self, url):
        hurl = url 
        try:
            r = self.ss.get(hurl, verify=False, headers=self.headers, proxies=self.proxies)
        except Exception as e:
            mylog.error("detail crawl fail: %s %s" % (e, url))
            self.downloadFail(url, PAGE_TYPE_DETAIL)
            return
        if r.status_code != 200:
            mylog.error("detail crawl fail: %s %s" % (r.status_code, url))
            self.downloadFail(url, PAGE_TYPE_DETAIL)
            return
        if not self.procDetailPage(r.content, url):
            mylog.error("detail proc fail: %s" %  url)
            self.downloadFail(url, PAGE_TYPE_DETAIL)
        else:
            self.bfilter.add(url)

    def run(self):
        self.initTasks()
        while True:
            if self.tasks.empty():
                break
            gl = []
            for i in xrange(0, self.concurent):
                try:
                    url = self.tasks.get_nowait()
                except Queue.Empty:
                    break
                if not url:
                    break
                if self.bfilter.isExists(url):
                    continue
                g = gevent.spawn(self.crawlList, url)
                gl.append(g)
            if gl:
                gevent.joinall(gl)
            time.sleep(0.3)

            while True:
                if self.details.empty():
                    break 
                dgl = []
                for i in xrange(0, self.concurent):
                    try:
                        url = self.details.get_nowait()
                    except Queue.Empty:
                        break
                    if not url:
                        break
                    if self.bfilter.isExists(url):
                        continue
                    g = gevent.spawn(self.crawlDetail, url)
                    dgl.append(g)
                if dgl:
                    gevent.joinall(dgl)
                time.sleep(0.3)

