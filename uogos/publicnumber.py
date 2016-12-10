# -*- coding:utf8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

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
import random

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

    '''
    dbcfg = dbcfg2
    conn2=MySQLdb.connect(host=dbcfg["host"],
            user=dbcfg["user"],
            passwd=dbcfg["password"],
            db=dbcfg["db"],
            port=dbcfg["port"],
            charset="utf8")
    '''

    htmlheaders = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            "Cookie":"pgv_pvi=4012552192; RK=UPFfKqcyMK; ptcz=208f346dd53f7e8303997108162c17ca1f0c53151715d54bb0d36896cbde332f; pt2gguin=o0756862636; verifysession=h01d6f9baa24d12931200ddda38f81e2b8989b3353f8fdcb8ca9d92f1366e1fb688382de3272890a03d; o_cookie=756862636; pgv_info=ssid=s2952550951; pgv_pvid=104691248; pac_uid=1_756862636; sig=h010399f9cca6eef6e4f2c73933a3bc2731ae7ffb9ab8a57fd8966587633673a9e86a601bfd1e613e3f",
            #'Cookie':'pgv_pvi=4012552192; pac_uid=0_5799c525f1e07; pgv_pvid=104691248; RK=UPFfKqcyMK; ptcz=208f346dd53f7e8303997108162c17ca1f0c53151715d54bb0d36896cbde332f; pt2gguin=o0756862636; sig=h01cde23eaa1431162da33b88b3c3d21c3072e02c2a2ef74f3d9faed2793f4d592d80b7eba1cf0db2fb',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
            }

    turl = 'http://weixin.sogou.com/weixin?query=%E9%94%82%E7%94%B5%E6%B1%A0&_sug_type_=&_sug_=n&type=1&ie=utf8'
    #turl = 'http://weixin.sogou.com/weixin?type=1&query=%E4%BA%8C%E6%89%8B%E8%BD%A6&ie=utf8&_sug_=n'
    
    hourre = re.compile(u'(\d{0,2})小时前')
    minre = re.compile(u'(\d{0,2})分钟前')
    dayre = re.compile(u'(\d+)天前')
    pubtimere = re.compile("vrTimeHandle552write\('(\d+)'\)")

    contentid = 4000
    homeid = contentid


    def __init__(self):
        s = requests.session()
        s.headers.update(self.htmlheaders)
        self.ss = s
        self.cursor = self.conn.cursor()
        self.cursor2 = None
        '''
        try:
            self.cursor2 = self.conn2.cursor()
        except:
            pass
        '''
        self.puburl = {}
        self.pubarturl = []


    def __del__(self):
        self.cursor.close()
        '''
        if self.cursor2:
            self.cursor2.close()
        '''

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
        url = self.turl + '&page=' + str(pn)
        try:
            r = self.ss.get(url)
        except Exception as e:
            mylog.Error('fail== %s %s' % (url, e))
            return
        if r.status_code != 200:
            mylog.info('fail== %s' % url)
            return
        self.saveFile(r.content, url, pn)
        self._parseData(r.content)
        '''
        b = self.saveDB(r.content)
        if not b:
            mylog.error('faildb== %s %s' % (url, pn))
        '''

    def _parseData(self, data):
        q =  BeautifulSoup(data, 'html.parser')
        dl = q.select('.news-list2 li .txt-box')
        gres = []
        mylog.info("parsedl: %d" % len(dl))
        for l in dl:
            res = {}
            try:
                #url title
                tit = l.select(".tit a")
                url = tit[0].get('href')
                res['url'] = url
                p = l.select('.info label')
                res['name'] = p[0].text
                pname = tit[0].text
                res['pname'] = pname
                mylog.info("number: %s" % url)
                self.puburl[pname] = url
            except Exception as e:
                mylog.error('failcsc== %s %s' % (l, e))
                continue
            try:
                #content
                p = l.select('p')
                res['funcinfo'] = p[0].text
                tmp = p[1].select('.sp-txt')[0].text.strip()
                if len(p) == 2:
                    if u'微信认证' not in tmp:
                        res['lastarticle'] = tmp 
                        tmp = p[1].select('.hui script')[0].text
                        tmp = self.pubtimere.search(tmp)
                        if tmp:
                            res['pubtime'] = int(tmp.group(1))
                    else:
                        res['authinfo'] = tmp
                else:
                    res['authinfo'] = tmp
                    res['lastarticle'] = p[2].select('.sp-txt')[0].text.strip()
                    tmp = p[2].select('.hui script')[0].text
                    tmp = self.pubtimere.search(tmp)
                    if tmp:
                        res['pubtime'] = tmp.group(1)
            except Exception as e:
                mylog.warn('fail funcauth== %s' % (e))
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
        sql = "insert ignore into jtyd_grab_wechat_pubnum(pub_url,pub_name,pub_pname,func_info,auth_info,last_article,last_article_time) values(%s, %s, %s, %s, %s, %s, %s)"
        vs = []
        for d in data:
            puburl = d.get('url')
            pubname = d.get('name')
            pubpname = d.get('pname')
            funcinfo = d.get('funcinfo')
            authinfo = d.get('authinfo')
            lastarticle = d.get('lastarticle')
            lapt = d.get('pubtime')
            vs.append((puburl, pubname, pubpname, funcinfo, authinfo, lastarticle, lapt))
        return sql, vs
        

    def saveDB(self, data):
        ret = self._parseData(data)
        if not ret:
            return False
        sql, val = self._orgInsertSql(ret)
        if val and sql:
            self.cursor.executemany(sql, val)
            self.conn.commit()
            '''
            try:
                self.cursor2.executemany(sql, val)
                self.conn2.commit()
            except Exception as e:
                mylog.error('jtyd fail!!! %s' % e)
            '''
            return True

    def crewlPubArticle(self, pname, url):
        try:
            r = self.ss.get(url)
        except Exception as e:
            mylog.errot('fail pubarticle: %s %s %s' % (pname, url, e))
            return
        if r.status_code != 200:
            mylog.errot('fail pubarticle: %s %s %s' % (pname, url, r.status_code))
        self.savePubArtice(pname, r.content)
        links =  self.parsePubArtice(r.content)
        self.pubarturl[-1:-1] = links

            
    def _genFileNameForPA(self, pname):
        t = time.localtime()
        strt = '%d-%d-%d-%d' % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour)
        dr =os.path.join('data', strt) 
        if not os.path.exists(dr):
            os.makedirs(dr)
        nm = 'article_%s.html' % (pname)
        fn = os.path.join(dr, nm)
        return fn


    def savePubArtice(self, pname, data):
        fn = self._genFileNameForPA(pname)
        with open(fn, 'w+') as f:
            f.write(data)


    def crawl(self):
        gl = []
        for pn in xrange(1, 2):
        #for pn in xrange(5, 11):
        #for pn in xrange(1, 5):
            g = gevent.spawn(self._crawl, pn)
            gl.append(g)
            if len(gl) >= 1:
                gevent.joinall(gl)
                gl = []
                sr = random.randint(5, 20)
                time.sleep(sr)
        if gl:
            gevent.joinall(gl)
            gl = []

        for k,v in self.puburl.items():
            g = gevent.spawn(self.crewlPubArticle, k, v)
            gl.append(g)
            if len(gl) >= 1:
                gevent.joinall(gl)
                gl = []
                sr = random.randint(5,20)
                time.sleep(sr)
        if gl:
            gevent.joinall(gl)
            gl = []

        for val in self.pubarturl:
            g = gevent.spawn(self.crewlArticle, val)
            gl.append(g)
            if len(gl) >= 1:
                gevent.joinall(gl)
                gl = []
                sr = random.randint(5, 20)
                time.sleep(sr)
            if gl:
                gevent.joinall(gl)


    def _genFileNameForArticle(self, pubid, fileid):
        t = time.localtime()
        strt = '%d-%d-%d-%d' % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour)
        dr =os.path.join('data', strt) 
        if not os.path.exists(dr):
            os.makedirs(dr)
        nm = 'art_%s_%s_%s.html' % (pubid, fileid, t.tm_min)
        fn = os.path.join(dr, nm)
        return fn


    def saveArtice(self, val, data):
        fn = self._genFileNameForArticle(val[1].replace('"', ""), val[4])
        with open(fn, 'w+') as f:
            f.write(data)
            line = "<!--"
            for v in val:
                line += str(v) + "_"
            line += "-->"
            f.write(line)

    def crewlArticle(self, val):
        if not val:
            return
        url = val[0]
        try:
            r = self.ss.get(url)
        except Exception as e:
            mylog.errot('fail pubarticle: %s %s %s' % (pname, url, e))
            return
        if r.status_code != 200:
            mylog.errot('fail pubarticle: %s %s %s' % (pname, url, r.status_code))
        self.saveArtice(val, r.content)


    def run(self):
        self.crawl()


    def parsePubArtice(self, data):
        p = data.find("var biz = ")
        d = data[p+10:]
        p1 = d.find("||")
        biz = d[:p1].strip()
        print biz
        p = d.find("var name=")
        d = d[p+9:]
        p = d.find(";")
        name = d[:p].strip()
        print name
        p = d.find("var msgList =")
        p1 = d.find("seajs.us")
        d = d[p+13:p1].strip()
        d = d.replace("amp;", '')
        d = d.replace("&quot;", '"')
        d = d.replace("\\\\", '')
        p = d.find("{")
        p1 = d.rfind("}")
        d = d[p:p1+1]
        d = d.decode("utf8")
        print d
        res = json.loads(d)
        links = []
        for val  in res["list"]:
            tval = val["app_msg_ext_info"]
            url = "http://mp.weixin.qq.com" + tval["content_url"]
            author = tval["author"]
            fileid = tval["fileid"]
            digest = tval["digest"]
            links.append((url, biz, name, author, fileid, digest))
        return links


if __name__ == '__main__':
    d = Lithium()
    d.run()



