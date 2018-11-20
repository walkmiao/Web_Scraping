#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : baidu.py
# @Author: lch
# @Date  : 2018/11/20
# @Desc  :
from aip import AipOcr
from config import *
import json


class BaiduAip:
    def __init__(self):
        self.APP_ID = APP_ID
        self.API_KEY = API_KEY
        self.SECRET_KEY = SECRET_KEY
        self.client = AipOcr(self.APP_ID, self.API_KEY, self.SECRET_KEY)

    def get_file_content(self, file_path):
        with open(file_path, 'rb') as fp:
            return fp.read()

    def get_result(self, image=None):
        result = self.client.basicGeneral(image)
        # result = json.loads(result)
        return result.get('words_result')[0].get('words')


if __name__ == '__main__':
    bd = BaiduAip()
    bd.get_result()





