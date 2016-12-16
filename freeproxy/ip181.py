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

from free import FreeBase

class IP181(FreeBase):
    startUrl = "http://www.ip181.com/"
    pageUrl = "http://www.ip181.com/daili/%d.html"


    htmlheaders = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Host': 'www.ip181.com',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'
            }

    qre = re.compile("<tr.*?>[\s\S]*?<td>(\d+\.\d+\.\d+\.\d+)</td>[\s\S]*?<td>(\d+)</td>[\s\S]*?<td>(.*?)</td>[\s\S]*?<td>(.*?)</td>[\s\S]*?<td>(.*?)</td>[\s\S]*?<td>(.*?)</td>[\s\S]*?<td>(.*?)</td>")

    def __init__(self):
        super(FreeBase, self).__init__()
        self.ss = requests.session()
        self.ss.headers.update(self.htmlheaders)


    def getDataByUrl(self, url, **args):
        '''
        args: --header
        '''
        try:
            r = self.ss.get(url)
        except Exception as e:
            return ""

        if r.status_code != 200:
            return ""
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
        dr = os.path.join('data', 'ip181', strt)
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


    def run(self):
        url = self.startUrl
        res = self.getDataByUrl(url)
        if not res:
            return
        ret = self.parseData(res, url)
        if not ret:
            return 
        self.saveResult(ret)


if __name__ == '__main__':
    i = IP181()
    i.run()
