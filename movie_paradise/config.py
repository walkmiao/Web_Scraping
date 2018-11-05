#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : config.py
# @Author: lch
# @Date  : 2018/10/18
# @Desc  :
from threading import Lock


start_url = "https://www.dy2018.com/"
prefix = "https://www.dy2018.com"
headers = {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"}
country_list = ['国产', '大陆', '日本', '美国', '香港', '印度', '德国', '英国', '韩国', '法国', '台湾', '泰国', '澳大利亚','俄罗斯', '希腊', '日韩', '欧美']
crawled_set = set()
mutex = Lock()
all_count = 0