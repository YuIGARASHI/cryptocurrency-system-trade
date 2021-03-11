# -*- coding: utf-8 -*-

from enum import Enum


class BalanceInfo:
    '''
    取引所の残高情報。
    '''
    def __init__(self, balance_info_dic):
        self.JPY = balance_info_dic["jpy"]
        self.BTC = balance_info_dic["btc"]
        self.ETH = balance_info_dic["eth"]
        self.QASH = balance_info_dic["qash"]

    def ___str___(self):
        return ">>>>>>>>>> BalanceInfo <<<<<<<<<<" + "\n" + \
               "JPY:" + str(self.JPY) + "\n" + \
               "BTC:" + str(self.BTC) + "\n" + \
               "ETH:" + str(self.ETH) + "\n" + \
               "QASH:" + str(self.QASH)

    def print_myself(self):
        print(self.___str___())


class TickerInfo:
    def __init__(self, product_id=-1, best_sell_order=-1, best_buy_order=-1,
                 best_sell_order_volume=-1, best_buy_order_volume=-1):
        '''
        Parameters:
        -----------
        product_id : int
            プロダクトID。
        best_sell_order : float
            現在板に出ている売り注文の最安値。単位は円建てなら[円]。
        best_buy_order : float
            現在板に出ている買い注文の最高値。単位は円建てなら[円]。
        best_sell_order_volume : float
            現在板に出ている最安の売り注文の数量。単位は仮想通貨による。
        best_buy_order_volume : float
            現在板に出ている最高の買い注文の数量。単位は仮想通貨による。
        '''
        self.product_id = product_id
        self.best_sell_order = best_sell_order
        self.best_buy_order = best_buy_order
        self.best_sell_order_volume = best_sell_order_volume
        self.best_buy_order_volume = best_buy_order_volume

    def print_myself(self):
        print(">>>>>>>>>> TickerInfo <<<<<<<<<<")
        print("product_id: " + str(self.product_id))
        print("best_sell_order: " +str(self.best_sell_order))
        print("best_buy_order: " + str(self.best_buy_order))
        print("best_sell_order_volume: " + str(self.best_sell_order_volume))
        print("best_buy_order_volume: " + str(self.best_buy_order_volume))


class ProductId:
    '''
    取り扱い通貨ペア一覧
    https://quoinexjp.zendesk.com/hc/ja/articles/360032764511-取り扱い通貨ペアの一覧

    ◇JPY建て
    BTC/JPY -> 5
    ETH/JPY -> 29
    XRP/JPY -> 83
    BCH/JPY -> 41
    QASH/JPY -> 50

    ◇BTC建て
    ETH/BTC -> 37
    XRP/BTC -> 111
    BCH/BTC -> 114

    ◇ETH建て
    QASH/ETH -> 51
    '''
    BTC_JPY = 5
    ETH_JPY = 29
    XRP_JPY = 83
    BCH_JPY = 41
    QASH_JPY = 50
    ETH_BTC = 37
    XRP_BTC = 111
    BCH_BTC = 114
    QASH_ETH = 51
