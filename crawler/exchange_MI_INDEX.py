# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from crawler.base import TwseCrawlerDaily
from util import str_to_int, proxy
import requests
import csv
import re


class MI_INDEX(TwseCrawlerDaily):
    name = 'MI_INDEX'
    url = 'http://www.tse.com.tw/exchangeReport/MI_INDEX?response=csv&date={:04}{:02}{:02}'

    def __init__(self):
        super(MI_INDEX, self).__init__()

    def _download_one_day(self, day):
        """輸入一個date或datetime物件，下載物件指定的日期的資訊。
        """
        csv_text = proxy.get(self.url.format(day.year, day.month, day.day))
        try:
            table = list(csv.reader(csv_text.split('\n')))
            start_row = [i + 1 for i, r in enumerate(table) if r and r[0].startswith('成交統計')][0]
            end_row = [i for i, r in enumerate(table) if r and r[0].startswith('證券合計')][0]
        except (ValueError, IndexError):  # not a transaction day
            return {'_id': self.date_to_datetime(day), 'TradingDay': False}

        data = dict()
        data['_id'] = self.date_to_datetime(day)
        data['TradingDay'] = True
        for row in table[start_row:end_row]:
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
