#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/15 13:41
# @Author  : LCH
# @Site    : 
# @File    : tk12306.py
# @Software: PyCharm
from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import json
import requests
import urllib
import re
import os
import time
from threading import Thread

city_map_url = "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9059"
base_url = "https://kyfw.12306.cn/otn/leftTicket/query?"
headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        'Referer': "https://kyfw.12306.cn/otn/leftTicket/init"
    }
train_no_url = "https://kyfw.12306.cn/otn/czxx/queryByTrainNo?"
ticket_price_url = "https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice?"


class TicketQuery:
        @staticmethod
        def get_city_map(map_url=city_map_url):
            html = requests.get(map_url, headers=headers)
            map_dict = dict()
            if html.status_code == 200:
                map_info = html.text.split('=')[1]
                for i in map_info.split('@')[1:]:
                    city = i.split('|')
                    map_dict[city[1]] = city[2]
                try:
                    with open('cityMap.json', 'w', encoding='utf-8') as f:
                        json.dump(map_dict, f, ensure_ascii=False)
                except Exception as e:
                    print('写入json文件出错(%s)' % e)
            else:
                print('获取城市MAP出错,status_code(%s)' % html.status_code)

        @staticmethod
        def query_ticket(query_date, from_city, to_city):
            city_map = GuiInit.map_dict
            log_info = list()
            train_info = dict()

            if city_map:
                city_map_reverse = GuiInit.map_dict_reverse
                from_station = city_map.get(from_city)
                end_station = city_map.get(to_city)
                query_dict = {'leftTicketDTO.train_date': query_date,
                              'leftTicketDTO.from_station': from_station,
                              'leftTicketDTO.to_station': end_station,
                              'purpose_codes': 'ADULT'}
                query_url = base_url + urllib.parse.urlencode(query_dict)
                log_info.append('%s--查询url:%s\n' %(time.ctime(), query_url))
                html = requests.get(query_url, headers=headers).text
                if 'result' in html:
                    ticket_info = json.loads(html).get('data').get('result')
                    for j, i in enumerate(ticket_info, 1):
                        info = i.split('|')
                        train_dict = {
                            'train_no': info[2], '出发站': city_map_reverse.get(info[6]),
                            '到达站': city_map_reverse.get(info[7]), '列车状态': info[1],
                            '车次': info[3], '出发时间':info[8], '到达时间': info[9],
                            '耗时': info[10], '一等座':info[31],
                            '二等座': info[30], '无座':info[26], '商务座': info[32], '硬座': info[29],
                            '软卧': info[23], '硬卧': info[28], '列车类型': info[-2]

                        }
                        train_info.setdefault(j, train_dict)

                else:
                    log_info.append('获取12306 json文件失败,请检查URL....\n')
            return train_info, log_info


class GuiInit:
    map_dict = dict()
    map_dict_reverse = dict()

    def __init__(self, my_window, title, window_size='750x600+10+10'):
        if not os.path.exists('./cityMap.json'):
            TicketQuery().get_city_map(city_map_url)

        with open('./cityMap.json', 'r', encoding='utf-8') as f:
            GuiInit.map_dict = json.load(f)
            GuiInit.map_dict_reverse = {v: k for k, v in GuiInit.map_dict.items()}
        # gui 初始化
        self.my_window = my_window
        self.my_window.title(title)
        self.my_window.geometry(window_size)
        # 出发城市label
        self.init_data_label = Label(self.my_window, width=10, text="出发城市").grid(row=0, column=0, sticky='NW')
        # 到达城市label
        self.result_data_label = Label(self.my_window, text="到达城市").grid(row=0, column=2, sticky='NW')
        # 日期选择
        self.date_label = Label(self.my_window, text="日期选择").grid(row=0, column=4)
        # 查询按钮
        self.query_button = Button(self.my_window, text="车次查询", bg="lightblue", width=10,
                                   command=self.query_thread).grid(row=0, column=6)
        # 树表格
        self.tree = ttk.Treeview(self.my_window, show="headings", height=10, columns=list(range(0, 16)),
                                 displaycolumns=list(range(1, 15)))
        self.vbar = ttk.Scrollbar(self.my_window, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.vbar.set)
        for i in range(16):
            if i==1 or i==2:
                self.tree.column(str(i), width=60, anchor="center")
            else:
                self.tree.column(str(i), width=50, anchor="center")

        self.tree.heading("0", text="Train_No")
        self.tree.heading("1", text="出发站")
        self.tree.heading("2", text="到达站")
        self.tree.heading("3", text="列车状态")
        self.tree.heading("4", text="车次")
        self.tree.heading("5", text="出发时间")
        self.tree.heading("6", text="到达时间")
        self.tree.heading("7", text="耗时")
        self.tree.heading("8", text="一等座")
        self.tree.heading("9", text="二等座")
        self.tree.heading("10", text="无座")
        self.tree.heading("11", text="商务座")
        self.tree.heading("12", text="硬座")
        self.tree.heading("13", text="软卧")
        self.tree.heading("14", text="硬卧")
        self.tree.heading("15", text="列车类型")
        self.tree.bind("<<TreeviewSelect>>", self.show_station)  # 事件(选中)绑定
        self.tree.grid(row=2, column=0, columnspan=7, sticky='NW')
        self.vbar.grid(row=2, column=7, columnspan=1, sticky='NSW')

        # 车次站台信息树表格
        self.station_tree = ttk.Treeview(self.my_window, show="headings", height=10,  columns=list(range(0, 5)))
        self.station_bar = ttk.Scrollbar(self.my_window, orient=VERTICAL, command=self.station_tree.yview)
        self.station_tree.configure(yscrollcommand=self.station_bar.set)
        self.station_tree.column("0", width=80, anchor="center")
        self.station_tree.column("1", width=80, anchor="center")
        self.station_tree.column("2", width=80, anchor="center")
        self.station_tree.column("3", width=80, anchor="center")
        self.station_tree.column("4", width=80, anchor="center")

        self.station_tree.heading("0", text="站序")
        self.station_tree.heading("1", text="站名")
        self.station_tree.heading("2", text="到站时间")
        self.station_tree.heading("3", text="出发时间")
        self.station_tree.heading("4", text="停留时间")

        self.station_tree.grid(row=3, column=0, columnspan=3, sticky='NW')
        self.station_bar.grid(row=3, column=3, columnspan=1, sticky='NSW')
        # 票价显示文本区域
        self.price_Text = Text(self.my_window, width=43, height=17)
        self.price_Text.grid(row=3, column=3, columnspan=4, sticky='NE')
        self.log_label = Label(self.my_window, text="日志", bg="lightblue").grid(row=25, column=0, sticky='W')
        # 日志显示文本区域
        self.log_data_Text = Text(self.my_window, width=100, height=9)
        self.log_data_Text.grid(row=60, column=0, columnspan=15)
        # 出发城市下拉列
        from_name = tk.StringVar()
        self.from_city_list = ttk.Combobox(self.my_window, width=10, textvariable=from_name)
        self.from_city_list.grid(row=0, column=1, sticky='NW')
        self.from_city_list['values'] = list(GuiInit.map_dict.keys())
        # 到达城市下拉列
        to_name = tk.StringVar()
        self.to_city_list = ttk.Combobox(self.my_window, width=10, textvariable=to_name)
        self.to_city_list.grid(row=0, column=3)
        self.to_city_list['values'] = list(GuiInit.map_dict.keys())
        # tkinter没有专门的日期控件,用此方式获取顺延二十天日期
        date_name = tk.StringVar()
        self.date_list = ttk.Combobox(self.my_window, width=10, textvariable=date_name)
        self.date_list.grid(row=0, column=5)
        self.date_list['values'] = [(datetime.datetime.now()+datetime.timedelta(days=i))
                                    .strftime("%Y-%m-%d") for i in range(0, 21)]
        # 复选框最短时间
        self.is_short = tk.BooleanVar()
        self.check_short = Checkbutton(self.my_window, text='最短时间', variable=self.is_short,
                                       command=self.query_thread).grid(row=1, column=0, sticky='NW')
        # 复选框是否高铁动车
        self.is_GD = tk.BooleanVar()
        self.check_style = Checkbutton(self.my_window, text='动车高铁', variable=self.is_GD,
                                       command=self.query_thread).grid(row=1, column=1, sticky='NW')

    # 显示每站信息
    def show_station(self, event):
        self.station_tree.delete(*self.station_tree.get_children())
        select = event.widget.selection()[0]
        my_value = self.tree.item(select)['values']
        # 启用多线程 暂不会卡顿
        t = Thread(target=self.get_all_station, args=(my_value, ), name='show_station')
        t.start()
        return

    def get_ticket_price(self, my_value, from_city_no, to_city_no):
        self.price_Text.delete(1.0, END)
        train_no = my_value[0]
        seat_types = my_value[-1]
        price_url_dict = {
            'train_no': train_no, 'from_station_no': from_city_no,
            'to_station_no': to_city_no, 'seat_types': seat_types,
            'train_date': self.date_list.get()
        }
        url = ticket_price_url + urllib.parse.urlencode(price_url_dict)
        html = requests.get(url, headers=headers).text
        station_info = json.loads(html).get('data')
        price_dict = {}
        keys = ['商务座', '一等座', '二等座', '无座', '硬座', '硬卧', '软卧']
        price_no = ['A9', 'M', 'O', 'WZ', 'A1', 'A3', 'A4']
        price_dict['车次'] = my_value[4]
        for i in range(len(keys)):
            price_dict.setdefault(keys[i], station_info.get(price_no[i], '无'))
        for k, v in price_dict.items():
            self.price_Text.insert(INSERT, k+':' + v + '\n')

    def get_all_station(self, my_value):
        train_no = my_value[0]
        from_city = GuiInit.map_dict.get(my_value[1])
        to_city = GuiInit.map_dict.get(my_value[2])
        depart_date = self.date_list.get()
        train_no_dict = {
            'train_no': train_no, 'from_station_telecode': from_city,
            'to_station_telecode': to_city, 'depart_date': depart_date
        }

        train_station_url = train_no_url + urllib.parse.urlencode(train_no_dict)
        html = requests.get(train_station_url, headers=headers, timeout=1).text
        station_info = json.loads(html, encoding='utf-8').get('data').get('data')
        from_city_no = ''
        to_city_no = ''
        for station in station_info:
            station_no = station['station_no']
            station_name = station['station_name']
            arrive_time = station['arrive_time']
            start_time = station['start_time']
            stopover_time = station['stopover_time']
            if not from_city_no and GuiInit.map_dict.get(station_name) == from_city:
                from_city_no = station_no
            if not to_city_no and GuiInit.map_dict.get(station_name) == to_city:
                to_city_no = station_no
            self.station_tree.insert('', 'end', values=(station_no,
                                                        station_name, arrive_time, start_time, stopover_time))

        self.get_ticket_price(my_value,from_city_no,to_city_no)
        return


    def query_thread(self):
        thread1 = Thread(target=self.ticket_query, args=())
        thread1.start()

    # 查票信息并插入到tree中
    def ticket_query(self):
        reg = re.compile(r'^(G|D)\d+', re.I)
        t_query = TicketQuery()
        train_info, log_info = t_query.query_ticket(self.date_list.get(),
                                                    self.from_city_list.get(),self.to_city_list.get())
        self.log_data_Text.delete(1.0, END)
        self.tree.delete(*self.tree.get_children())

        if train_info:
            train_list = [v for k, v in train_info.items()]
            gd_list = list(filter(lambda x: reg.match(x['车次']), train_list))
            gd_short_list = sorted(gd_list, key=lambda x: x['耗时'])
            short_list = sorted(train_list, key=lambda x: x['耗时'])
            if self.is_short.get() and self.is_GD.get():
                train_list = gd_short_list
            elif self.is_short.get() and not self.is_GD.get():
                train_list = short_list
            elif not self.is_short.get() and self.is_GD.get():
                train_list = gd_list
            else:
                pass

            for i in train_list:
                info = []
                for k, v in i.items():
                    info.append(v if v else '--')
                self.tree.insert('', 'end', values=info)

        else:
            self.log_data_Text.insert(1.0, '无此车次信息，请核实！')
        for i in log_info:
            self.log_data_Text.insert(1.0, i)

    def run(self):
        self.my_window.mainloop()


if __name__ == '__main__':
    init_window = Tk()
    my_gui = GuiInit(init_window, '火车票查询')
    my_gui.run()


