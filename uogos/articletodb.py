# -*- coding:utf8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
import re
import time
import json
from bs4 import BeautifulSoup
import MySQLdb

conn=MySQLdb.connect(host=dbcfg["host"],
            user=dbcfg["user"],
            passwd=dbcfg["password"],
            db=dbcfg["db"],
            port=dbcfg["port"],
            charset="utf8")
cursor = conn.cursor()



def _savetodb():
    global cacheres
    feilds = "weixin_name,weixin_code,article_name,article_url,article_content,article_desc,platform_url,create_by,titledate"
    valuespos = "%s, %s, %s, %s, %s, %s, %s, %s, %s"
    sql = "insert ignore into jtyd_weixin_article(%s) values(%s)" % (feilds, valuespos)

    vs = []
    for res in cacheres:
        v = (res["nickname"], res["charname"], res["title"],
             res["source_url"], res["content"], res["desc"],
             res["link"], "jyl", res["pubtime"])
        vs.append(v)
    cnt = cursor.executemany(sql, vs)
    print cnt
    conn.commit()


cacheres = []
def savetodb(res):
    global cacheres
    if res:
        cacheres.append(res)

    if len(cacheres) > 30:
        _savetodb()
        cacheres = []

def run():
    #dd = ["data/2016-12-11-16"]
    '''
    dd = ["data/2016-12-11-17",
          "data/2016-12-11-18", "data/2016-12-11-19",
          "data/2016-12-11-20"]
    '''
    #dd = ["data/2016-12-11-21"]
    dd = ["data/2016-12-11-22"]
    for name in dd:
        cnt = 0
        for path, dirs, files in os.walk(name):
            print path
            for fn in files:
                if not fn.endswith(".json"):
                    continue
                print fn
                rfn = os.path.join(path,fn)
                with open(rfn, "r") as f:
                    try:
                        res = json.load(f)
                        savetodb(res)
                        cnt += 1
                    except Exception as e:
                        print e
            print path, cnt
    _savetodb()



if __name__ == "__main__":
    run()
