#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/15 10:36
# @Author  : LCH
# @Site    : 
# @File    : test.py
# @Software: PyCharm
from fake_useragent import UserAgent
import requests
import json
import urllib
headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    'Referer': "https://kyfw.12306.cn/otn/leftTicket/init"
}
url = "https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=2018-07-15&leftTicketDTO.from_station=NJH&leftTicketDTO.to_station=INH&purpose_codes=ADULT"
city_map_url = "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9059"
base_url = "https://kyfw.12306.cn/otn/leftTicket/query?"

def query_ticket():
    try:
        with open('./cityMap.json', 'r', encoding='utf-8') as f:
            city_map = json.load(f)

    except Exception as e:
        print('打开json文件错误(%s)' % e)

    if city_map:
        city_map_reverse = {v:k for k,v in city_map.items()}
        date = input('input query date(YYYY-MM-DD):\n')
        from_station = city_map.get(input('input from city:\n'))
        end_station = city_map.get(input('input to city:\n'))
        query_dict = {'leftTicketDTO.train_date': date,
                      'leftTicketDTO.from_station': from_station,
                      'leftTicketDTO.to_station': end_station,
                      'purpose_codes': 'ADULT'}
        query_url = base_url + urllib.parse.urlencode(query_dict)
        print(query_url)
        html = requests.get(query_url, headers=headers).text
        print(html)
        if from_station in html:
            ticket_info = json.loads(html).get('data').get('result')
            for i in ticket_info:
                train_info = i.split('|')
                print('车次:%s' % train_info[3])
                print('出发时间:%s' % train_info[8])
                print('到达时间:%s' % train_info[9])
                print('起始站:{0}||终点站:{1}'.format(city_map_reverse.get(train_info[4]), city_map_reverse.get(train_info[5])))
                print('一等座:{0}|二等座:{1}|无座:{2}|商务座:{3}'.format(train_info[31], train_info[30], train_info[26],train_info[32]))
                print("".center(30, '*'))


        else:
            print('获取失败....')

query_ticket()
# html = requests.get(url,headers=headers).text
# info = json.loads(html)
# result = info['data']['result']
# print(result)
# for i in result[0:1]:
#     for j in i.split('|'):
#         print(j)
def get_city_map(map_url):
    html = requests.get(map_url, headers=headers)
    map_dict = dict()
    if html.status_code == 200:
        map_info = html.text.split('=')[1]
    for i in map_info.split('@')[1:]:
        city = i.split('|')
        map_dict[city[1]] = city[2]
    try:
        with open('cityMap.json','w',encoding='utf-8') as f:
            json.dump(map_dict, f, ensure_ascii=False)
    except Exception as e:
        print('写入json文件出错(%s)' % e)
