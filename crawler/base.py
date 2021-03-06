# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from crawler.holidaySchedule import HolidaySchedule, WorkdaySchedule
from pymongo import MongoClient, ASCENDING
from datetime import timedelta, datetime, date
import pytz
import time
from util import RetryException, HolidayException, proxy


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
        if day < date(2002, 1, 1):  # 在 holidaySchedule 中沒有2002以前的資料，所以一律視為上班日
            return False
        if day in HolidaySchedule:  # 確定是假日
            return True
        if day in WorkdaySchedule:  # 確定是上班日
            return False
        if day.weekday() >= 5:  # 5=星期六, 6=星期日
            return True
        return False

    def get_json(self, day, name_field, value_field):
        if self.isHoliday(day):
            raise HolidayException()

        try:
            ts = self.timestamp()
            self.js = js = proxy.get(self.url.format(day.year, day.month, day.day, ts)).json()
            if (value_field not in js) or (not js[value_field]):
                raise HolidayException()
            assert len(js[name_field]) == len(js[value_field][0])
        except HolidayException:
            raise
        except:
            proxy.increase_loc_index()
            raise RetryException()

    def _download_one_day(self, day):
        raise NotImplementedError

    def download(self, from_date=date(2004, 1, 1), to_date=date.today()):
        """將from_date到to_date之間所有資料抓下來，存到資料庫。
        """
        assert from_date < to_date
        # 如果今天還沒收盤，不要抓今天的資料
        if datetime.now().hour < 15 and to_date == date.today():
            to_date = date.today() - timedelta(days=1)

        one_day = timedelta(days=1)
        day = from_date
        timeout = 0
        while day <= to_date:
            if self.col.find_one({'_id': self.date_to_datetime(day)}):  # already exists
                day += one_day
                continue
            try:
                result = self._download_one_day(day)
            except RetryException:
                timeout += 1
                if timeout > 5:
                    raise
                continue
            else:
                timeout = 0
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
