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
from movie_paradise.config import start_url, headers, prefix, crawled_set, movie_kind_list, country_list
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
    def __init__(self, q, sql_ins):
        super(CrawInfo, self).__init__()
        self.q = q
        self.sql_ins = sql_ins

    def run(self):
        crawl_movie_info(self.q, self.sql_ins)


class SqlInit:
    def __init__(self, db, table, insert_count):
        self.db = db
        self.table = table
        self.insert_count = insert_count
        try:
            conn = sqlite3.connect(self.db, check_same_thread=False)
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
                                    KIND           TEXT    NOT NULL,
                                    PUBLISH_DATE   TEXT            ,
                                    COUNTRY         TEXT           ,
                                    SCORE           FLOAT 
                                   );'''.format(table=self.table))
                logger.info("[SUCCESS]Table {} created successfully".format(self.table))
            except Exception as e:
                logger.info('[FAIL]创建表{}错误:[{}]'.format(self.table, e))

    def sql_insert(self, data):
            # sql_expression = '''INSERT INTO {table} (INFO, LINK, KIND, PUBLISH_DATE, COUNTRY)
            #                     VALUES ('{info}', '{link}', '{kind}', '{publish}', '{country}')
            #                     '''.format(table=self.table, info=info,
            #                                link=link, kind=kind, publish=publish, country=country)
            sql_expression = '''INSERT INTO {table} (INFO, FTP_LINK, MAGNET_LINK,  KIND, PUBLISH_DATE, COUNTRY, SCORE) 
                                           VALUES (?, ?, ?, ?, ?, ?, ?)
                                           '''.format(table=self.table)
            try:

                self.conn.executemany(sql_expression, data)
                self.insert_count += 50
                print('[{}]插入50行成功，当前行[{}]'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.insert_count))
                self.conn.commit()
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
    try_count = 1
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


def crawl_index():
    '''
    爬取首页，获取首页分类url
    :return:
    '''
    html, res_url = get_res(start_url)
    sel = etree.HTML(html)
    m_dict = dict()
    for seq, i in enumerate(sel.xpath("//div[@class='contain']/ul//li")[:-4]):
        class_name = i.xpath(".//a/text()")[0] if i.xpath(".//a/text()") else None
        class_link = prefix + i.xpath(".//a/@href")[0] if i.xpath(".//a/@href") else None
        if class_link and class_name:
            m_dict[class_name] = class_link
    return m_dict


def crawl_kinds(name, url, q, crawl_num=0):
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
            link = prefix + link
            q.put(link)
            logger.debug("向Queue中放入[{}]:{}".format(movie_info, link))
    next_link = sel.xpath("//a[contains(text(),'下一页')]/@href")
    if next_link:
        next_link = prefix + sel.xpath("//a[contains(text(),'下一页')]/@href")[0]
        # logger.debug("获取到next_link:%s" % next_link)
        # logger.info("开始爬取地址:{}".format(next_link))
        crawl_kinds(name, next_link, q, crawl_num)
    else:
        logger.info("{}分类已经爬取完毕，共{}条  最后URL:{}".format(name, crawl_num, cache_url))


# def write_err(err, path="./error.txt"):
#     current = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
#     with open(path,mode='w') as f:
#         f.write(str(current)+ ':'


def crawl_movie_info(q, sql_ins):
    '''
    :param q: queue
    :param conn: sqlite连接
    :return:
    '''
    data_list = []
    while True:
        url = q.get()
        q.task_done()
        if not url:
            print('已经结束了')
            break
        if url not in crawled_set:
            logging.debug("从QUEUE取出URL:{}".format(url))
            result = get_res(url)
            crawled_set.add(url)
            if result:
                html, res_url = get_res(url)
            else:
                continue
            ftp_link = list()
            magnet_link = list()
            try:
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
                kind = '其他'
                country = '其他'
                for k in movie_kind_list:
                    if k in movie_info:
                        kind = k
                        break
                for c in country_list:
                    if c in movie_info:
                        country = c
                        break
                    if '欧美' in movie_info:
                        country = '欧美'
                data_list.append((movie_info, ftp_link, magnet_link, kind, publish_date, country, score))
                if len(data_list) == 50:
                    mutex.acquire()
                    sql_ins.sql_insert(data_list)
                    data_list = []
                    mutex.release()
            except Exception as e:
                logger.info("获取不到此URL:{}下载地址[{}]".format(url, e))
                continue


def main():
    global mutex
    mutex = Lock()
    global insert_count
    insert_count = 0
    sql_ins = SqlInit('movie.db', 'movie_info', insert_count)
    sql_ins.create_table()
    m_dict = crawl_index()
    work_list = []
    queue_list = []
    for kind, url in m_dict.items():
        q = Queue()
        queue_list.append(q)
        work = CrawlKind(name=kind, url=url, q=q)
        work_info = CrawInfo(q, sql_ins)
        work_list.append(work)
        work_list.append(work_info)
    for work in work_list:
        work.setDaemon(True)
        work.start()
    for work in work_list:
        work.join()
    for q in queue_list:
        q.put(None)
    for q in queue_list:
        q.join()
    sql_ins.conn.close()
    print("[END] ALL DATA({} items) INSERT SUCCESS!")


if __name__ == "__main__":
    main()
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



