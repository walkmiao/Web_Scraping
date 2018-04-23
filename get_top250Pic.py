#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/15 21:26
# @Author  : LCH
# @Site    : 
# @File    : get_top250Pic.py
# @Software: PyCharm

from lxml import etree
import pandas as pd
import requests
import time
import os
from get_top250movies import download

base_url='https://movie.douban.com/top250'

def get_data(url):
        k=0
        while k<=250:
            k+=25
            html = download(url,k)
            soup = etree.HTML(html)
            dir='d:/pic/'
            for i in soup.xpath('//div[@class="pic"]/a/img/@src'):
                path=dir+i.split('/')[-1]
                print(i)
                if not os.path.exists(dir):
                    os.makedirs(dir)
                if not os.path.exists(path):
                    img = requests.get(i)
                    with open(path,'wb') as f:
                        print(path)
                        f.write(img.content)
                        print('save pic successful!')
                else:
                    print('pic already exists!')

get_data(base_url)
