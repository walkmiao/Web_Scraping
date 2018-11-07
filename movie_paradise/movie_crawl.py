#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : movie_crawl.py
# @Author: lch
# @Date  : 2018/10/15
# @Desc  :
from lxml import etree
from threading import Thread, Lock
from queue import Queue
import requests
from ftplib import FTP
import os
import re
import sqlite3
import logging
from movie_paradise.config import start_url, headers, prefix, crawled_set,  country_list, mutex, all_count
from movie_paradise.logger import logger
import datetime


class CrawlKind(Thread):
    def __init__(self, name, url, q):
        super(CrawlKind, self).__init__(name=name)
        self.url = url
        self.q = q
        self.name = name

    def run(self):
        logger.info("THREAD{}启动了" .format(self.getName()))
        crawl_kinds(self.name, self.url, self.q)


class CrawInfo(Thread):
    def __init__(self, kind, q, sql_ins):
        super(CrawInfo, self).__init__()
        self.kind = kind
        self.q = q
        self.sql_ins = sql_ins

    def run(self):
        crawl_movie_info(self.kind, self.q, self.sql_ins)


class SqlInit:
    def __init__(self, db, table, all_count):
        self.db = db
        self.table = table
        self.all_count = all_count
        try:
            conn = sqlite3.connect(self.db, check_same_thread=False)
            conn.execute("PRAGMA synchronous = OFF")  # 关闭磁盘同步
            conn.execute("BEGIN TRANSACTION")  # 开始事务处理
            logger.info("[SUCCESS]数据库{}创建完毕".format(db))
            self.conn = conn
        except Exception as e:
            logger.info('[FAIL]数据库创建错误:[{}]'.format(e))

    def create_table(self):
        with self.conn:
            try:
                self.conn.execute('''CREATE TABLE {table}
                                   (ID INTEGER PRIMARY KEY     AUTOINCREMENT ,
                                    INSERT_TIME   TIMESTAMP   DEFAULT (datetime('now', 'localtime')), 
                                    INFO           TEXT    NOT NULL,
                                    FTP_LINK           TEXT    NOT NULL,
                                    MAGNET_LINK           TEXT    NOT NULL,
                                    URL     TEXT NOT NULL,
                                    KIND           TEXT    NOT NULL,
                                    PUBLISH_DATE   TEXT            ,
                                    COUNTRY         TEXT           ,
                                    SCORE           FLOAT 
                                   );'''.format(table=self.table))
                logger.info("[SUCCESS]Table {} created successfully".format(self.table))
            except Exception as e:
                logger.info('[FAIL]创建表{}错误:[{}]'.format(self.table, e))

    def sql_insert(self, data,  name):
            # sql_expression = '''INSERT INTO {table} (INFO, LINK, KIND, PUBLISH_DATE, COUNTRY)
            #                     VALUES ('{info}', '{link}', '{kind}', '{publish}', '{country}')
            #                     '''.format(table=self.table, info=info,
            #                                link=link, kind=kind, publish=publish, country=country)
            insert_sql_expression = '''INSERT INTO {table} (INFO, FTP_LINK, MAGNET_LINK, URL, KIND, PUBLISH_DATE, COUNTRY, SCORE) 
                                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                           '''.format(table=self.table)
            query_sql_expression = '''SELECT * FROM {table} 
                                            WHERE INFO = '{info}'  
                                        '''.format(table=self.table, info=data[0])
            try:
                if len(self.conn.execute(query_sql_expression).fetchall()) < 1:
                    self.conn.execute(insert_sql_expression, data)
                    self.all_count += 1
                    # print('[{}]插入{}行[分类:{}]成功，当前分类行[{}]'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    #       1, name, self.all_count))
                    print('插入分类{} info:[{}] 成功 当前行{}'.format(name, data[0], self.all_count))
                    self.conn.commit()
                else:
                    print('[{}]已存在'.format(data[0]))
            except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
                logger.info('[FAIL]插入数据库失败 SQL:{}'.format(e))

    def sql_query(self, name):
        try:
            with self.conn:
                query_sql = '''SELECT * FROM {table} 
                                WHERE INFO LIKE '%{name}%'  
                            '''.format(table=self.table, name=name)
                query_result = self.conn.execute(query_sql).fetchall()
                print('[SUCCESS]查询关键字[{}]成功,共查询到{}条结果'.format(name, len(query_result)))
                return query_result
        except sqlite3.OperationalError as e:
            print('[FAIL]数据库查询错误:[{}]'.format(e))


class FtpDownload:
    def __init__(self, host, username, password, port):
        """
        初始化ftp
        :param host: ftp主机ip
        :param username: ftp用户名
        :param password: ftp密码
        :param port:  ftp端口 （默认21）
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port

    def ftp_connect(self):
        """
        连接ftp
        :return:
        """
        ftp = FTP()
        ftp.set_debuglevel(0)  # 不开启调试模式
        ftp.connect(host=self.host, port=self.port)  # 连接ftp
        ftp.login(self.username, self.password)  # 登录ftp
        return ftp

    def download_file(self, dst_file_path, ftp_file_path):
        """
        从ftp下载文件到本地
        :param ftp_file_path: ftp下载文件路径
        :param dst_file_path: 本地存放路径
        :return:
        """
        buffer_size = 10240  #默认是8192
        ftp = self.ftp_connect()
        logging.debug(ftp.getwelcome()) #显示登录ftp信息
        write_file = os.path.join(dst_file_path, ftp_file_path)
        print(ftp.pwd())
        with open(write_file, "wb") as f:
            logging.debug("正在下载{}..".format(ftp_file_path))
            ftp.retrbinary('RETR {0}'.format(ftp_file_path.encode('utf-8').decode('latin1')), f.write, buffer_size)
        f.close()


def get_res(url, times=5):
    try_count = 0
    while times > 0:
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                res_url = res.url
                crawled_set.add(res_url)
                res.encoding = 'gb2312'
                html = res.text
                return html, res_url
            else:
                times = times - 1
                try_count += 1
                logger.info('爬取 url:{} error！将进行{}次尝试'.format(url, try_count))
        except Exception as e:
            logger.error('[REQUEST ERROR]:[{}]'.format(e))
    return


def crawl_index(url):
    '''
    爬取首页，获取首页分类url
    :return:
    '''
    html, res_url = get_res(url)
    sel = etree.HTML(html)
    m_dict = dict()
    exract_url = prefix + sel.xpath("//div[@class='contain']/ul//li")[1].xpath(".//a/@href")[0] # 随便获取一个分类的URL这里是动作片
    html_kind = get_res(exract_url)[0]
    sel_kind = etree.HTML(html_kind)
    for i in sel.xpath("//div[@class='contain']/ul//li")[:-4]:
        class_name = i.xpath(".//a/text()")[0] if i.xpath(".//a/text()") else None
        class_link = prefix + i.xpath(".//a/@href")[0] if i.xpath(".//a/@href") else None
        if class_link and class_name:
            m_dict[class_name] = class_link

    for i in sel_kind.xpath("//div[@class='co_content2']/ul//table[@width]")[1:]:
        class_name = i.xpath(".//a/text()")[0]
        class_link = prefix + i.xpath(".//a/@href")[0]
        if class_link and class_name:
            m_dict[class_name] = class_link
    temp_dict = {}
    for k, v in m_dict.items():
        html = get_res(v)[0]
        count = re.findall(r'.*总数(\d+).*', html)[0]
        temp_dict[k] = int(count)
    return m_dict, temp_dict


def crawl_kinds(name, url, q, crawl_num=0, link_num=0):
    '''
    分类解析，遇到下一页解析并继续爬取
    :param url: 分类url
    :param q: queue
    :return:
    '''
    html, res_url = get_res(url)
    cache_url = res_url
    crawl_num += 1
    sel = etree.HTML(html)
    movie_items = sel.xpath("//table[@class='tbspan']")
    for i in movie_items:
        a_mark = i.xpath(".//a[contains(@href,'.html')]")[0]
        movie_info = a_mark.xpath("./text()")[0] if a_mark.xpath("./text()") else a_mark.xpath("./@title")[0]
        link = a_mark.xpath("./@href")[0]
        if link:
            link_num += 1
            link = prefix + link
            # logger.info("获取到分类[{}]连接 link序号:{} link:{}".format(name, link_num, link))
            q.put(link)
            # logger.debug("向Queue中放入[{}]:{}".format(movie_info, link))

    next_link = sel.xpath("//a[contains(text(),'下一页')]/@href")
    if next_link:
        next_link = prefix + sel.xpath("//a[contains(text(),'下一页')]/@href")[0]
        # logger.info("获取到分类[{}]next_link:{}".format(name, next_link))
        # logger.info("开始爬取地址:{}".format(next_link))
        crawl_kinds(name, next_link, q, crawl_num, link_num)
    else:
        logger.info("{}分类已经爬取完毕，共{}条 总数：{}  最后URL:{}".format(name, crawl_num,link_num,cache_url))
        return


# def write_err(err, path="./error.txt"):
#     current = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
#     with open(path,mode='w') as f:
#         f.write(str(current)+ ':'


def crawl_movie_info(name, q, sql_ins):
    '''
    :param q: queue
    :param conn: sqlite连接
    :return:
    '''
    err_count = 0
    crawled_count = 0
    insert_count = 0
    repeat_url_count = 0
    while True:
        try:
            url = q.get(block=True, timeout=100)
        except Exception:
            logger.info('当前分类[{}] 总数：{} 插入总数：{}出错条数:{} 重复URL条数：{} 已爬取的URL： {} '
                        .format(name, kind_num_dict[name], insert_count,err_count,repeat_url_count,crawled_count))
            break
        if url not in crawled_set:
                crawled_count += 1
                crawled_set.add(url)
                try:
                    result = get_res(url)
                    html, res_url = result
                    ftp_link = list()
                    magnet_link = list()
                    sel = etree.HTML(html)
                    for i in sel.xpath("//div[@id='Zoom']//table"):
                        link = i.xpath(".//a/@href")[0] if i.xpath(".//a/@href") else "暂缺"  # 电影只有一个连接，电视则有多条连接
                        if 'ftp' in link:
                            ftp_link.append(link)
                        else:
                            magnet_link.append(link)
                    ftp_link = '||'.join(ftp_link)
                    magnet_link = '||'.join(magnet_link)
                    movie_info = sel.xpath("//div[@class='title_all']//h1/text()")[0] \
                        if sel.xpath("//div[@class='title_all']//h1/text()") else "资源信息未解析出"
                    publish_date = re.findall(r'.*发布时间.*(\d{4}\-\d{2}\-\d{2}).*', html)[0] \
                        if re.findall(r'.*发布时间.*(\d{4}\-\d{2}\-\d{2}).*', html) else '未知时间'
                    score = re.findall(r'.*(\d\.\d).*', movie_info)[0] if re.findall(r'.*(\d\.\d).*', movie_info) else None
                    country = '其他'
                    for c in country_list:
                        if c in movie_info:
                            country = c
                    # data_list.append((movie_info, ftp_link, magnet_link, name, publish_date, country, score))
                    data = (movie_info, ftp_link, magnet_link, url, name, publish_date, country, score)
                except Exception as e:
                    logger.info("[ERROR]CAUSE BY [{}] URL:{}".format(e, url))
                    err_count += 1
                    continue

                mutex.acquire()
                sql_ins.sql_insert(data, name)
                mutex.release()
                insert_count += 1

        else:
            repeat_url_count += 1


def main():
    global kind_num_dict
    m_dict, kind_num_dict = crawl_index(start_url)
    sql_ins = SqlInit('movie.db', 'movie_info', all_count)
    sql_ins.create_table()
    work_list = []
    queue_list = []
    for kind, url in m_dict.items():
        q = Queue()
        queue_list.append(q)
        work = CrawlKind(name=kind, url=url, q=q)
        work_info = CrawInfo(kind, q, sql_ins)
        work_list.append(work)
        work_list.append(work_info)
    for work in work_list:
        work.start()

    for work in work_list:
        work.join()

    sql_ins.conn.close()
    logger.info("[END] ALL DATA items INSERT SUCCESS! ITEMS:{}".format(sql_ins.all_count))


if __name__ == "__main__":
    main()
    # url="https://www.dy2018.com/"
    # crawl_index(url)
    # url = "http://www.ygdy8.net/html/tv/hytv/20170404/53606.html"
    # crawl_movie_info(url)
    # q = Queue()
    # url = "http://www.ygdy8.net/html/gndy/china/index.html"
    # crawl_kinds(url,q)
    # q = Queue()
    # # m_dict = crawl_index()
    # kind_url = "http://www.ygdy8.net//html/gndy/dyzz/list_23_1.html"
    # # url = "http://www.ygdy8.net/html/tv/hytv/20180926/57500.html"
    # # conn = SqlInit('movie.db', 'movie_info')
    # # # # conn.create_table()
    # # # movie_info, link_string = crawl_movie_info(url)
    # # # conn.sql_insert(movie_info, link_string)
    # # result = conn.sql_query("生")
    # # print(result)
    # print(crawl_index())
    # crawl_kinds(kind_url, q)


    '''
    ftp下载部分
    '''
    # query_dict = dict()
    # for item in result:
    #     movie_name, link_string = item
    #     link_list = link_string.split(' ')
    #     query_dict[movie_name] = link_list
    # a= query_dict.popitem()
    # if a:
    #     list_link = a[1][30]
    #     print(list_link)
    #     if 'ftp' in list_link:
    #         reg = re.compile(r'ftp://(\w+):(\w+)@(\w+.\w+.\w+):(\w+)/(.*)')
    #
    #         ftp_info = re.findall(reg, list_link)[0]
    #         print(ftp_info)
    #         username, password, host, port, filename = ftp_info
    #         ftp_obj = FtpDownload(host, username, password, int(port))
    #         ftp_obj.download_file('.', filename)



