# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from collections import defaultdict
from datetime import datetime, timedelta, date
from dataset import dailydata
from util import slack_log

one_day = timedelta(days=1)


def buy_fee(amount):
    """假設買進時的手續費是0.1425%"""
    return amount * 0.001425


def sell_fee(amount):
    """假設賣出時的手續費是0.1425%，交易稅是0.3%"""
    return amount * (0.001425 + 0.003)


def backtest(broker, start_money, start_day=date(2017, 1, 1), end_day=date(2017, 12, 31)):
    broker.money = float(start_money)
    broker.portfolio = defaultdict(int)
    today = start_day
    while today <= end_day:
        data = dailydata[today]
        if data['TradingDay']:
            last_trading_data = data
        transactions = broker.append(data)
        for trans in transactions:
            target_price, stock_id = trans['target_price'], trans['stock_id']
            if target_price == 'open':
                price = data[stock_id + '_開盤價']
            elif target_price == 'close':
                price = data[stock_id + '_收盤價']
            elif target_price > data[stock_id + '_最低價'] and target_price < data[stock_id + '_最高價']:
                price = target_price
            else:
                price = data[stock_id + '_收盤價']

            action, num_shares = trans['action'], trans['n_shares']
            if num_shares == 'auto':
                if action == 'buy':
                    num_shares = int(broker.money / (price * 1000)) * 1000
                    act = '買進'
                elif action == 'sell':
                    num_shares = broker.portfolio[stock_id]
                    act = '賣出'
                elif action == 'stoploss':
                    num_shares = broker.portfolio[stock_id]
                    act = '停損賣出'
            prefix = '{}，以{}的價格{}{}股"{}"'.format(today, price, act, num_shares, stock_id)

            if action == 'buy':
                broker.money -= price * num_shares + buy_fee(price * num_shares)
                broker.portfolio[stock_id] += num_shares
            elif action == 'sell' or action == 'stoploss':
                broker.portfolio[stock_id] -= num_shares
                broker.money += price * num_shares - sell_fee(price * num_shares)
                assert broker.portfolio[stock_id] >= 0
            msg = prefix + '，餘額{}'.format(broker.money)
            print(msg)
        today += one_day

    # 測試期間結束時，以最後一個交易日的收盤價，賣出所有股票
    for stock_id in broker.portfolio:
        if broker.portfolio[stock_id] > 0:
            price = last_trading_data[stock_id + '_收盤價']
            num_shares = broker.portfolio[stock_id]
            broker.money += price * num_shares - sell_fee(price * num_shares)
            print('以{}的價格賣出{}股{}，餘額{}'.format(price, num_shares, stock_id, broker.money))

    roi = broker.money / start_money * 100 - 100
    print('啟始資金={}，投資報酬率={:.2f}%'.format(start_money, roi))
    return roi
