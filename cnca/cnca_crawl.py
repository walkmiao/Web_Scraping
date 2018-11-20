#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : cnca.py
# @Author: lch
# @Date  : 2018/11/16
# @Desc  :

from interface_chaojiying import Chaojiying
from interface_baidu import BaiduAip
from config import *
import requests
import json

class CNCA(object):
    def __init__(self):
        """
        初始化注册信息
        :param code: 验证码
        """
        self.url = URL  # 目标站点
        self.s = requests.session()
        self.chaojiying = Chaojiying(USERNAME, PASSWORD, SOFT_ID)  # 创建超级鹰对象

    def get_captcha(self):
        captcha = self.s.get(CAPTCHA_URL, headers=headers).content
        with open('captcha.png', 'wb') as f:
            f.write(captcha)
        return captcha

    def post(self, org_name,check_code):
        data = {
            'orgName': org_name,
            'certNumber': '',
            'certItemOne': '',
            'certItemTwo': '',
            'certItemThree': '',
            'checkCode': check_code,
            'queryType': 'public',
            'certStatus': '01',
            'country': 156}

        res = self.s.post(POST_URL, data=data, headers=headers).text
        res = json.loads(res)
        org_name_list = [d.get('orgName') for d in res.get('data')]
        return org_name_list

    def cert_post(self, org_list, check_code):
        if len(org_list)>0:
            for org_name in org_list:
                data = {
                    'orgName': org_name,
                    'randomCheckCode': check_code,
                    'queryType': 'public'
                }
                result = self.s.post(url=CERT_URL, data=data, headers=headers).text
                result = json.loads(result)
                for row in result.get('rows'):
                    print('certNumber:{} orgName:{} rziGid:{} rziGidName:{}'
                          .format(row.get('certNumber'), row.get('orgName'), row.get('rzjgId'), row.get('rzjgIdName')))
        else:
            pass

    def parse_image(self, num_result):
        if len(num_result) > 3:

            a = Cal_dict.get(num_result[0])
            b = Cal_dict.get(num_result[2])
            symbol = num_result[1]
            if symbol == '一':
                return a-b
            elif symbol =='x':
                return a*b
            elif symbol =='十':
                return a+b
            else:
                return a/b


if __name__ == '__main__':
    org_name = input("请输入查询结构:")
    cnca = CNCA()
    image = cnca.get_captcha()
    bd = BaiduAip()
    num_result = bd.get_result(image)
    check_code = cnca.parse_image(num_result)
    print(check_code)
    # json_result = cnca.chaojiying.PostPic(image, codetype=CHAOYING_KIND)
    # check_code = json_result.get('pic_str')
    # print(check_code)
    if check_code != None:
        org_list = cnca.post(org_name, int(check_code))
        cnca.cert_post(org_list, check_code)
