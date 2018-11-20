#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : urllib_demo.py
# @Author: lch
# @Date  : 2018/11/15
# @Desc  :
from urllib import request, parse
from http import cookiejar
data = {"name":"lch"}

url = "http://www.httpbin.org/post"
# request可以生成一个request对象 urlopen的参数可以是一个request对象 也可以是普通参数
req = request.Request(url=url, data=bytes(parse.urlencode(data), encoding='utf-8'))
res = request.urlopen(req)
res1 = request.urlopen(url=url, data=bytes(parse.urlencode(data), encoding='utf-8'))

# res_handle = request.ProxyHandler({'http': '140.82.5.100:15576'}) # 设置代理ip 和类型
# opener = request.build_opener(res_handle) # 根据handle创建opener
# res = opener.open("http://wwww.bidu.com")


cookie_ins = cookiejar.CookieJar()
coo_handle = request.HTTPCookieProcessor(cookie_ins)
opener = request.build_opener(coo_handle)
res = opener.open("http://www.baidu.com")
for i in cookie_ins:
    print(i.name, i.value)
# print(res.read())
# print(res.read().decode('utf-8'))
# print(res1.read().decode('utf-8'), res1.status)