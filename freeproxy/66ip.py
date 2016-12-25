# -*- coding:utf8 -*-

#http://www.kxdaili.com/

import requests
import re
import time
import os
import json
import sys
reload(sys) 
sys.setdefaultencoding("utf-8")

import redis 

from free import FreeBase

class IP181(FreeBase):
    httpstartUrl = "http://m.66ip.cn/nmtq.php?getnum=100&isp=0&anonymoustype=3&start=&ports=&export=&ipaddress=&area=1&proxytype=0&api=66ip"
    httpsstartUrl = "http://m.66ip.cn/nmtq.php?getnum=100&isp=0&anonymoustype=3&start=&ports=&export=&ipaddress=&area=1&proxytype=1&api=66ip"

    htmlheaders = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Host': 'm.66ip.cn',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'
            }

    
    qre = re.compile("(\d+\.\d+\.\d+\.\d+:\d+)<br/>")

    def __init__(self):
        super(FreeBase, self).__init__()
        self.ss = requests.session()
        self.ss.headers.update(self.htmlheaders)
        self.pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0) 
        self.rediscli = redis.Redis(connection_pool=self.pool)

        self.rkey = "proxy_66ip"

    def getDataByUrl(self, url, **args):
        '''
        args: --header
        '''
        try:
            r = self.ss.get(url)
        except Exception as e:
            print(e)
            return ""

        if r.status_code != 200:
            print(r.status_code)
            return ""
        print r.content
        return r.content


    def parseData(self, data, url):
        '''
        url: assistant
        '''
        if not isinstance(data, unicode):
            data = data.decode("gb2312")
        return self.qre.findall(data)
        

    
    def _genFile(self):
        t = time.localtime()
        strt = '%d-%d-%d' % (t.tm_year, t.tm_mon, t.tm_mday)
        dr = os.path.join('data', '66ip', strt)
        if not os.path.exists(dr):
            os.makedirs(dr)
        nm = '%d_%d.json' % (t.tm_hour, t.tm_min)
        fn = os.path.join(dr, nm)
        return fn


    def saveResult(self, result):
        if not result:
            return
        fn = self._genFile()
        with open(fn, "w+") as f:
            json.dump(result, f)
    

    def saveToRedis(self, result, ptype):
        if ptype == "HTTP":
            rtype = "http://"
        elif ptype == "HTTPS":
            rtype = "https://"
        else:
            return
        for r in result:
            px = rtype  + r
            self.rediscli.lpush(self.rkey, px)

    def run(self):
        url = self.httpstartUrl
        res = self.getDataByUrl(url)
        if not res:
            return
        ret = self.parseData(res, url)
        if not ret:
            return 
        self.saveResult(ret)
        self.saveToRedis(ret, "HTTP")
        print url, len(ret)

        url = self.httpsstartUrl
        res = self.getDataByUrl(url)
        if not res:
            return
        ret = self.parseData(res, url)
        if not ret:
            return 
        self.saveResult(ret)
        self.saveToRedis(ret, "HTTPS")
        print url, len(ret)


if __name__ == '__main__':
    i = IP181()
    i.run()
