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


class GmoHandler:
    '''
    GMOのAPIラッパークラス。
    https://api.coin.z.com/docs/#outline

    同一アカウントからGETのAPI呼出は1秒間に3回が上限。
    同一アカウントからPOSTのAPI呼出は1秒間に3回が上限。
    '''

    def __init__(self):
        self.api_key = ""
        self.api_secret_key = ""
        self.connect_timeout = 3.0 # サーバとのコネクトタイムアウト
        self.read_timeout = 10.0   # サーバからの読み込みタイムアウト
        self.api_private_endpoint = "https://api.coin.z.com/private"
        self.api_public_endpoint = "https://api.coin.z.com/public"
        self.crypto_map = {
            CryptoType.BTC: "BTC",
            CryptoType.ETH: "ETH",
            CryptoType.BCH: "BCH",
            CryptoType.XRP: "XRP",
            CryptoType.LTC: "LTC"
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
        path = "/v1/orderbooks"
        url = self.api_public_endpoint + path
        params = {}
        params["symbol"] = self.crypto_map[crypto_type]

        try:
            json_data = requests.get(url, params=params, timeout=(self.connect_timeout, self.read_timeout)).json()
        except:
            print("warn: GMOとの通信に失敗しました。")  # todo: エラーログに吐き出す。
            return WebAPIErrorCode.FAIL_CONNECTION, TickerInfo()
        if json_data["status"] != 0:
            print("warn: GMOとの通信に失敗しました。メッセージは下記の通りです。")
            print(json_data)
            return WebAPIErrorCode.SYS_ERROR, TickerInfo()

        best_order_index = 0
        best_sell_order = float(json_data["data"]["asks"][best_order_index]["price"])
        best_buy_order = float(json_data["data"]["bids"][best_order_index]["price"])
        best_sell_order_volume = float(json_data["data"]["asks"][best_order_index]["size"])
        best_buy_order_volume = float(json_data["data"]["bids"][best_order_index]["size"])
        ticker_info = TickerInfo(crypto_type, ExchangeType.GMO, best_sell_order, best_buy_order,
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
        error_code, api_key, api_secret_key = APIKeyReader.get_api_keys(ExchangeType.GMO)
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
        リスク回避のために、0.05BTC以上の注文を出そうとするとエラーで落ちる。
        (現時点では、ETHの場合はセーフティネットを設けていないため注意)
        また、volumeの0.0001未満の部分については切り捨てる。

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
        if crypto_type == CryptoType.BTC:
            symbol = "BTC"
        elif crypto_type == CryptoType.ETH:
            symbol = "ETH"
        else:
            print("error: 無効なCryptoTypeが指定されています。プログラムを停止します。")  # todo: エラーログに吐き出す。
            sys.exit()

        if order_type == OrderType.BUY:
            side = "BUY"
        elif order_type == OrderType.SELL:
            side = "SELL"
        else:
            print("error: 無効なOrderTypeが指定されています。プログラムを停止します。")  # todo: エラーログに吐き出す。
            sys.exit()

        timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        method = 'POST'
        path = '/v1/order'
        req_body = {
            "symbol": symbol,  # BTC_JPY は信用取引なので注意.
            "side": side,
            "executionType": "MARKET",
            "size": str(volume)
        }
        text = timestamp + method + path + json.dumps(req_body)
        sign = hmac.new(bytes(self.api_secret_key.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
        headers = {
            "API-KEY": self.api_key,
            "API-TIMESTAMP": timestamp,
            "API-SIGN": sign
        }

        try:
            json_data = requests.post(self.api_private_endpoint + path, headers=headers, data=json.dumps(req_body)).\
                json()
        except:
            print("warn: GMOとの通信に失敗しました。")  # todo: エラーログに吐き出す。
            return WebAPIErrorCode.FAIL_CONNECTION
        if json_data["status"] != 0:
            print("warn: GMOへの売買注文に失敗しました。メッセージは下記の取りです。")
            print(json_data)
            return WebAPIErrorCode.FAIL_ORDER

        print("info: GMOへの注文に成功しました。売買種別は " + side + ", 数量は " + str(volume) + " です。")
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
        method = 'GET'
        path = '/v1/account/assets'
        text = timestamp + method + path
        sign = hmac.new(bytes(self.api_secret_key.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).\
            hexdigest()
        headers = {
            "API-KEY": self.api_key,
            "API-TIMESTAMP": timestamp,
            "API-SIGN": sign
        }

        try:
            json_data = requests.get(self.api_private_endpoint + path, headers=headers).json()
        except:
            print("warn: GMOとの通信に失敗しました。")  # todo: エラーログに吐き出す。
            return WebAPIErrorCode.FAIL_CONNECTION, BalanceInfo()
        if not json_data.get("data"):
            print("warn: GMOからの価格取得に失敗しました。メッセージは下記の通りです。")
            print(json_data["messages"])
            return WebAPIErrorCode.FAIL_CONNECTION, BalanceInfo()

        balance_data_list = json_data["data"]
        for balance_data in balance_data_list:
            if balance_data["symbol"] == "JPY":
                yen_balance = float(balance_data["amount"])
            elif balance_data["symbol"] == "BTC":
                btc_balance = float(balance_data["amount"])
            elif balance_data["symbol"] =="ETH":
                eth_balance = float(balance_data["amount"])
            else:
                continue
        balance_info = BalanceInfo(yen_balance, btc_balance, eth_balance)
        self.balance = balance_info

        return WebAPIErrorCode.OK, balance_info
