#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/5/9 20:25
# @Author  : lch
# @File    : courtSpider.py

import requests
from lxml import etree
from dateutil.relativedelta import relativedelta
import datetime,time
import json
from requests.exceptions import ConnectionError,HTTPError,ConnectTimeout

#html爬取
def get_html(baseUrl,data=None):
    html=requests.get(baseUrl,data)
    try:
        if html.status_code==200:
            return html.text
    except ConnectionError:
        raise ConnectionError
#爬取数据的清洗筛选
def parse_html(html):
    item=dict()
    tree=etree.HTML(html)
    for i in tree.xpath("//table[@id='report']/tbody//tr"):
        if i.xpath("td[1]//text()")[0].replace('\n','')=="法院":
            continue
        #法院
        item['court']=i.xpath("td[1]//text()")[0].strip()
        #法庭
        item['court2'] = i.xpath("td[2]//text()")[0].strip()
        #开庭日期
        item['court_date'] = i.xpath("td[3]//text()")[0].strip()
        #案号
        item['case_number'] = i.xpath("td[4]//text()")[0].strip()
        #案由
        item['case_cause'] = i.xpath("td[5]//text()")[0].strip()
        #承办部门
        item['depart'] = i.xpath("td[6]//text()")[0].strip()
        #审判长
        item['chief'] = i.xpath("td[7]//text()")[0].strip()
        #原告
        item['demandant'] = i.xpath("td[8]//text()")[0].strip()
        #被告
        item['defendant'] = i.xpath("td[9]//text()")[0].strip()
        yield item

#筛选后数据写入文件
def write_to_file(content):
    with open('result.txt','a',encoding='utf-8') as f:
         f.write(json.dumps(content,ensure_ascii=False)+'\n')

def get_pagesNum():
    baseUrl="http://www.hshfy.sh.cn/shfy/gweb2017/ktgg_search_content.jsp?"
    pagesNum=etree.HTML(get_html(baseUrl)).xpath("//div[@class='meneame']//strong/text()")[0]
    pagesNum=int(pagesNum)
    if pagesNum%15==0:
        pagesNum=pagesNum//15
    pagesNum=(pagesNum//15)+1

    return pagesNum
    # while page<=pagesNum:
def main():
    baseUrl = "http://www.hshfy.sh.cn/shfy/gweb2017/ktgg_search_content.jsp?"
    pagesNum=get_pagesNum()
    page=1

    timeStart=time.time()
    while page<=pagesNum:
        data = {
            'ktrqks': datetime.date.today(),
            'ktrqjs': datetime.date.today() + relativedelta(months=1),
            'pagesnum': page
        }
        print(data['pagesnum'])
        print('正在爬取%d页....'%page)
        html=get_html(baseUrl,data)
        info=parse_html(html)
        print('正在写入第%d页...'%page)
        for i in info:
            write_to_file(i)
        time.sleep(0.2)
        page+=1
    if page==(pagesNum+1):
        print('爬取完毕..共耗时%d秒'%(time.time()-timeStart))


if __name__ == '__main__':
    main()
