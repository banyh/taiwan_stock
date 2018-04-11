# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from pymongo import MongoClient, ASCENDING
from datetime import timedelta, datetime, date
import pytz
from collections import defaultdict
import numpy as np


class TwseDailyDataset(object):
    def __init__(self, mongo_url='localhost'):
        self.db = MongoClient(host=mongo_url)['twse_daily']
        self.db.authenticate(name='crawler', password='crawler')
        self.collections = [self.db[c] for c in ['BFI82U', 'FMTQIK', 'MI_INDEX', 'MI_MARGN', 'STOCK_DAY']]

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
            result = c.find_one({'_id': self.date_to_datetime(day)})
            if result:
                data.update(result)
        return data

    def gen_features(self, feature_names):
        start_day = date(2004, 4, 1)
        end_day = date.today() if datetime.now().hour > 15 else date.today() - timedelta(days=1)
        dates = []
        day = start_day
        while day <= end_day:
            dates.append(day)
            day += timedelta(days=1)

        masks = np.zeros((len(dates), len(feature_names)), dtype=bool)
        features = np.zeros((len(dates), len(feature_names)), dtype=np.float32)
        cond = {n: 1 for n in feature_names}
        cond.update({'_id': 0})
        print(cond)

        for i, day in enumerate(dates):
            feat = {}
            for c in self.collections:
                feat.update(c.find_one({'_id': self.date_to_datetime(day)}, cond))
            print(day, feat)
            for j, name in enumerate(feature_names):
                if name in feat:
                    features[i, j] = feat[name]
                    masks[i, j] = True
        return dates, masks, features

dailydata = TwseDailyDataset()
