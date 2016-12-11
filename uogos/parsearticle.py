# -*- coding:utf8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
import re
import time
import json
from bs4 import BeautifulSoup

msgtitlere = re.compile('var msg_title = "(.*?)";')
msgdescre = re.compile('var msg_desc = "(.*?)";')
msgsourceurlre = re.compile("var msg_source_url = '(.*?)';", re.S)
nicknamere = re.compile('var nickname = "(.*?)";')
pubtimere = re.compile('var publish_time = "(.*?)" \|\| "";')
usernamere = re.compile('var user_name = "(.*?)";')
codere = re.compile('var appuin = ""\|\|"(.*?)";')
pubcharname = re.compile(u'微信号.*?<span.*?>(.*?)<', re.S)

urlre = re.compile("<!--(http.*?)-->$")
msglinkre = re.compile('var msg_link = "(.*?)";', re.S)

def getcontent(data, res):
    soup = BeautifulSoup(data, 'html.parser')
    content = soup.find(id="js_content")
    if content:
        res["content"] = content.get_text()

def parsearticle(data, res):
    ret = urlre.search(data)
    if ret:
        res["sougou_url"] = ret.group(1)

    ret = msgtitlere.search(data)
    if ret:
        res["title"] = ret.group(1)
    ret = msgdescre.search(data)
    if ret:
        res["desc"] = ret.group(1)

    ret = msgsourceurlre.search(data)
    if ret:
        sourceUrl = ret.group(1).replace("amp;", "")
        sourceUrl = sourceUrl.replace(u"\\x26", "&")
        res["source_url"] = sourceUrl
    ret = msglinkre.search(data)
    if ret:
        link = ret.group(1)
        link = link.replace("amp;", "")
        link = link.replace(u"\\x26", "&")
        res["link"] = link
    ret = nicknamere.search(data)
    if ret:
        nickname = ret.group(1)
        res["nickname"] = nickname

    ret = pubtimere.search(data)
    if ret:
        res["pubtime"] = ret.group(1)
    ret = usernamere.search(data)
    if ret:
        res["username"] = ret.group(1)

    ret = codere.search(data)
    if ret:
        namecode = ret.group(1)
        res["namecode"] = namecode
    ret = pubcharname.search(data)
    if ret:
        charname = ret.group(1)
        res["charname"] = charname

def run():
    '''
    dd = ["data/2016-12-11-16", "data/2016-12-11-17",
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
               if not fn.endswith(".html"):
                   continue

               print fn
               rfn = os.path.join(path,fn)
               res = {}
               with open(rfn, "r") as f:
                   data = f.read()
                   if not isinstance(data, unicode):
                       data = data.decode("utf8")
                   parsearticle(data, res)
                   getcontent(data, res)

               if res:
                   newfn = rfn.split(".")
                   newfn = newfn[0] + ".json"
                   cnt += 1
                   with open(newfn, "w+") as fw:
                       json.dump(res, fw)
            print path, cnt



if __name__ == "__main__":
    run()
