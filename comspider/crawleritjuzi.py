# -*- coding:utf8 -*-

import re
import md5
import os
import json

from crawler import Crawler




class CrawlerItjuzi(Crawler):
    nextpagere = re.compile('<a*?href=\'(.*?)\' title=\'下一页\'>') 
    listre = re.compile('<article.*?<h2.*?><a.*?href="(.*?)".*?</a></h2>', re.S)

    def __init__(self):
        super(CrawlerItjuzi, self).__init__("itjuzi")

    def initTasks(self):
        self.addListUrl("http://blog.itjuzi.com/category/%E6%AF%8F%E6%97%A5%E9%A3%8E%E9%99%A9%E6%8A%95%E8%B5%84%E9%80%9F%E9%80%92/")
        #self.addListUrl("http://blog.itjuzi.com/category/%E6%AF%8F%E6%97%A5%E9%A3%8E%E9%99%A9%E6%8A%95%E8%B5%84%E9%80%9F%E9%80%92/page/127/")


    #ret: True success  False: try get
    def procListPage(self, data, url):
        #print type(data)
        tmp = self.nextpagere.search(data)
        nexturl = ""
        if tmp:
            nexturl = tmp.group(1)
            self.addListUrl(nexturl)
        tmp = self.listre.findall(data)
        print nexturl, len(tmp)
        if tmp:
            for link in tmp:
                print link
                self.addDetailUrl(link)
        return True

    #ret: True success  False: try get
    def procDetailPage(self, data, url):
        if len(data) < 500:
            print "short!!", url

        d = {"data": data, "url": url}
        m1 = md5.new()   
        m1.update(url)   
        fn = m1.hexdigest()
        pdir = os.path.join("data", "itjuzi")
        if not os.path.exists(pdir):
            os.makedirs(pdir)
        fn = os.path.join(pdir, fn)
        with open(fn, "w+") as f:
            json.dump(d, f)
            return True

        


if __name__ == "__main__":
    c = CrawlerItjuzi()
    c.run()

