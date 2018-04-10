# -*- coding: utf-8 -*-
"""最早資料為2004/3/31
"""
from __future__ import unicode_literals, print_function
from crawler.base import TwseCrawlerDaily
from util import str_to_int, proxy, str_to_float, RetryException, HolidayException
import requests
import csv
import re


class BFI82U(TwseCrawlerDaily):
    name = 'BFI82U'
    url = 'http://www.twse.com.tw/fund/BFI82U?response=json&dayDate={:04}{:02}{:02}&_={}'

    def __init__(self):
        super(BFI82U, self).__init__()

    def _download_one_day(self, day):
        """輸入一個date或datetime物件，下載物件指定的日期的資訊。
        """
        try:
            self.get_json(day, name_field='fields', value_field='data')
        except HolidayException:
            return {'_id': self.date_to_datetime(day), 'TradingDay': False}

        data = dict()
        data['_id'] = self.date_to_datetime(day)
        data['TradingDay'] = True
        for row in self.js['data']:
            item_name = row[0].replace(')', '').replace('(', '_')
            if row[0] == '合計':
                continue
            for name, value in zip(self.js['fields'][1:], row[1:]):
                data[item_name + '_' + name] = str_to_int(value)
        return data
