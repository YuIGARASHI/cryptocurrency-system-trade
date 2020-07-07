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
import jwt

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
        self.connect_timeout = 3.0 # サーバとのコネクトタイムアウト
        self.read_timeout = 10.0   # サーバからの読み込みタイムアウト
        self.api_endpoint = "https://api.liquid.com"
        self.ids = {
            CryptoType.BTC: 5,
            CryptoType.ETH: 29,
            CryptoType.BCH: 41,
            CryptoType.XRP: 83
        }
        self.balance = None

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
        if not self.ids.get(crypto_type):
            print("warn: " + str(crypto_type) + " はLiquidで扱っていません。")
            return WebAPIErrorCode.SYS_ERROR, TickerInfo()
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
        '''
        API Key, Secret keyをロードする。
        注文を扱うメソッドを呼ぶ前には本メソッドを実行する必要がある。

        Returns:
        --------
        error_code : FileAccessErrorCode
            ファイルアクセスエラーコード。
        '''
        error_code, api_key, api_secret_key = APIKeyReader.get_api_keys(ExchangeType.LIQUID)
        if error_code != FileAccessErrorCode.OK:
            return error_code
        self.api_key = api_key
        self.api_secret_key = api_secret_key
        return FileAccessErrorCode.OK

    def make_buy_market_order(self, crypto_type, volume):
        return self.__make_market_order(crypto_type, volume, OrderType.BUY)

    def make_sell_market_order(self, crypto_type, volume):
        return self.__make_market_order(crypto_type, volume, OrderType.SELL)

    def __make_market_order(self, crypto_type, volume, order_type):
        '''
        成行注文を出す。

        Parameters:
        -----------
        crypto_type : CryptoType
            仮想通貨種別。
        volume : float
            数量。単位は仮想通貨による。
        order_type : OrderType
            売買種別。

        Returns:
        --------
        error_code : WebAPIErrorCode
            WebAPIエラーコード。
        '''
        order_type_dict = {
            OrderType.BUY: "buy",
            OrderType.SELL: "sell"
        }
        if not self.ids.get(crypto_type):
            print("error: 無効な仮想通貨種別が指定されています。")
            return WebAPIErrorCode.SYS_ERROR

        params = {
            "order": {
                "order_type": "market",
                "product_id": self.ids[crypto_type],
                "side": order_type_dict[order_type],
                "quantity": volume
            }
        }
        timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        path = "/orders"
        url = self.api_endpoint + path;
        auth_payload = {
            "path": path,
            "nonce": timestamp,
            "token_id": self.api_key
        }
        signature = jwt.encode(payload=auth_payload, key=self.api_secret_key, algorithm='HS256')
        headers = {
            'X-Quoine-API-Version': '2',
            'X-Quoine-Auth': signature,
            'Content-Type': 'application/json'
        }
        try:
            json_data = requests.post(url, data=json.dumps(params), headers=headers).json()
        except:
            print("warn: Liquidとの通信に失敗しました。")
            return WebAPIErrorCode.FAIL_CONNECTION
        if not json_data.get("id"):
            print("warn: Liquidへの注文に失敗しました。Jsonをダンプします。")
            print(json_data)
            return WebAPIErrorCode.FAIL_ORDER
        print("info: Liquidへの注文に成功しました。売買種別は " + str(order_type) + ", 数量は " + str(volume) + " です。")
        self.balance = None
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
        if self.balance:
            return WebAPIErrorCode.OK, self.balance

        timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        path = "/accounts/balance"
        url = self.api_endpoint + path
        auth_payload = {
            "path": path,
            "nonce": timestamp,
            "token_id": self.api_key
        }
        signature = jwt.encode(payload=auth_payload, key=self.api_secret_key, algorithm='HS256')
        headers = {
            'X-Quoine-API-Version': '2',
            'X-Quoine-Auth': signature,
            'Content-Type': 'application/json'
        }

        try:
            json_data = requests.get(url, data={}, headers=headers).json()
        except:
            print("warn: Liquidとの通信に失敗しました。")
            return WebAPIErrorCode.FAIL_CONNECTION
        jpy_index = 0
        eth_index = 1
        btc_index = 2
        jpy = float(json_data[jpy_index]["balance"])
        eth = float(json_data[eth_index]["balance"])
        btc = float(json_data[btc_index]["balance"])
        balance_info = BalanceInfo(jpy, btc, eth)
        self.balance = balance_info

        return WebAPIErrorCode.OK, balance_info
