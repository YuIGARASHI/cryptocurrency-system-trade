from src.common.common import CryptoType, TickerInfo, ExchangeType, OrderType, BalanceInfo
from src.common.common import WebAPIErrorCode, FileAccessErrorCode
from src.util.api_key_reader import APIKeyReader
import requests
import sys
import hmac
import hashlib
import time
import json
from datetime import datetime

class BitbankHandler:
    '''
    BitbankのAPIラッパークラス。
    https://github.com/bitbankinc/bitbank-api-docs/blob/master/README_JP.md
    '''

    def __init__(self):
        self.api_key = ""
        self.api_secret_key = ""
        self.connect_timeout = 3.0 # サーバとのコネクトタイムアウト
        self.read_timeout = 10.0   # サーバからの読み込みタイムアウト
        self.api_endpoint = "https://public.bitbank.cc"
        self.crypto_map = {
            CryptoType.BTC: "btc_jpy",
            CryptoType.ETH: "eth_jpy",
            CryptoType.BCH: "bcc_jpy",
            CryptoType.XRP: "xrp_jpy",
            CryptoType.LTC: "ltc_btc"
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
        url = self.api_endpoint + "/" + self.crypto_map[crypto_type] + "/depth"
        try:
            json_data = requests.get(url, timeout=(self.connect_timeout, self.read_timeout)).json()
        except:
            print("warn: Bitbankとの通信に失敗しました。")
            return WebAPIErrorCode.FAIL_CONNECTION, TickerInfo()
        if json_data["success"] != 1:
            print("error: Bitbankとの通信でエラーが発生しました。エラーコードは " + json_data["data"]["code"] + " です。")
            return WebAPIErrorCode.SYS_ERROR, TickerInfo()
        best_order_index = 0
        price_index = 0
        volume_index = 1
        best_sell_order = float(json_data["data"]["asks"][best_order_index][price_index])
        best_sell_order_volume = float(json_data["data"]["asks"][best_order_index][volume_index])
        best_buy_order = float(json_data["data"]["bids"][best_order_index][price_index])
        best_buy_order_volume = float(json_data["data"]["bids"][best_order_index][volume_index])
        ticker_info = TickerInfo(crypto_type)

        ticker_info = TickerInfo(crypto_type, ExchangeType.BITBANK, best_sell_order, best_buy_order,
                                 best_sell_order_volume, best_buy_order_volume)
        return WebAPIErrorCode.OK, ticker_info

    def load_api_key(self):
        '''
        API Key, Secret keyをロードする。
        注文を扱うメソッドを呼ぶ前には本メソッドを実行する必要がある。

        Returns:
        --------
        error_code : FileAccessErrorCode
            ファイルアクセスエラーコード。
        '''
        return FileAccessErrorCode.OK

    def make_buy_market_order(self, crypto_type, volume):
        '''
        成行注文（買い）を出す。

        Parameters:
        -----------
        crypto_type : CryptoType
            仮想通貨種別。
        volume : float
            数量。単位は仮想通貨による。
        timeout : int
            注文をキャンセルするまでの時間。[秒]
            この時間内に約定しなかった場合は cancel_expired_order が呼ばれた時点でキャンセルされる。

        Returns:
        --------
        error_code : WebAPIErrorCode
            WebAPIエラーコード。
        '''
        return WebAPIErrorCode.OK

    def make_sell_market_order(self, crypto_type, volume):
        '''
        成行注文（売り）を出す。

        Parameters:
        -----------
        crypto_type : CryptoType
            仮想通貨種別。
        volume : float
            数量。単位は仮想通貨による。
        timeout : int
            注文をキャンセルするまでの時間。[秒]
            この時間内に約定しなかった場合は cancel_expired_order が呼ばれた時点でキャンセルされる。

        Returns:
        --------
        error_code : WebAPIErrorCode
            WebAPIエラーコード。
        '''
        return WebAPIErrorCode.OK

    def cancel_expired_order(self):
        '''
        期限切れの注文をキャンセルする。

        Returns:
        --------
        error_code : WebAPIErrorCode
            WebAPIエラーコード。
        '''
        WebAPIErrorCode.OK

    def fetch_balance(self):
        return WebAPIErrorCode.OK, BalanceInfo()