#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : JD_scrapy.py
# @Author: lch
# @Date  : 2018/5/25
# @Desc  :
import requests
import json

url="https://sclub.jd.com/" \
    "comment/productPageComments.action?callback" \
    "=fetchJSON_comment98vv12653&productId=2551276&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1"

html=requests.get(url)
print(html.text)
json_content=json.loads(html.text[:3])
# print(json_content[1])/
