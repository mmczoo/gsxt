#-*- coding:utf8 -*-


import re
import redis
import json



rd = redis.StrictRedis(host="10.1.192.18",port=6379, db=0) 

key = "proxy_socks5"
ips = rd.lrange(key, 0, -1)
print len(ips)

rep = re.compile("socks5://(\d+\.\d+\.\d+)\.\d+:(\d+)")

cips = set()
ports = set()

addrs = set()

for ip in ips:
    if not ip.startswith("socks5"):
        continue
    addrs.add(ip)
    ret = rep.search(ip)
    if ret:
        cips.add(ret.group(1))
        ports.add(int(ret.group(2)))
print len(cips), len(ports)
#print list(cips)
#print ports

rd = redis.StrictRedis(host="10.1.192.18",port=6379, db=14) 
key = "socks"
ips = rd.lrange(key, 0, -1)
print len(ips)
for ip in ips:
    if not ip.startswith("socks5"):
        continue
    ret = rep.search(ip)
    if ret:
        cips.add(ret.group(1))
        ports.add(int(ret.group(2)))


#print list(cips)
print len(cips), len(ports)
print list(cips)
print ports


print len(addrs)
print addrs

