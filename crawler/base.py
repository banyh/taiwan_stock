# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from pymongo import MongoClient, ASCENDING
from datetime import timedelta, datetime
import pytz
import time


class TwseCrawlerDaily(object):
    """用來抓每天一次的資料
    """
    name = 'TwseCrawlerDaily'

    def __init__(self, mongo_url='localhost'):
        super(TwseCrawlerDaily, self).__init__()
        self.db = MongoClient(host=mongo_url)['twse_daily']
        self.db.authenticate(name='crawler', password='crawler')

        if self.name not in self.db.collection_names():
            c = self.db.create_collection(self.name)
        else:
            c = self.db[self.name]
        c.create_index([('datetime', ASCENDING)], unique=True)

    def _download_one_day(self, day):
        raise NotImplementedError

    def download(self, from_date, to_date):
        """將from_date到to_date之間所有資料抓下來，存到資料庫。
        """
        assert from_date < to_date

        one_day = timedelta(days=1)
        day = from_date
        data = []
        while day <= to_date:
            print(day)
            data.append(self._download_one_day(day))
            time.sleep(0.01)
            day += one_day
        # 當設定 ordered=False 時，出現錯誤不會停止，而會將所有資料試著insert一遍
        # 因為有設定index "datetime"，如果出現重複的日期，那一筆就不會插入
        self.db.insert_many(data, ordered=False)

    def date_to_datetime(self, day):
        """將date物件轉換成datetime物件，時間設為台灣時間的下午2點(收盤時間)。
        pymongo寫入datetime物件時，會自動轉換成utc timezone。
        """
        dt = datetime(year=day.year, month=day.month, day=day.day, hour=14)
        return pytz.timezone('Asia/Taipei').localize(dt)
