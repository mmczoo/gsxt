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

from bs4 import BeautifulSoup


from crawler import Crawler
from bfilter import Filter 
from errortry import ErrorTry

from crawler import PAGE_TYPE_LIST
from crawler import PAGE_TYPE_DETAIL



class CrawlerHome(Crawler):
    def __init__(self):
        bfilter = Filter(capacity=100000000, fname="home_filter.bloom")
        errortry = ErrorTry(fname="home_err.bloom")
        super(CrawlerHome, self).__init__("home", bfilter, errortry, concurent=1)
        self.cache = set()

        self.tre = re.compile(">(.*?)<br>(.*?)<")


    def initTasks(self):
        self.addListUrl("http://www.homes.co.jp/kodate/chuko/osaka/list/")
        for i in xrange(2, 285):
            url = "http://www.homes.co.jp/kodate/chuko/osaka/list/?page=%d" % i
            self.addListUrl(url)

        
    #ret: True success  False: try get
    def procListPage(self, data, url):
        print url
        #print data
        soup = BeautifulSoup(data, 'html.parser')
        divs = soup.select("#kksframelist .mod-listKks")
        rd = []
        print "first=== ", len(divs)
        for div in divs:
            #print "=======", div, "\n"
            res = {} 
            try:
                mh = div.select(".moduleHead a span")
                res["postion"] = mh[0].get_text()
                mtr = div.select(".moduleBody .sec-specB table tr")
                tr = mtr[1]
                res["price"] = tr.select(".price")[0].get_text()
                res["addr"] = tr.select(".address")[0].get_text()
                res["traffic"] = tr.select(".traffic")[0].get_text()
                tmp = tr.select(".space")[0].get_text().replace("\n", "").replace("\r","")
                tmp = re.split(' +', tmp)
                try:
                    res["space"] = tmp[0]
                    res["layout"] = tmp[1]
                except:
                    pass
            except Exception as e:
                print e
            rd.append(res)

        divs = soup.select("#prg-mod-bukkenList .prg-bundle .mod-mergeBuilding--sale")
        print "second==== ", len(divs)
        for div in divs:
            #print "=======", div, "\n"
            res = {} 
            try:
                mh = div.select(".moduleHead a span")
                res["postion"] = mh[0].get_text()
                mtr = div.select(".moduleBody .sec-spec .sec-specB table tr td")
                tr = mtr[0]
                tmp = self.tre.search(str(tr))
                if tmp:
                    res["traffic"] = tmp.group(1)
                    res["addr"] = tmp.group(2) 


                tr = div.select(".moduleBody .unitSummary")[0]
                res["price"] = tr.select(".priceLabel")[0].get_text()
                res["layout"] = tr.select(".layout")[1].get_text()
                space1 = tr.select("td[class=\"space\"]")[0].get_text()
                space2 = tr.select("td[class=\"space\"]")[1].get_text()
                res["space"] = [space1, space2]

                tr = mtr[1]
                res["build_year"] = tr.get_text()
                tr = mtr[2]
                res["state"] = tr.get_text()
                tr = mtr[3]
                res["light"] = tr.get_text()

                '''
                for k, v in res.items():
                    print k, v
                break
                '''
            except Exception as e:
                print e

            rd.append(res)

        if res:
            self.saveFile(rd, url)
        return True


    #ret: True success  False: try get
    def procDetailPage(self, data, url):
        return True

    def saveFile(self, data, url):
        st = time.strftime("%Y%m%d", time.localtime())
        pdir = os.path.join("data", "home", st)
        if not os.path.exists(pdir):
            os.makedirs(pdir)
        m1 = md5.new()   
        m1.update(url)   
        fn = m1.hexdigest()
        fn = os.path.join(pdir, fn)
        d = {"data": data, "url": url}
        with open(fn, "w+") as f:
            json.dump(d, f)

if __name__ == "__main__":
    c = CrawlerHome()
    c.run()
    c.bfilter.sync()
    c.errortry.sync()

