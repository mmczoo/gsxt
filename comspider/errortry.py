# -*- coding:utf8 -*-

import logging as mylog
mylog.basicConfig(level=mylog.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')

from bfilter import Filter 

class ErrorTry(object):
    def __init__(self, trymax=3, fname="errtry.bloom", errlink="errlink.txt"):
        self.trydict = {}
        self.bfilter = Filter(capacity=100000, fname=fname)
        self.trymax = trymax
        self.errlinkfd = open(errlink, "a+")

    def isTry(self, value):
        if not value:
            return False

        if self.bfilter.isExists(value):
            #print "aaaaaaaaaaaaa"
            return False

        trycnt = self.trydict.get(value, 0)
        if trycnt >= self.trymax:
            self.bfilter.add(value)
            self.trydict.pop(value)
            mylog.warn("maxtry: %s" % value)
            self.errlinkfd.write(value + "\n")
            return False

        try:
            self.trydict[value] += 1
        except:
            self.trydict[value] = 1

        return True

    def sync(self):
        self.bfilter.sync()


if __name__ == "__main__":
    e = ErrorTry()
    print e.isTry("dddddddddddddddddddddd")
    print e.isTry("dddddddddddddddddddddd")
    print e.isTry("dddddddddddddddddddddd")
    print e.isTry("dddddddddddddddddddddd")
    print e.isTry("dddddddddddddddddddddd")
    print e.isTry("dddddddddddddddddddddd")
    print e.isTry("dddddddddddddddddddddd")
    print e.isTry("dddddddddddddddddddddd")
    
