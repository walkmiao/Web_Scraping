#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/4/7 22:34
# @Author  : lch
# @File    : Crawling.py
import requests
import re
from bs4 import BeautifulSoup
from lxml import etree
import pandas as pd

#HTML下载函数
def download(url,retries=2):
    headers={'User-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'}
    html = requests.get(url,headers=headers)
    if retries>0:
        print('Downloading',url)
        if(500<=html.status_code<=600):
            print('error code:%s'%html.status_code)
            download(url,retries=retries-1)
        return html
    else:
        print('经过%s次重试...'%retries)
        return None
#下载链接地址的获取函数
def crawl_sitemap(seed_url):
    # 此部分使用lxml的etree来解析指定链接
    craw_queue=[seed_url]
    while craw_queue:
        url=craw_queue.pop()
        html=download(url).text
    site_map=[]
    tree = etree.HTML(html)
    href = tree.xpath('//a')
    for i in href:
        print(i.get('href'))
    #     if re.match(r'.*-\d', i.get('href')):
    #         site_map.append(url + i.get('href'))
    #     if re.match(r'.*index/\d{1,2}',i.get('href')):
    #         crawl_sitemap(url+i.get('href'))
    # return site_map

    # 注释部分采用bs4获取需要的链接

    # bs=BeautifulSoup(html,'lxml')
    # zzr=bs.find_all('a')
    # sitemap=[]
    #
    # for i in zzr:
    #     if re.match(r'.*-\d{1}',i["href"]):
    #         sitemap.append(url+i["href"])
    # return sitemap



#获取指定数据
def get_info():
    area_list=[]
    country_list=[]
    for i in crawl_sitemap('http://example.webscraping.com'):
        html=download(i).text
        tree=etree.HTML(html)
        area=tree.xpath('//tr[@id="places_area__row"]/td[@class="w2p_fw"]')
        country=tree.xpath('//tr[@id="places_country__row"]/td[@class="w2p_fw"]')
        area_list.append(area[0].text)
        country_list.append(country[0].text)

    area_info=dict(zip(country_list,area_list))
    return area_info

    #以下部分使用bs4获取信息
    #     soup=BeautifulSoup(html,'lxml')
    #     zzr=soup.find_all('tr',attrs={'id':"places_area__row"})
    #     for i in zzr:
    #         tdlist=i.find_all('td')
    #         info_list.append(tdlist[1].string)
    # return info_list

def write_csv():
    dict_info=get_info()
    data_frame=pd.DataFrame({'Country':list(dict_info.keys()),'Area':list(dict_info.values())})


print(crawl_sitemap('http://example.webscraping.com'))


