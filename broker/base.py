# -*- coding: utf-8 -*-
"""程式交易員的基本類別。
"""


class BaseBroker(object):
    """這是交易員的 base class。
    當回測開始時，回測程式會設定 broker.money(持有的現金) 及 broker.portfolio(持有的投資組合)。
    每一天，回測程式會呼叫append，交易員應該根據過去的資料，決定這一天要進行的交易，並傳回給回測。
    """
    def append(self, one_day_data):
        """輸入「今天」的價格資料，傳回要進行的動作，並將今天的資料存入cache。
        動作的範例: [('buy', '0050', 53.20, 2000), ('sell', '2002', 21.80, 1000)]
        表示以53.2的價格買入2張0050，以21.8的價格賣出1張2002。
        注意：買入的花費不應超過 self.money，賣出的股票一定要存在於 self.portfolio。
        """
        raise NotImplementedError
