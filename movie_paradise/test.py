#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : test.py
# @Author: lch
# @Date  : 2018/11/1
# @Desc  :
from movie_paradise.movie_crawl import get_res, crawl_index, crawl_kinds
from movie_paradise.config import start_url
from lxml import etree
from queue import Queue
import re
url = 'https://www.dy2018.com/i/100076.html'
q = Queue()

def crawl_movie_info(url):
    '''
    :param q: queue
    :param conn: sqlite连接
    :return:
    '''

    html, res_url = get_res(url)
    ftp_link = list()
    magent_link = list()
    sel = etree.HTML(html)
    for i in sel.xpath("//div[@id='Zoom']//table"):
        link = i.xpath(".//a/@href")[0] if i.xpath(".//a/@href") else "暂缺"  # 电影只有一个连接，电视则有多条连接
        if 'ftp' in link:
            ftp_link.append(link)
        else:
            magent_link.append(link)
    ftp_link = '||'.join(ftp_link)
    magent_link = '||'.join(magent_link)
    movie_info = sel.xpath("//div[@class='title_all']//h1/text()")[0] \
        if sel.xpath("//div[@class='title_all']//h1/text()") else "资源信息未解析出"
    publish_date = re.findall(r'.*发布时间.*(\d{4}\-\d{2}\-\d{2}).*', html)[0]
    print('movieinfo:{}, ftp_link:{}, magent_link:{}, date:{}'.format(movie_info, ftp_link, magent_link,  publish_date))

result = crawl_movie_info(url)
print(result)

