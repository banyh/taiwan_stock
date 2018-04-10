# -*- coding: utf-8 -*-
from pymongo import MongoClient, ASCENDING
from datetime import timedelta, datetime, date
import pytz
from collections import defaultdict


class TwseDailyDataset(object):
    def __init__(self, mongo_url='localhost'):
        self.db = MongoClient(host=mongo_url)['twse_daily']
        self.db.authenticate(name='crawler', password='crawler')
        self.collections = ['BFI82U', 'FMTQIK', 'MI_INDEX', 'MI_MARGN', 'STOCK_DAY']

    def date_to_datetime(self, obj_or_year, month=None, day=None):
        """將date物件轉換成datetime物件，時間設為台灣時間的下午2點(收盤時間)。
        pymongo寫入datetime物件時，會自動轉換成utc timezone。
        """
        if month is None:
            year, month, day = obj_or_year.year, obj_or_year.month, obj_or_year.day
        else:
            year = obj_or_year
        dt = datetime(year=year, month=month, day=day, hour=14)
        return pytz.timezone('Asia/Taipei').localize(dt)

    def __getitem__(self, day):
        data = dict()
        for c in self.collections:
            result = self.db[c].find_one({'_id': self.date_to_datetime(day)})
            if result:
                data.update(result)
        return data

dailydata = TwseDailyDataset()
