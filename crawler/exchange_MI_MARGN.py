# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from crawler.base import TwseCrawlerDaily
from util import str_to_int, proxy, str_to_float, RetryException
import requests
import csv
import re


class MI_MARGN(TwseCrawlerDaily):
    name = 'MI_MARGN'
    url = 'http://www.tse.com.tw/exchangeReport/MI_MARGN?response=json&type=ALL&date={:04}{:02}{:02}&_={}'

    def __init__(self):
        super(MI_MARGN, self).__init__()

    def _download_one_day(self, day):
        """輸入一個date或datetime物件，下載物件指定的日期的資訊。
        """
        try:
            self.get_json(day, name_field='creditFields', value_field='creditList')
        except HolidayException:
            return {'_id': self.date_to_datetime(day), 'TradingDay': False}

        data = dict()
        data['_id'] = self.date_to_datetime(day)
        data['TradingDay'] = True
        for row in js['creditList']:
            item_name = re.sub('\(.*?\)', '', row[0])
            for name, value in zip(js['creditFields'][1:], row[1:]):
                data[item_name + '_' + re.sub('\(.*?\)', '', name)] = str_to_int(value)
        return data
