#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/15 11:43
# @Author  : LCH
# @Site    : 
# @File    : get_top250movies.py
# @Software: PyCharm

from lxml import etree
import pandas as pd
import requests
import time

def download(url,k=0):
    try:
        if k==0:kw={}
        else:kw={'start':k,'filter':''}
        html=requests.get(url,params=kw)
        return html.text
    except:
        print('download fail...')

base_url='https://movie.douban.com/top250'

def get_data(url):
    k=0
    j=1
    title_list = []
    actor_list = []
    release_date_list = []
    country_list = []
    category_list = []
    rate_list = []
    comment_list = []
    rate_count_list = []


    while k<=250:
        html = download(url, k)
        soup = etree.HTML(html)
        k=k+25
        for i in soup.xpath('//div[@class="info"]'):
            #电影名称
            title = i.xpath('div[@class="hd"]/a/span[@class="title"][1]/text()')[0]
            title_list.append(title)
            #导演主演
            actor = i.xpath('div[@class="bd"]/p[1]/text()')[0].replace(" ", "").replace('\n','').replace('...', '')
            actor_list.append(actor)
            #上映日期
            release_date = i.xpath('div[@class="bd"]/p[1]/text()')[1].replace(" ", "").replace("\n",'').split('/')[0]
            release_date_list.append(release_date)
            #国家
            country = i.xpath('div[@class="bd"]/p[1]/text()')[1].replace(" ", "").split('/')[1]
            country_list.append(country)
            #分类
            category = i.xpath('div[@class="bd"]/p[1]/text()')[1].replace(" ", "").replace('\n','').split('/')[2]
            category_list.append(category)
            #评分
            rate = i.xpath('div[@class="bd"]/div[@class="star"]/span[@class="rating_num"]/text()')[0]
            rate_list.append(rate)
            #简评,对有的电影没有简评做了处理
            if len(i.xpath('div[@class="bd"]/p[@class="quote"]/span[@class="inq"]/text()'))>=1:
                comment = i.xpath('div[@class="bd"]/p[@class="quote"]/span[@class="inq"]/text()')[0].replace('\n','')
                comment_list.append(comment)
            else:
                comment=''
                comment_list.append(comment)
            #评论人数
            rate_count = i.xpath('div[@class="bd"]/div[@class="star"]/span[4]/text()')[0].split('评价')[0]
            rate_count_list.append(rate_count)
            #写入文件
            with open('top250movie.txt', 'a', encoding='utf-8') as f:
                f.write('Top%s\n影片名称:%s\n评分:%s\n评论数:%s\n上映日期:%s\n上映国家:%s\n分类:%s\n简评:%s\n%s\n'% (
                j, title, rate, rate_count, release_date, country, category, comment, actor))
                f.write(''.center(50, '*')+'\n')
            j=j+1
    #写入csv
    data_frame = pd.DataFrame({'标题':title_list,'导演演员':actor_list,'上映日期':release_date_list,'国家':country_list
                               ,'分类':category_list,'评分':rate_list,'简评':comment_list,'评论人数':rate_count_list})
    data_frame.to_csv('250.csv',sep=",",encoding='utf_8_sig')

if __name__=='__main__':
    start=time.time()
    get_data(base_url)
    print('耗时%s'%(time.time()-start))










    

