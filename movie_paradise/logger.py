#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : logger.py
# @Author: lch
# @Date  : 2018/10/19
# @Desc  :
import logging


class Logger:
    def __init__(self, path, clevel=logging.DEBUG, Flevel=logging.INFO):
        #设置创建日志的对象
        self.logger = logging.getLogger(path)
        #设置日志的最低级别低于这个级别将不会在屏幕输出，也不会保存到log文件
        self.logger.setLevel(logging.DEBUG)
        #给这个handler选择一个格式（）
        fmt = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
        # 设置终端日志 像终端输出的日志
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)#设置个终端日志的格式
        sh.setLevel(clevel)#设置终端日志最低等级
        # 设置文件日志 用于向一个文件输出日志信息。不过FileHandler会帮你打开这个文件。
        fh = logging.FileHandler(path, encoding='utf-8')
        fh.setFormatter(fmt)#设置个文件日志的格式
        fh.setLevel(Flevel)#设置终端日志最低等级
        self.logger.addHandler(sh)#增加终端日志Handler
        self.logger.addHandler(fh)#增加文件日志Handler

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warn(self, message):
        self.logger.warn(message)

    def error(self, message):
        self.logger.error(message)

    def crit(self, message):
        self.logger.critical(message)


logger = Logger('./CrawlInfo.log')
