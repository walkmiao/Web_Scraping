#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/23 10:23
# @Author  : LCH
# @Site    : 
# @File    : 豆瓣图书top250.py
# @Software: PyCharm
#爬取豆瓣图书top250
from lxml import etree
import requests
from threading import Thread
from queue import Queue
import time
class bookSpider(Thread):
    def __init__(self,url,queue,headers):
        super(bookSpider,self).__init__()
        self.url=url
        self.queue=queue
        self.headers=headers
    def get_html(self,url):
        html=requests.get(url,headers=self.headers)
        return html.text
    def get_info(self):
        html=self.get_html(self.url)
        html_tree=etree.HTML(html)
        node_list=html_tree.xpath('//td[2]')
        for i in node_list:
            title=i.xpath('div[@class="pl2"]/a/text()')[0].replace(' ','').replace('\n','')
            author=i.xpath('p[@class="pl"]/text()')[0].split('/')[0]
            self.queue.put(title+'*'.center(10,'*')+author)
    def run(self):
        self.get_info()


def main():
    base_url='https://book.douban.com/top250?start='
    url_list=[base_url+str(i) for i in range(0,251,25)]
    q=Queue()
    thread_list=[]
    for i in url_list:
        bs=bookSpider(i,q,headers='')
        bs.start()
        thread_list.append(bs)
    for i in thread_list:
        i.join()
    for i in range(1,q.qsize()+1):
        print(i,q.get())

if __name__=='__main__':
    start=time.time()
    main()
    print('耗时:{}'.format(time.time()-start))





