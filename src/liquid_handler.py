# -*- coding: utf-8 -*-

import json
import requests
import jwt
import time
import sys
from datetime import datetime
from src.common import BalanceInfo, TickerInfo, ProductId
from src.logger import Logger


class LiquidHandler:
    '''
    LiquidのAPIラッパークラス。
    https://developers.liquid.com/#introduction

    API呼び出しのLimitは300回/5分。
    LiquidではLTCを扱っていないため注意。
    '''

    def __init__(self):
        self.api_key = ""
        self.api_secret_key = ""
        self.get_api_key()
        self.api_endpoint = "https://api.liquid.com"
        self.balance = None
        self.connect_timeout = 3.0 # サーバとのコネクトタイムアウト
        self.read_timeout = 10.0   # サーバからの読み込みタイムアウト
        self.logger = Logger()

    def get_api_key(self):
        '''
        APIキーを取得する。
        '''
        try:
            json_open = open("../config/api_keys.json", 'r')
            json_load = json.load(json_open)
            key_object = json_load["liquid"]
            self.api_key = key_object["api_key"]
            self.api_secret_key = key_object["api_secret_key"]
        except:
            print("api_keys.jsonからの情報取得に失敗しました。")

    def __get_private_headers(self, path):
        '''
        private通信メソッドで必要なヘッダーを取得する。
        '''
        timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        auth_payload = {
            "path": path,
            "nonce": timestamp,
            "token_id": self.api_key
        }
        signature = jwt.encode(payload=auth_payload, key=self.api_secret_key, algorithm='HS256')
        header = {
            'X-Quoine-API-Version': '2',
            'X-Quoine-Auth': signature,
            'Content-Type': 'application/json'
        }
        return header

    def fetch_balance(self):
        '''
        残高取得

        Returns:
            成功の場合 -> BalanceInfoオブジェクト
            成功の場合 -> None
        '''

        # 前回残高を取得してから取引を行っていない場合、前回の情報をそのまま返す
        if self.balance:
            return self.balance

        # 残高情報の取得
        path = "/accounts/balance"
        headers = self.__get_private_headers(path)
        url = self.api_endpoint + path
        try:
            json_data = requests.get(url, data={}, headers=headers).json()
        except:
            self.logger.write_log("fetch_balance: Liquidとの通信に失敗しました。")
            return None

        # 残高オブジェクト生成 & 返却
        jpy_index = 0
        qash_index = 1
        eth_index = 2
        btc_index = 3
        balance_info = {}
        balance_info["jpy"] = float(json_data[jpy_index]["balance"])
        balance_info["eth"] = float(json_data[eth_index]["balance"])
        balance_info["btc"] = float(json_data[btc_index]["balance"])
        balance_info["qash"] = float(json_data[qash_index]["balance"])
        self.balance = BalanceInfo(balance_info)
        return self.balance

    def make_market_order(self, product_id, volume, order_type):
        '''
        成行注文を出す。

        Returns:
        取引成功の場合 -> 0
        取引失敗の場合 -> -1
        '''
        # 引数チェック
        if order_type != "buy" and order_type != "sell":
            print("error:buyまたはsellを指定してください。")
            sys.exit()

        # 注文内容の作成
        params = {
            "order": {
                "order_type": "market", # 成行注文
                "product_id": product_id,
                "side": order_type,
                "quantity": volume
            }
        }

        # 注文の発行
        path = "/orders"
        headers = self.__get_private_headers(path)
        url = self.api_endpoint + path
        try:
            json_data = requests.post(url, data=json.dumps(params), headers=headers).json()
        except:
            self.logger.write_log("make_market_order:Liquidとの通信に失敗しました。")
            return -1
        if not json_data.get("id"):
            self.logger.write_log("make_market_order:Liquidへの注文に失敗しました。Json, 注文内容をダンプします。")
            self.logger.write_log(json_data)
            self.logger.write_log(str(product_id) + " >>>> " + str(volume) + " >>>> " + order_type)
            return -1
        self.logger.write_log("make_market_order: Liquidへの注文に成功しました。"
                         "売買種別は " + str(order_type) + ", 数量は " + str(volume) + " です。")
        self.balance = None
        return 0

    def fetch_ticker_info(self, product_id):
        '''
        板情報オブジェクトを取得する。

        Returns:
            成功の場合 -> TickerInfoオブジェクト
            失敗の場合 -> None
        '''

        # 板情報の取得
        path = "/products/" + str(product_id) + "/price_levels"
        url = self.api_endpoint + path
        try:
            json_data = requests.get(url, timeout=(self.connect_timeout, self.read_timeout)).json()
        except:
            self.logger.write_log("fetch_ticker_info: Liquidとの通信に失敗しました。")
            return None

        # 板情報オブジェクト生成 & 返却
        best_order_index = 0
        order_price_index = 0
        order_volume_index = 1
        best_buy_order = float(json_data["buy_price_levels"][best_order_index][order_price_index])
        best_buy_order_volume = float(json_data["buy_price_levels"][best_order_index][order_volume_index])
        best_sell_order = float(json_data["sell_price_levels"][best_order_index][order_price_index])
        best_sell_order_volume = float(json_data["sell_price_levels"][best_order_index][order_volume_index])
        ticker_info = TickerInfo(product_id, best_sell_order, best_buy_order, best_sell_order_volume,
                                 best_buy_order_volume)
        return ticker_info


if __name__ == "__main__":
    handler = LiquidHandler()
    handler.fetch_balance().print_myself()
    # handler.make_market_order(ProductId.BTC_JPY, 0.00027699, "sell")
    # handler.fetch_ticker_info(product_id=ProductId.BTC_JPY).print_myself()
    # handler.fetch_ticker_info(product_id=ProductId.ETH_BTC).print_myself()
    # handler.fetch_ticker_info(product_id=ProductId.ETH_JPY).print_myself()
    handler.fetch_ticker_info(product_id=ProductId.QASH_JPY).print_myself()
