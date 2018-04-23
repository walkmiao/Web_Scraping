#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/18 15:18
# @Author  : LCH
# @Site    : 
# @File    : 多线程爬豆瓣Top250.py
# @Software: PyCharm
from threading import Thread
from lxml import etree
import requests
import pandas as pd
import time
from queue import Queue

class douban_Spider(Thread):
    def __init__(self,url,q):
        super(douban_Spider,self).__init__()
        self.url=url
        self.q=q
    def get_html(self,url):
        html=requests.get(url).text
        return html
    def get_info(self):
        response=self.get_html(self.url)
        soup=etree.HTML(response)
        node_list=soup.xpath('//div[@class="info"]')
        for i in node_list:
            # 电影名称
            title = i.xpath('div[@class="hd"]/a/span[@class="title"][1]/text()')[0]
            # 导演主演
            actor = i.xpath('div[@class="bd"]/p[1]/text()')[0].replace(" ", "").replace('\n', '').replace('...', '')
            self.q.put(title + '*'.center(10,'*') + actor)
    def run(self):
        self.get_info()
def main():
    q=Queue()
    thread_list=[]
    base_url='https://movie.douban.com/top250?start='
    url_list=[base_url+str(i) for i in range(0,226,25) ]
    for i in url_list:
        ds=douban_Spider(i,q)
        ds.start()
        thread_list.append(ds)
    for t in thread_list:
        t.join()
    while not q.empty():
        for i in range(1,q.qsize()+1):
            print(i,q.get())
if __name__=='__main__':
    start=time.time()
    main()
    print('耗时:%s'%(time.time()-start))




