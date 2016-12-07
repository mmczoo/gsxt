# -*- coding:utf8 -*-

import os
import re
import time
import json
import shutil
import md5
import logging as mylog
#mylog.basicConfig(level=mylog.DEBUG,
mylog.basicConfig(level=mylog.INFO,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
import cPickle as pickle
from urlparse import urlparse

import requests
import MySQLdb
import gevent
from gevent import monkey; monkey.patch_socket()
from bs4 import BeautifulSoup


dbcfg = {
        "host": "192.168.54.198",
        "port": 3306,
        "user": "yaowu",
        "password": "123456",
        "db": "accumulation",
        }

dbcfg2 = {
        "host": "101.200.87.104",
        "port": 3306,
        "user": "mmczoo",
        "password": "mmczoo@git",
        "db": "jtyd",
        }

class Lithium(object):
    conn=MySQLdb.connect(host=dbcfg["host"],
            user=dbcfg["user"],
            passwd=dbcfg["password"],
            db=dbcfg["db"],
            port=dbcfg["port"],
            charset="utf8")

    dbcfg = dbcfg2
    conn2=MySQLdb.connect(host=dbcfg["host"],
            user=dbcfg["user"],
            passwd=dbcfg["password"],
            db=dbcfg["db"],
            port=dbcfg["port"],
            charset="utf8")

    htmlheaders = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'
            }

    turl = 'https://www.baidu.com/s?wd=%E9%94%82%E7%94%B5%E6%B1%A0&tn=baidurt&ie=utf-8&rtt=1&bsst=1'
    
    hourre = re.compile(u'(\d{0,2})小时前')
    minre = re.compile(u'(\d{0,2})分钟前')
    dayre = re.compile(u'(\d+)天前')

    contentid = 4000
    homeid = contentid


    def __init__(self):
        s = requests.session()
        s.headers.update(self.htmlheaders)
        self.ss = s
        self.cursor = self.conn.cursor()
        self.cursor2 = None
        try:
            self.cursor2 = self.conn2.cursor()
        except:
            pass

    def __del__(self):
        self.cursor.close()
        if self.cursor2:
            self.cursor2.close()


    def _genFileName(self, pn):
        t = time.localtime()
        strt = '%d-%d-%d-%d' % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour)
        dr =os.path.join('data', strt) 
        if not os.path.exists(dr):
            os.makedirs(dr)
        nm = 'pn%d_%s.html' % (pn, t.tm_min)
        fn = os.path.join(dr, nm)
        return fn

    def _crawl(self, pn):
        url = self.turl + '&pn=' + str(pn*10)
        try:
            r = self.ss.get(url)
        except Exception as e:
            mylog.Error('fail== %s %s' % (url, e))
            return
        if r.status_code != 200:
            mylog.info('fail== %s' % url)
            return
        self.saveFile(r.content, url, pn)
        b = self.saveDB(r.content)
        if not b:
            mylog.error('faildb== %s %s' % (url, pn))

    def _parseData(self, data):
        q =  BeautifulSoup(data, 'html.parser')
        dl = q.select('.content table')
        gres = []
        for l in dl:
            res = {}
            try:
                #url title
                p = l.select('a')
                res['url'] = p[0].get('href')
                res['title'] = p[0].text.replace('<em>', '').replace('</em>', '')
            except Exception as e:
                mylog.error('failcsc== %s %s' % (l, e))
                continue
            try:
                #content
                p = l.select('font')
                res['outline'] = p[0].text.replace('<em>', '').replace('</em>', '').replace(u'\xa0', '')
            except Exception as e:
                mylog.error('failcsc== %s %s' % (l, e))

            try:
                #websit time 
                p = l.select('font div')
                #&nbsp;  u'\xa0'
                tp = p[0].text.replace(u'\xa0', '')
                tp = tp.split('-')
                res['website'], res['ptime'] = tp[0], tp[1]
            except Exception as e:
                p = urlparse(res['url'])
                res['website'] = p.hostname
                res['ptime'] = tp[0]
            gres.append(res)
        return gres


    def saveFile(self, data, url, pn):
        fn = self._genFileName(pn)
        with open(fn, 'w+') as f:
            f.write(data)
            line = '\n<!--%s-->' % url
            line += '\n<!--%d-->' % int(time.time())
            f.write(line)
        mylog.info('succ== %s' % url)

    def _formatPTime(self, pt):
        now = time.time()
        p = self.hourre.search(pt)
        if p:
            h = int(p.group(1))
            if h > 23:
                return None
            sec = now - h * 3600
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(sec))
        p = self.minre.search(pt)
        if p:
            h = int(p.group(1))
            if h > 59:
                return None
            sec = now - h * 60
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(sec))
        p = self.dayre.search(pt)
        if p:
            h = int(p.group(1))
            if h > 59:
                return None
            sec = now - h * 86400
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(sec))
        return None
         
    def _orgInsertSql(self, data):
        sql = "insert ignore into jtyd_grab_news(url,title,titledate,getdate,contentid,homeid,homename,content,grab_keyword) values(%s, %s, %s, now(), %s, %s, %s, %s, '锂电池')"
        vs = []
        for d in data:
            url = d.get('url')
            title = d.get('title')
            content = d.get('outline')
            website = d.get('website')
            ptime = d.get('ptime')
            titledate = self._formatPTime(ptime)
            vs.append((url, title, titledate, self.contentid, self.homeid, website, content))
        return sql, vs
        

    def saveDB(self, data):
        ret = self._parseData(data)
        if not ret:
            return False
        sql, val = self._orgInsertSql(ret)
        if val and sql:
            self.cursor.executemany(sql, val)
            self.conn.commit()
            try:
                self.cursor2.executemany(sql, val)
                self.conn2.commit()
            except Exception as e:
                mylog.error('jtyd fail!!! %s' % e)
            return True


    def crawl(self):
        gl = []
        #for pn in xrange(0, 73):
        #for pn in xrange(0, 1):
        for pn in xrange(0, 30):
        #for pn in xrange(10, 73):
        #for pn in xrange(72, 73):
            g = gevent.spawn(self._crawl, pn)
            gl.append(g)

            if len(gl) >= 5:
                gevent.joinall(gl)
                gl = []
                time.sleep(3)
        if gl:
            gevent.joinall(gl)

    def run(self):
        self.crawl()



if __name__ == '__main__':
    d = Lithium()
    d.run()

