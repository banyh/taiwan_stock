# -*- coding: utf-8 -*-
"""程式交易員的基本類別。
"""


class BaseBroker(object):
    def append(self, one_day_data):
        """輸入「今天」的價格資料，傳回要進行的動作，並將今天的資料存入cache。
        動作的範例: [('buy', '0050', 53.20, 2000), ('sell', '2002', 21.80, 1000)]
        表示以53.2的價格買入2張0050，以21.8的價格賣出1張2002。
        """
        raise NotImplementedError
