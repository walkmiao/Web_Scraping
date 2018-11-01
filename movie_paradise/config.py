#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : config.py
# @Author: lch
# @Date  : 2018/10/18
# @Desc  :
# start_url = "http://www.ygdy8.net/index.html"
start_url = "https://www.dy2018.com/"
prefix = "https://www.dy2018.com"
headers = {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"}
movie_kind_list = ['动作片', '剧情片', '爱情片', '喜剧片', '科幻片', '恐怖片', '动画片', '惊悚片', '战争片', '犯罪片', '综艺']
country_list = ['国产', '大陆', '日本', '美国', '香港', '印度', '德国', '英国', '韩国', '法国', '台湾', '泰国', '澳大利亚','俄罗斯', '希腊', '日韩']
crawled_set = set()