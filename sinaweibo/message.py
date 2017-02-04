# -*- coding:utf8 -*-

import time 
import requests 
import re
import json
import os
import random

from bs4 import BeautifulSoup

headers = {
        #"Host": "s.weibo.com",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:49.0) Gecko/20100101 Firefox/49.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        #"Referer": "http://weibo.com/login.php?category=99991",
        "Cookie": "YF-Ugrow-G0=56862bac2f6bf97368b95873bc687eef; login_sid_t=4fcf29396044a5132d9ebd16c1cce1d4; YF-V5-G0=c6a30e994399473c262710a904cc33c5; WBStorage=5d1a8eee17d84880|undefined; _s_tentry=-; Apache=7393341328008.716.1484140287410; SINAGLOBAL=7393341328008.716.1484140287410; ULV=1484140287587:1:1:1:7393341328008.716.1484140287410:; YF-Page-G0=046bedba5b296357210631460a5bf1d2; SUB=_2AkMvKqAMf8NhqwJRmPgQy23nbYV3zwvEieKZdlHXJRMxHRl-yT9kqhAstRAny8W_gZnqES3AI69S7B853IzQJA..; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9W5U5ivEYTGvpaGSUg-Uhsmq",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
}

ss = requests.session()
ss.headers.update(headers)


class Message(object):
    def __init__(self):
        pass

    def genfile(key, suffix="html", prefix="info"):
        t = time.localtime()
        strt = '%04d%02d%02d%02d' % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour)
        dr = os.path.join('data', strt)
        if not os.path.exists(dr):
            os.makedirs(dr)
        fn = "%s_%s.%s" % (prefix, key, suffix)
        return os.path.join(dr, fn)

    def laugh(self, page):
        if page == 0 or page == 1:
            url = "http://weibo.com/a/aj/transform/loadingmoreunlogin?ajwvr=6&category=10011&getrecommand=1&no_timetip=false&__rnd=%s" % (int(round(time.time()*1000))) 
        else:
            url = "http://weibo.com/a/aj/transform/loadingmoreunlogin?ajwvr=6&category=10011&page=%s&lefnav=0&__rnd=%s" % (page, int(round(time.time()*1000)))
        r = ss.get(url)
        return r.content


    def military(self, page):
        if page == 0 or page == 1:
            url = "http://weibo.com/a/aj/transform/loadingmoreunlogin?ajwvr=6&category=4&getrecommand=1&no_timetip=false&__rnd=%s" % (int(round(time.time()*1000))) 
        else:
            url = "http://weibo.com/a/aj/transform/loadingmoreunlogin?ajwvr=6&category=4&page=%s&lefnav=0&__rnd=%s" % (page, int(round(time.time()*1000)))
        r = ss.get(url)
        return r.content

    def emotion(self, page):
        if page == 0 or page == 1:
            url = "http://weibo.com/a/aj/transform/loadingmoreunlogin?ajwvr=6&category=10010&getrecommand=1&no_timetip=false&__rnd=%s" % (int(round(time.time()*1000))) 
        else:
            url = "http://weibo.com/a/aj/transform/loadingmoreunlogin?ajwvr=6&category=10010&page=%s&lefnav=0&__rnd=%s" % (page, int(round(time.time()*1000)))
        r = ss.get(url)
        return r.content

    def fashion(self, page):
        if page == 0 or page == 1:
            url = "http://weibo.com/a/aj/transform/loadingmoreunlogin?ajwvr=6&category=12&getrecommand=1&no_timetip=false&__rnd=%s" % (int(round(time.time()*1000))) 
        else:
            url = "http://weibo.com/a/aj/transform/loadingmoreunlogin?ajwvr=6&category=12&page=%s&lefnav=0&__rnd=%s" % (page, int(round(time.time()*1000)))
        r = ss.get(url)
        return r.content

    def social(self, page):
        if page == 0 or page == 1:
            url = "http://weibo.com/a/aj/transform/loadingmoreunlogin?ajwvr=6&category=7&getrecommand=1&no_timetip=false&__rnd=%s" % (int(round(time.time()*1000))) 
        else:
            url = "http://weibo.com/a/aj/transform/loadingmoreunlogin?ajwvr=6&category=7&page=%s&lefnav=0&__rnd=%s" % (page, int(round(time.time()*1000)))
        r = ss.get(url)
        return r.content


    def mingxing(self, page):
        if page == 0 or page == 1:
            url = "http://weibo.com/a/aj/transform/loadingmoreunlogin?ajwvr=6&category=2&getrecommand=1&no_timetip=false&__rnd=%s" % (int(round(time.time()*1000))) 
        else:
            url = "http://weibo.com/a/aj/transform/loadingmoreunlogin?ajwvr=6&category=2&page=%s&lefnav=0&__rnd=%s" % (page, int(round(time.time()*1000)))
        r = ss.get(url)
        return r.content


    def hot(self, page):
        if page == 0 or page == 1:
            url = "http://weibo.com/a/aj/transform/loadingmoreunlogin?ajwvr=6&category=0&getrecommand=1&no_timetip=false&__rnd=%s" % (int(round(time.time()*1000))) 
        else:
            url = "http://weibo.com/a/aj/transform/loadingmoreunlogin?ajwvr=6&category=0&page=%s&lefnav=0&__rnd=%s" % (page, int(round(time.time()*1000)))
        r = ss.get(url)
        return r.content


    def toutiao(self, page):
        if page == 0 or page == 1:
            url = "http://weibo.com/a/aj/transform/loadingmoreunlogin?ajwvr=6&category=1760&getrecommand=1&no_timetip=false&__rnd=%s" % (int(round(time.time()*1000))) 
        else:
            url = "http://weibo.com/a/aj/transform/loadingmoreunlogin?ajwvr=6&category=1760&page=%s&lefnav=0&__rnd=%s" % (page, int(round(time.time()*1000)))
        r = ss.get(url)
        return r.content

    def bangdan(self):
        if page == 0 or page == 1:
            url = "http://weibo.com/a/aj/transform/loadingmoreunlogin?ajwvr=6&category=99991&getrecommand=1&no_timetip=false&__rnd=%s" % (int(round(time.time()*1000))) 
        else:
            url = "http://weibo.com/a/aj/transform/loadingmoreunlogin?ajwvr=6&category=1760&page=%s&lefnav=0&__rnd=%s" % (page, int(round(time.time()*1000)))
        r = ss.get(url)
        return r.content

    


if __name__ == "__main__":
    m = Message()
    data = m.hot(1)
    ret = json.loads(data)
    rd = ret["data"]
    soup = BeautifulSoup(rd, "lxml")
    lis = soup.select('ul[class~="pt_ul"] li[class~=pt_li]')
    print len(lis), lis



