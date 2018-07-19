#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/14 21:25
# @Author  : LCH
# @Site    : 
# @File    : requests_module.py
# @Software: PyCharm
import requests
payload={'key1':'value1','key2':'value2'}
r=requests.post('http://httpbin.org/post',data=payload)
print(r.text)