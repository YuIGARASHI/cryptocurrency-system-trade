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


class ZaifHandler:
    '''
    ZaifのAPIラッパークラス。
    https://zaif-api-document.readthedocs.io/ja/latest/index.html

    XRP, LTCに対応していないため注意。
    '''
    def __init__(self):
        self.api_key = ""
        self.api_secret_key = ""
        self.connect_timeout = 3.0 # サーバとのコネクトタイムアウト
        self.read_timeout = 10.0   # サーバからの読み込みタイムアウト
        self.api_endpoint = "https://api.zaif.jp/api/1"
        self.crypto_map = {
            CryptoType.BTC: "btc_jpy",
            CryptoType.ETH: "eth_jpy",
            CryptoType.BCH: "bch_jpy",
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
        if not self.crypto_map.get(crypto_type):
            print("error: " + str(crypto_type) + "はZaifで取り扱っていません。")
            return WebAPIErrorCode.SYS_ERROR, TickerInfo()
        path = "/depth/" + self.crypto_map[crypto_type]

        url = self.api_endpoint + path
        try:
            json_data = requests.get(url, timeout=(self.connect_timeout, self.read_timeout)).json()
        except:
            print("warn: Zaifとの通信に失敗しました。")
            return WebAPIErrorCode.FAIL_CONNECTION, TickerInfo()

        best_order_index = 0
        order_price_index = 0
        order_volume_index = 1
        best_sell_order = float(json_data["asks"][best_order_index][order_price_index])
        best_buy_order = float(json_data["bids"][best_order_index][order_price_index])
        best_sell_order_volume = float(json_data["asks"][best_order_index][order_volume_index])
        best_buy_order_volume = float(json_data["bids"][best_order_index][order_volume_index])
        ticker_info = TickerInfo(crypto_type, ExchangeType.ZAIF, best_sell_order, best_buy_order,
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

    def fetch_balance(self):
        '''
        取引所に預けている残高を取得する。

        Returns:
        --------
        error_code : WebAPIErrorCode
            WebAPIエラーコード。
        balance_info : BalanceInfo
            残高情報。
        '''
        return self.impl.fetch_balance()