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

class HuobiJpHandler:
    '''
    Huobi japanのAPIラッパークラス。
    https://api-doc.huobi.co.jp/#api
    '''

    def __init__(self):
        self.api_key = ""
        self.api_secret_key = ""
        self.connect_timeout = 3.0 # サーバとのコネクトタイムアウト
        self.read_timeout = 10.0   # サーバからの読み込みタイムアウト
        self.api_endpoint = "https://api-cloud.huobi.co.jp"
        self.crypto_map = {
            CryptoType.BTC: "btcjpy",
            CryptoType.ETH: "ethjpy",
            CryptoType.BCH: "bchjpy",
            CryptoType.XRP: "xrpjpy",
            CryptoType.LTC: "ltcjpy"
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
        url = self.api_endpoint + "/market/depth"
        params = {
            "symbol": self.crypto_map[crypto_type],
            "type": "step1"  # 板情報を取得する際のステップ幅
        }
        try:
            json_data = requests.get(url, params=params, timeout=(self.connect_timeout, self.read_timeout)).json()
        except:
            print("warn: Huobiとの通信に失敗しました。")
            return WebAPIErrorCode.FAIL_CONNECTION, TickerInfo()
        if json_data["status"] != "ok":
            print("error: Huobiとの通信でエラーが発生しました。エラーメッセージは " + json_data["err-msg"]+ " です。")
            return WebAPIErrorCode.SYS_ERROR, TickerInfo()
        best_order_index = 0
        price_index = 0
        volume_index = 1
        best_sell_order = float(json_data["tick"]["asks"][best_order_index][price_index])
        best_sell_order_volume = float(json_data["tick"]["asks"][best_order_index][volume_index])
        best_buy_order = float(json_data["tick"]["bids"][best_order_index][price_index])
        best_buy_order_volume = float(json_data["tick"]["bids"][best_order_index][volume_index])
        ticker_info = TickerInfo(crypto_type)

        ticker_info = TickerInfo(crypto_type, ExchangeType.HUOBI_JP, best_sell_order, best_buy_order,
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
        return WebAPIErrorCode.OK, BalanceInfo()