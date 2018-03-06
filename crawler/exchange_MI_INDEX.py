# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from crawler.base import TwseCrawlerDaily
import requests
import pandas as pd
import re


class MI_INDEX(TwseCrawlerDaily):
    def __init__(self):
        super(MI_INDEX, self).__init__()
        self.name = 'MI_INDEX'
        self.url = 'http://www.tse.com.tw/exchangeReport/MI_INDEX?response=html&date={:04}{:02}{:02}&type=MS'

    def _download_one_day(self, day):
        """輸入一個date或datetime物件，下載物件指定的日期的資訊。
        """
        headers = {
            'Connection': 'close',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        }
        requests.session().keep_alive = False
        html_text = requests.get(self.url.format(day.year, day.month, day.day), headers=headers).text
        data = dict()
        table_name = '成交統計'
        try:
            table = pd.read_html(html_text, match=table_name)[0]
        except ValueError:  # not a transaction day
            return data
        data['datetime'] = self.date_to_datetime(day)
        for _, row in table.iterrows():
            item_name = table_name + '_' + re.sub(r'\(.*\)', '', row[0])
            data[item_name + '_成交金額'] = row[1]
            data[item_name + '_成交股數'] = row[2]
            data[item_name + '_成交筆數'] = row[3]
            data[item_name + '_平均每筆金額'] = row[1] / float(row[3]) if row[3] > 0 else 0.0
            data[item_name + '_平均每筆股數'] = row[2] / float(row[3]) if row[3] > 0 else 0.0
        return data
