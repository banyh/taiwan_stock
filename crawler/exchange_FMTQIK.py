# -*- coding: utf-8 -*-
"""最早資料為1990/01/04
"""
from __future__ import unicode_literals, print_function
from crawler.base import TwseCrawlerDaily
from util import str_to_int, str_to_float, proxy
import requests
import csv
import re


class FMTQIK(TwseCrawlerDaily):
    name = 'FMTQIK'
    url = 'http://www.tse.com.tw/exchangeReport/FMTQIK?response=json&date={:04}{:02}{:02}&_={}'

    def __init__(self):
        super(FMTQIK, self).__init__()
        self.cache = dict()

    def _download_one_day(self, day):
        """輸入一個date或datetime物件，下載物件指定的日期的資訊。
        """
        date_key = '{:04d}{:02d}'.format(day.year, day.month)
        if date_key in self.cache:
            js = self.cache[date_key]
        else:
            print('cache miss', date_key)
            ts = self.timestamp()
            self.cache[date_key] = js = proxy.get(self.url.format(day.year, day.month, 1, ts)).json()
        if 'data' not in js:
            return {'_id': self.date_to_datetime(day), 'TradingDay': False}
        found = [item for item in js['data']
                 if item[0] == '{:3d}/{:02d}/{:02d}'.format(day.year - 1911, day.month, day.day)]
        if not found:
            return {'_id': self.date_to_datetime(day), 'TradingDay': False}
        item = found[0]

        data = dict()
        data['_id'] = self.date_to_datetime(day)
        data['TradingDay'] = True
        data['成交股數'] = str_to_int(item[1])
        data['成交金額'] = str_to_int(item[2])
        data['成交筆數'] = str_to_int(item[3])
        data['發行量加權股價指數'] = str_to_float(item[4])
        data['漲跌點數'] = str_to_float(item[5])
        if data['成交筆數'] == 0:
            data['平均每筆金額'] = 0.0
            data['平均每筆股數'] = 0.0
        else:
            n_trans = float(data['成交筆數'])
            data['平均每筆金額'] = data['成交金額'] / n_trans
            data['平均每筆股數'] = data['成交股數'] / n_trans
        return data
