# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from crawler.holidaySchedule import HolidaySchedule, WorkdaySchedule
from pymongo import MongoClient, ASCENDING
from datetime import timedelta, datetime, date
import pytz
import time


class TwseCrawlerDaily(object):
    """用來抓每天一次的資料
    """
    def __init__(self, mongo_url='localhost'):
        super(TwseCrawlerDaily, self).__init__()
        self.db = MongoClient(host=mongo_url)['twse_daily']
        self.db.authenticate(name='crawler', password='crawler')

        if hasattr(self, 'name'):
            self.col = self.db[getattr(self, 'name')]

    def timestamp(self):
        return str(int(time.time() * 1000) - 500)

    def isHoliday(self, day):
        if isinstance(day, datetime):
            day = date(day.year, day.month, day.day)
        if day in HolidaySchedule:
            return True
        if day in WorkdaySchedule:
            return False
        if day.weekday() >= 5:  # 5=Saturday, 6=Sunday
            return True
        return False

    def _download_one_day(self, day):
        raise NotImplementedError

    def download(self, from_date, to_date):
        """將from_date到to_date之間所有資料抓下來，存到資料庫。
        """
        assert from_date < to_date

        one_day = timedelta(days=1)
        day = from_date
        while day <= to_date:
            if self.col.find_one({'_id': self.date_to_datetime(day)}):  # already exists
                day += one_day
                continue
            result = self._download_one_day(day)
            if result:
                self.col.insert_one(result)
                print(day, len(result))
            day += one_day
        # 當設定 ordered=False 時，出現錯誤不會停止，而會將所有資料試著insert一遍
        # 如果出現重複的日期，那一筆就不會插入，但仍然會發生 BulkWriteError

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
