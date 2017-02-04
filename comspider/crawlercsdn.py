# -*- coding:utf8 -*-
import sys

import re
import md5
import os
import json
import time
import Queue 

import logging as mylog
mylog.basicConfig(level=mylog.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')

import gevent
from gevent import monkey; monkey.patch_socket()


from crawler import Crawler
from bfilter import Filter 
from errortry import ErrorTry

from csdnstarturl import starturls
from crawler import PAGE_TYPE_LIST



class CrawlerCsdn(Crawler):
    linkre = re.compile('href="(.*?)"')
    articleurlre = re.compile("article/details/\d+")

    def __init__(self):
        bfilter = Filter(capacity=100000000, fname="csdn_filter.bloom")
        errortry = ErrorTry(fname="csdn_err.bloom")
        super(CrawlerCsdn, self).__init__("csdn", bfilter, errortry, concurent=10)
        self.linkfd = open("csdnlinks.txt", "a+")
        self.fd404 = open("csdn404.txt", "a+")
        self.proxies = {
                "http": "http://127.0.0.1:8080"
                }
        self.cache = set()


    def initTasks(self):
        #self.addListUrl("http://blog.csdn.net")
        cnt = 0
        for url in starturls:
            if not self.bfilter.isExists(url):
                cnt += 1
                self.addListUrl(url)
        mylog.info("inittask: %d" % cnt)
        #self.addListUrl("http://blog.csdn.net/?articles")
        #self.addListUrl("http://www.csdn.net/")
        #self.addListUrl("http://blog.csdn.net/foruok/article/details/53500801")
        

    def commproc(self, data, url):
        self.linkfd.write(url + "\n")
        if self.articleurlre.search(url):
            self.saveFile(data, url)

        links = self.linkre.findall(data)
        for link in links:
            tmp = link.split("#")
            link = tmp[0]
            link = link.replace("&amp;", "&")
            if not link.startswith("http"):
                continue
            if ".css" in link or ".js" in link:
                continue
            if ".ppt" in link or ".doc" in link:
                continue
            if ".gz" in link or ".zip" in link:
                continue
            if "csdn.net" not in link:
                continue

            if link in self.cache:
                continue
            if not self.bfilter.isExists(link):
                self.addListUrl(link)
                self.cache.add(link)
            if len(self.cache) > 1000:
                self.cache.clear()

    #ret: True success  False: try get
    def procListPage(self, data, url):
        self.commproc(data, url)
        return True

    #ret: True success  False: try get
    def procDetailPage(self, data, url):
        self.commproc(data, url)
        return True



    def saveFile(self, data, url):
        st = time.strftime("%Y%m%d", time.localtime())
        pdir = os.path.join("data", "csdn", st)
        if not os.path.exists(pdir):
            os.makedirs(pdir)
        m1 = md5.new()   
        m1.update(url)   
        fn = m1.hexdigest()
        fn = os.path.join(pdir, fn)
        d = {"data": data, "url": url}
        with open(fn, "w+") as f:
            json.dump(d, f)


    def crawlList(self, url):
        hurl = url
        try:
            r = self.ss.get(hurl, verify=False, headers=self.headers, proxies=self.proxies, timeout=120)
        except Exception as e:
            mylog.error("crawl fail: %s %s" % (e, url))
            self.downloadFail(url, PAGE_TYPE_LIST)
            return
        if r.status_code == 404 or r.status_code == 444 or r.status_code==500:
            mylog.error("crawl fail: %s %s" % (r.status_code, url))
            self.bfilter.add(url)
            self.fd404.write(url + "\n")
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



    def run(self):
        self.initTasks()
        while True:
            if self.tasks.empty():
                break
            dgl = []
            for i in xrange(0, self.concurent):
                try:
                    url = self.tasks.get_nowait()
                except Queue.Empty as e:
                    break
                if not url:
                    break
                if self.bfilter.isExists(url):
                    continue
                g = gevent.spawn(self.crawlList, url)
                dgl.append(g)
            mylog.info("===how: %d %d" % (self.tasks.qsize(), len(dgl)))
            if dgl:
                gevent.joinall(dgl)
            time.sleep(0.3)


if __name__ == "__main__":
    c = CrawlerCsdn()
    c.run()
    c.bfilter.sync()
    c.errortry.sync()

