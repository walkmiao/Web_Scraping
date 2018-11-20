#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : config.py
# @Author: lch
# @Date  : 2018/11/16
# @Desc  :
import time

USERNAME = 'lichunhui'
PASSWORD = 'fU8C89uk7R5vDim'
EMAIL = '372815340@QQ.COM'
SOFT_ID= 96001
CHAOYING_KIND = 6003
POST_URL = 'http://cx.cnca.cn/rjwcx/cxAuthenticationResult/queryOrg.do?progId=10'
CERT_URL = "http://cx.cnca.cn/rjwcx/cxAuthenticationResult/queryCertByOrg.do?progId=10"
URL = 'http://cx.cnca.cn/'
now_time = lambda:int(round(time.time() * 1000))
CAPTCHA_URL = 'http://cx.cnca.cn/rjwcx/checkCode/rand.do?d={}'.format(now_time())
headers = {
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"
}


# 以下是百度接口的信息
APP_ID = '14870988'
API_KEY = 'lEYEuqtQzDWqvfYGBCXitIc7'
SECRET_KEY = 'IwwiN6DzdfCXvtCV4jn6plnVfo7AMwy3'

Cal_dict = {'玖':9,'捌':8, '柒':7, '陆':6, '肆':4, '叁':3, '贰':2, '壹':1, '零':0}


