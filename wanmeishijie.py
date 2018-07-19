#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/12 20:52
# @Author  : LCH
# @Site    : 
# @File    : wanmeishijie.py
# @Software: PyCharm
import requests, time, random
from multiprocessing import Process,Pool,Queue
from lxml import etree
from threading import Thread
base_url = "https://www.cangqionglongqi.com/wanmeishijie/"
headers = {'User-Agent':'User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'}



def get_sub_html(url):
    tar = list()
    requests.packages.urllib3.disable_warnings()
    html = requests.get(url, headers=headers, timeout=500, verify=False)
    html.encoding = 'gbk'
    tree = etree.HTML(html.text)
    total_html = len(tree.xpath("//dd"))
    for i in tree.xpath("//dd"):
        sub_html = base_url + i.xpath('a/@href')[0]
        tar.append(sub_html)
    return tar, total_html


def sub_work(url, queue):
    response = requests.get(url, headers=headers)
    response.encoding = 'gbk'
    tree = etree.HTML(response.text)
    result=''
    for i in tree.xpath("//div[@id='content']/text()"):
        result +=i
    book_name = tree.xpath("//div[@class='bookname']/h1/text()")[0]
    dic = dict()
    dic[book_name] = result
    queue.put(dic)
    time.sleep(0.2)

def write_to_txt(queue):
    global total
    global a
    while True:
        dic= queue.get()
        if dic:
            for i,j in dic.items():
                with open('1.txt', 'a+', encoding='utf-8') as f:
                    f.write('***%s***\n%s\n' % (i, j))
            a +=1
            print('下载百分比：%s %%'%((a/total)*100))
            time.sleep(0.2)


if __name__ == '__main__':
    q = Queue()
    tar,total_html = get_sub_html(base_url)
    print('需爬去总章节数:%s'%total_html)
    global total
    total = total_html
    global a
    a=0
    thread_list = []
    for i in tar:
        p = Thread(target=sub_work, args=(i, q))
        p2 = Thread(target=write_to_txt, args=(q,))
        thread_list.append(p)
        thread_list.append(p2)
    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join()

    print('爬去完毕')

