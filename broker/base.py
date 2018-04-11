# -*- coding: utf-8 -*-
"""程式交易員的基本類別。
"""


class BaseBroker(object):
    """這是交易員的 base class。
    當回測開始時，回測程式會設定 broker.money(持有的現金) 及 broker.portfolio(持有的投資組合)。
    每一天，回測程式會呼叫append，交易員應該根據過去的資料，決定這一天要進行的交易，並傳回給回測。
    交易的類型只有6種：以開盤價買賣、以收盤價買賣、以特定價格買賣。
    以開盤價或收盤價的買賣，都可以掛市價單。
    """
    def append(self, one_day_data):
        """輸入「今天」的價格資料，傳回要進行的動作，並將今天的資料存入cache。
        動作的範例: [('buy', '0050', 53.20, 2000), ('sell', '2002', 21.80, 1000)]
        表示以53.2的價格買入2張0050，以21.8的價格賣出1張2002。
        注意：買入的花費不應超過 self.money，賣出的股票一定要存在於 self.portfolio。
        """
        raise NotImplementedError

    def buy_at_open(self, stock_id, n_shares='auto'):
        return {
            'action': 'buy',
            'stock_id': stock_id,
            'target_price': 'open',
            'n_shares': n_shares,
        }

    def sell_at_open(self, stock_id, n_shares='auto'):
        return {
            'action': 'sell',
            'stock_id': stock_id,
            'target_price': 'open',
            'n_shares': n_shares,
        }

    def buy_at_close(self, stock_id, n_shares='auto'):
        return {
            'action': 'buy',
            'stock_id': stock_id,
            'target_price': 'close',
            'n_shares': n_shares,
        }

    def sell_at_close(self, stock_id, n_shares='auto'):
        return {
            'action': 'sell',
            'stock_id': stock_id,
            'target_price': 'close',
            'n_shares': n_shares,
        }

    def buy_at_target(self, stock_id, target_price, n_shares='auto'):
        """設法以目標價買入，如果目標價超過當日的價格區間，則以收盤價買入。
        """
        return {
            'action': 'buy',
            'stock_id': stock_id,
            'target_price': target_price,
            'n_shares': n_shares,
        }

    def sell_at_target(self, stock_id, target_price, n_shares='auto'):
        """設法以目標價賣出，如果目標價超過當日的價格區間，則以收盤價賣出。
        """
        return {
            'action': 'sell',
            'stock_id': stock_id,
            'target_price': target_price,
            'n_shares': n_shares,
        }

    def stoploss_at_target(self, stock_id, target_price, n_shares='auto'):
        """設法以目標價賣出，如果最高價低於目標價，則改以收盤價賣出。
        """
        return {
            'action': 'stoploss',
            'stock_id': stock_id,
            'target_price': target_price,
            'n_shares': n_shares,
        }
