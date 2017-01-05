# -*- coding:utf8 -*-
import md5
import time
import logging as mylog
mylog.basicConfig(level=mylog.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')


from pybloomfilter import BloomFilter


class Filter(object):
    def __init__(self, capacity=1000000, errrate=0.01, fname="filter.bloom"):
        try:
            self.bf = BloomFilter.open(fname)
        except:
            self.bf = BloomFilter(capacity, errrate, fname)
        self.syncmax = 100
        self.synccnt = 0


    def isExists(self, value):
        if value:
            return value in self.bf
        return True


    def add(self, value):
        if value:
            try:
                ret = self.bf.add(value)
                self.synccnt += 1
                if self.synccnt >= self.syncmax:
                    self.bf.sync()
                    self.synccnt = 0
                return ret
            except Exception as e:
                mylog.info("bf add fail! %s %s" % (e, value))

        return True

    def sync(self):
        self.bf.sync()


if __name__ == "__main__":
    f = Filter(fname="csdn_filter.bloom")

    print f.isExists("http://blog.csdn.net/jiangwei0910410003/article/details/53954686")
    print f.isExists("http://blog.csdn.net")
