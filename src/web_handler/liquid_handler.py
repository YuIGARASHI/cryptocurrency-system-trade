from src.common.common import CryptoType, TickerInfo, ExchangeType, BalanceInfo, OrderType
from src.common.common import WebAPIErrorCode, FileAccessErrorCode
from src.util.api_key_reader import APIKeyReader
import sys
import hmac
import hashlib
import time
import json
import requests
from datetime import datetime

class LiquidHandler:
    '''
    LiquidのAPIラッパークラス。
    https://developers.liquid.com/#introduction

    API呼び出しのLimitは300回/5分。
    '''

    def __init__(self):
        self.api_key = ""
        self.api_secret_key = ""
        self.connect_timeout = 3.0 # サーバとのコネクトタイムアウト
        self.read_timeout = 10.0   # サーバからの読み込みタイムアウト
        self.api_endpoint = "https://api.liquid.com"
        self.ids = {
            CryptoType.BTC: 5,
            CryptoType.ETH: 29
        }

    def fetch_ticker_info(self, crypto_type):
        '''
        板情報オブジェクトを取得する。
        想定していない仮想通貨が指定された場合はプログラムを停止する。

        Parameters:
        -----------
        crypto_type : CryptoType
            仮想通貨の種類。

        Returns:
        --------
        error_code : WebAPIErrorCode
        　WebAPIエラーコード。
        ticker_info : TickerInfo
        　板情報オブジェクト。
        '''
        path = "/products/" + str(self.ids[crypto_type]) + "/price_levels"
        url = self.api_endpoint + path
        try:
            json_data = requests.get(url, timeout=(self.connect_timeout, self.read_timeout)).json()
        except:
            print("warn: Liquidとの通信に失敗しました。")
            return WebAPIErrorCode.FAIL_CONNECTION, TickerInfo()
        best_order_index = 0
        order_price_index = 0
        order_volume_index = 1
        best_buy_order = float(json_data["buy_price_levels"][best_order_index][order_price_index])
        best_buy_order_volume = float(json_data["buy_price_levels"][best_order_index][order_volume_index])
        best_sell_order = float(json_data["sell_price_levels"][best_order_index][order_price_index])
        best_sell_order_volume = float(json_data["sell_price_levels"][best_order_index][order_volume_index])
        ticker_info = TickerInfo(crypto_type, ExchangeType.LIQUID, best_sell_order, best_buy_order,
                                 best_sell_order_volume, best_buy_order_volume)
        return WebAPIErrorCode.OK, ticker_info

    def load_api_key(self):
        return FileAccessErrorCode.OK

    def make_buy_market_order(self, crypto_type, volume):
        return WebAPIErrorCode.OK

    def make_sell_market_order(self, crypto_type, volume):
        return WebAPIErrorCode.OK

    def cancel_expired_order(self):
        return WebAPIErrorCode.OK

    def fetch_balance(self):
        return WebAPIErrorCode.OK, BalanceInfo()
