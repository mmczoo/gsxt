# -*- coding:utf8 -*-

import time 
import requests 
import re
import json
import os
import random


headers = {
        #"Host": "s.weibo.com",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:49.0) Gecko/20100101 Firefox/49.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        #"Referer": "http://weibo.com/login.php?category=99991",
        "Cookie": "YF-Ugrow-G0=56862bac2f6bf97368b95873bc687eef; login_sid_t=4fcf29396044a5132d9ebd16c1cce1d4; YF-V5-G0=c6a30e994399473c262710a904cc33c5; WBStorage=5d1a8eee17d84880|undefined; _s_tentry=-; Apache=7393341328008.716.1484140287410; SINAGLOBAL=7393341328008.716.1484140287410; ULV=1484140287587:1:1:1:7393341328008.716.1484140287410:; YF-Page-G0=046bedba5b296357210631460a5bf1d2; SUB=_2AkMvKqAMf8NhqwJRmPgQy23nbYV3zwvEieKZdlHXJRMxHRl-yT9kqhAstRAny8W_gZnqES3AI69S7B853IzQJA..; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9W5U5ivEYTGvpaGSUg-Uhsmq",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
}

ss = requests.session()
ss.headers.update(headers)

def test():
    url = "http://weibo.com/?category=99991"
    r = ss.get(url)
    print r.content

def auth_ord(key):
    url = "http://s.weibo.com/user/%s&auth=ord" % key
    print url
    r = ss.get(url)
    return r.content

def getuser(userid):
    url = "http://weibo.com/u/%s?refer_flag=1001030201_" % userid
    print url
    ss.headers.update(headers)
    r = ss.get(url)
    print r.content


#rep = re.compile(r'''<a class=\\"W_texta W_fb\\".*?href=\\"(.*?)\\" title=\\"(.*?)\\" uid=\\"(.*?)\\"''')
rep = re.compile(r'<a class=\\"W_texta W_fb\\".*?href=\\"(.*?)\\" title=\\"(.*?)\\" uid=\\"(.*?)\\"')

rep2 = re.compile(r'uid=\\"(.*?)\\".*?person_num.*?_num\\">(.*?)<\\/a>.*?_num\\">(.*?)<\\/a>.*?_num\\">(.*?)<\\/a>')

'''
#rep = re.compile(r'uid=\\"(\w+)\\"')
#testdata = r'uid=\"dadafd\"'
testdata = r'<div class=\"person_detail\">\n\t<p class=\"person_name\">\n\t<a class=\"W_texta W_fb\" target=\"_blank\" href=\"http:\/\/weibo.com\/u\/3119987271?refer_flag=1001030201_\" title=\"\u601d\u4e88MAMI\u5962\u4f88\u54c1\u4ee3\u8d2d\" uid=\"3119987271\" suda-data=\"key=tblog_search_user&value=user_feed_2_name\">'
print testdata
print rep
ret = rep.findall(testdata)
print ret, len(ret)
exit(0)
'''



'''
with open("search", "r") as f:
    data = f.read()
'''

def genfile(key, suffix="html"):
    t = time.localtime()
    strt = '%04d%02d%02d%02d' % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour)
    dr = os.path.join('data', strt)
    if not os.path.exists(dr):
        os.makedirs(dr)
    fn = "%s.%s" % (key, suffix)
    return os.path.join(dr, fn)


users = {}

#key = u"papa"
#keys = ["mami", "mama", "jingyou"]
#keys = ["php", "java", "c", "python", "c++", "golang", "perl", "lua", "js", "html", "hadoop",
#    "blog", "debu", "www", "web", "hot", "hw", "a", "b", "c"]
keys = ["donglin"]

for key in keys:
    data = auth_ord(key)
    fn = genfile(key)
    with open(fn, "w+") as f:
        f.write(data)

    ret = rep.findall(data)
    print len(ret)
    for v in ret:
        print v[0], v[1], v[2]
        uid = v[2]
        if users.get(uid, None):
            continue
        url = v[0]
        name = v[1]
        users[uid] = {"url": url, "name": name}
        
    ret = rep2.findall(data)
    print len(ret)
    for v in ret:
        print v[0], v[1], v[2], v[3]
        uid = v[0]
        follow = v[1]
        fan = v[2]
        article = v[3]

        user = users.get(uid, None)
        if user:
            user["follow"] = follow
            user["fan"] = fan
            user["article"] = article
        else:
            users[uid] = {"follow": follow, "fan": fan, "article": article}
     
    fn = genfile(key, suffix="json")
    with open(fn, "w+") as f:
        json.dump(users, f)
    #getuser("1767059140")
    users = {}
    time.sleep(random.randint(15,40))


