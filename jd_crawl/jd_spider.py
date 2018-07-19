#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/13 11:58
# @Author  : LCH
# @Site    : 
# @File    : jd_spider.py
# @Software: PyCharm
import requests
from fake_useragent import UserAgent
import time
from lxml import etree
ua = UserAgent()
class JD_spider():
    def __init__(self, username, password):
        self.headers = {'User-Agent': ua.random,
                        'Referer': 'https://www.jd.com/'
        }
        self.login_url = "https://passport.jd.com/new/login.aspx"
        self.post_url = "https://passport.jd.com/uc/loginService"
        self.auth_url = "https://passport.jd.com/uc/showAuthCode"
        self.username = username
        self.password = password

def get_login_info(self):
    html = self.session.get(self.login_url, headers=self.headers).text
    html = etree.HTML(html)
    uuid = html.xpath("//div[@class='form']//input")