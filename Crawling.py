#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/4/7 22:34
# @Author  : lch
# @File    : Crawling.py
import requests
def download(url,retries=2):
    print('Downloading',url)
    try:
        html=requests.get(url).text
    except requests.ConnectionError as e:
        print('HTTP ERROR',e.reason)
        html=None
        if retries>0:
            if hasattr(e,'code') and 500<=e.code<600:
                return download(url,retries-1)
    return html

print(download('http://www.baidu.com'))