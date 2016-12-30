# -*- coding:utf8 -*-

import md5
import threading

import MySQLdb
from config import wdbconf

class DBTool(object):
    dbconf = wdbconf
    __conns = {}
    __mutex=threading.Lock()

    def __init__(self):
        self.cursor = None

    @staticmethod
    def getInstance(dbconf):
        strdb = str(sorted(dbconf.iteritems(), key=lambda d:d[0]))
        m1 = md5.new()
        m1.update(strdb)
        hs = m1.hexdigest()

        DBTool.__mutex.acquire()
        conn = DBTool.__conns.get(hs, None)
        if conn:
            print "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            dbtool = DBTool()
            dbtool.cursor = conn.cursor()
            DBTool.__mutex.release()
            return dbtool

        print "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        conn = MySQLdb.connect(host=dbconf["host"],
                           user=dbconf["user"],
                           passwd=dbconf["password"],
                           db=dbconf["db"],
                           port=dbconf["port"],
                           charset="utf8")
        DBTool.__conns[hs] = conn
        dbtool = DBTool()
        dbtool.cursor = conn.cursor()
        DBTool.__mutex.release()
        return dbtool

    def __del__(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None

    def excecute(self, sql, *args):
        return self.cursor.execute(sql, args)

    def fetchall(self):
        return self.cursor.fetchall()



if __name__ == "__main__":
    wdbconf = {
        "host": "192.168.54.198",
        "port": 3306,
        "user": "yaowu",
        "password": "123456",
        "db": "accumulation",
        }

    d = DBTool.getInstance(wdbconf)
    print("%d"%id(d))
    d = DBTool.getInstance(wdbconf)
    print("%d"%id(d))

    wdbconf = {
        "host": "192.168.54.198",
        "port": 3306,
        "user": "root",
        "password": "123456",
        "db": "comls",
        }
    d = DBTool.getInstance(wdbconf)
    print("%d"%id(d))
