# -*- coding:utf8 -*-

import re

from crawler import Crawler


class CrawlerExample(Crawler):
    def __init__(self):
        super(CrawlerExample, self).__init__("baidu")

    def initTasks(self):
        self.addListUrl("https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=0&rsv_idx=1&tn=baidu&wd=news&rsv_pq=b313ad7d0003a209&rsv_t=c5709MgwqApQ4wHyAx0fBFfbIHKooypzhVNyZPSoNhDUFUDleMF0LrN35KY&rqlang=cn&rsv_enter=1&rsv_sug3=12&rsv_sug1=15&rsv_sug7=100&rsv_sug2=0&inputT=3865&rsv_sug4=5734")

    #ret: True success  False: try get
    def procListPage(self, data):
        rep = re.compile('<a href="(.*?)" target="_blank">')
        ret = rep.search(data)
        if ret:
            self.addDetailUrl(ret.group(1))
        return True

    #ret: True success  False: try get
    def procDetailPage(self, data):
        rep = re.compile('<title>(.*?)</title>')
        ret = rep.search(data)
        if ret:
            print ret.group(1)
        return True

        


if __name__ == "__main__":
    c = CrawlerExample()
    c.run()

