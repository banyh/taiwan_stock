# -*- coding: utf-8 -*-
"""最早資料為2004/2/11
"""
from __future__ import unicode_literals, print_function
from crawler.base import TwseCrawlerDaily
from util import str_to_int, proxy
import requests
import csv
import re


class MI_INDEX(TwseCrawlerDaily):
    name = 'MI_INDEX'
    url = 'http://www.tse.com.tw/exchangeReport/MI_INDEX?response=json&type=ALL&date={:04}{:02}{:02}&_={}'

    def __init__(self):
        super(MI_INDEX, self).__init__()

    def _download_one_day(self, day):
        """輸入一個date或datetime物件，下載物件指定的日期的資訊。
        """
        if self.isHoliday(day):
            return {'_id': self.date_to_datetime(day), 'TradingDay': False}

        ts = self.timestamp()
        self.day = day
        self.js = js = proxy.get(self.url.format(day.year, day.month, day.day, ts)).json()

        item = None
        for k in js.keys():
            if k.startswith('fields') and js[k][0] == '成交統計':
                item = js['data' + k.replace('fields', '')]
        if not item:
            return {'_id': self.date_to_datetime(day), 'TradingDay': False}

        data = dict()
        data['_id'] = self.date_to_datetime(day)
        data['TradingDay'] = True
        for row in item[:12]:
            item_name = '成交統計_' + re.sub(r'\(.*\)', '', row[0]).replace('.', '_')
            data[item_name + '_成交金額'] = str_to_int(row[1])
            data[item_name + '_成交股數'] = str_to_int(row[2])
            data[item_name + '_成交筆數'] = str_to_int(row[3])
            if data[item_name + '_成交筆數'] == 0:
                data[item_name + '_平均每筆金額'] = 0.0
                data[item_name + '_平均每筆股數'] = 0.0
            else:
                n_trans = float(data[item_name + '_成交筆數'])
                data[item_name + '_平均每筆金額'] = data[item_name + '_成交金額'] / n_trans
                data[item_name + '_平均每筆股數'] = data[item_name + '_成交股數'] / n_trans

        return data
