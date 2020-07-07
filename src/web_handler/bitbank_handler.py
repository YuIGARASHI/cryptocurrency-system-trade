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
        self.public_api_endpoint = "https://public.bitbank.cc"
        self.private_api_endpoint = "https://api.bitbank.cc"
        self.crypto_map = {
            CryptoType.BTC: "btc_jpy",
            CryptoType.BCH: "bcc_jpy",
            CryptoType.XRP: "xrp_jpy",
        }
        self.balance = None

    def fetch_ticker_info(self, crypto_type):
        '''
        板情報オブジェクトを取得する。

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
        url = self.public_api_endpoint + "/" + self.crypto_map[crypto_type] + "/depth"
        try:
            json_data = requests.get(url, timeout=(self.connect_timeout, self.read_timeout)).json()
        except:
            print("warn: Bitbankとの通信に失敗しました。")
            return WebAPIErrorCode.FAIL_CONNECTION, TickerInfo()
        if json_data["success"] != 1:
            print("error: Bitbankとの通信でエラーが発生しました。エラーコードは " + str(json_data["data"]["code"]) + " です。")
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
        error_code, api_key, api_secret_key = APIKeyReader.get_api_keys(ExchangeType.BITBANK)
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
        if crypto_type != CryptoType.BTC:
            print("error: 現在BTC以外の売買はサポートしていません。")
            return WebAPIErrorCode.FAIL_ORDER

        timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        path = "/v1/user/spot/order"
        url = self.private_api_endpoint + path
        buy_sell_dict = {
            OrderType.BUY: "buy",
            OrderType.SELL: "sell"
        }
        params = {
            "pair": self.crypto_map[crypto_type],
            "amount": volume,
            "side": buy_sell_dict[order_type],
            "type": "market"
        }
        text = timestamp + json.dumps(params)
        sign = hmac.new(bytes(self.api_secret_key.encode('ascii')), bytes(text.encode('ascii')),
                        hashlib.sha256).hexdigest()
        headers = {
            'Content-Type': 'application/json',
            "ACCESS-KEY": self.api_key,
            "ACCESS-NONCE": timestamp,
            "ACCESS-SIGNATURE": sign
        }

        try:
            json_data = requests.post(url, data=json.dumps(params), headers=headers).json()
        except:
            print("warn: Bitbankとの通信に失敗しました。")
            return WebAPIErrorCode.FAIL_CONNECTION
        if json_data["success"] != 1:
            print("warn: Bitbankへの売買注文に失敗しました。ステータスコードは下記です。")
            print(str(json_data["data"]["code"]))
            return WebAPIErrorCode.FAIL_ORDER
        print("info: Bitbankへの注文に成功しました。売買種別は " + str(order_type) + ", 数量は " + str(volume) + " です。")
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
        path = "/v1/user/assets"
        url = self.private_api_endpoint + path
        text = timestamp + path
        sign = hmac.new(bytes(self.api_secret_key.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).\
            hexdigest()
        headers = {
            "ACCESS-KEY": self.api_key,
            "ACCESS-NONCE": timestamp,
            "ACCESS-SIGNATURE": sign
        }
        try:
            json_data = requests.get(url, data={}, headers=headers).json()
        except:
            print("warn: Bitbankとの通信に失敗しました。")
            return WebAPIErrorCode.FAIL_CONNECTION, BalanceInfo()
        if json_data["success"] != 1:
            print("warn: Bitbankからの残高取得に失敗しました。ステータスコードは以下です。")
            print(str(json_data["data"]["code"]))
            return WebAPIErrorCode.FAIL_CONNECTION, BalanceInfo()
        for asset in json_data["data"]["assets"]:
            if asset["asset"] == "jpy":
                jpy_balance = float(asset["free_amount"])
            elif asset["asset"] == "btc":
                btc_balance = float(asset["free_amount"])
            elif asset["asset"] == "eth":
                eth_balance = float(asset["free_amount"])
        balance_info = BalanceInfo(jpy_balance, btc_balance, eth_balance)
        self.balance = balance_info

        return WebAPIErrorCode.OK, balance_info