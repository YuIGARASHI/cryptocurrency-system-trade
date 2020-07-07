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


class CoincheckHandler:
    '''
    CoincheckのAPIラッパークラス。
    https://coincheck.com/ja/documents/exchange/api#about
    '''
    def __init__(self):
        self.api_key = ""
        self.api_secret_key = ""
        self.connect_timeout = 3.0 # サーバとのコネクトタイムアウト
        self.read_timeout = 10.0   # サーバからの読み込みタイムアウト
        self.api_endpoint = "https://coincheck.com"

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
        path = "/api/order_books"
        url =  self.api_endpoint + path
        if crypto_type != CryptoType.BTC:
            print("error: Coincheckでは現在BTCのみ扱っています。プログラムを停止します。")  # todo:エラーログを吐き出す。
            return WebAPIErrorCode.SYS_ERROR, TickerInfo()

        try:
            json_data = requests.get(url, timeout=(self.connect_timeout, self.read_timeout)).json()
        except:
            print("warn: Coincheckとの通信に失敗しました。")  # todo: エラーログに吐き出す。
            return WebAPIErrorCode.FAIL_CONNECTION, TickerInfo()
        best_order_index = 0
        order_price_index = 0
        order_volume_index = 1
        best_sell_order = float(json_data["asks"][best_order_index][order_price_index])
        best_buy_order = float(json_data["bids"][best_order_index][order_price_index])
        best_sell_order_volume = float(json_data["asks"][best_order_index][order_volume_index])
        best_buy_order_volume = float(json_data["bids"][best_order_index][order_volume_index])
        ticker_info = TickerInfo(crypto_type, ExchangeType.COINCHECK, best_sell_order, best_buy_order,
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
        error_code, api_key, api_secret_key = APIKeyReader.get_api_keys(ExchangeType.COINCHECK)
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
        リスク回避のために、0.02BTC以上の注文を出そうとするとエラーで落ちる。
        (現時点では、ETHの場合はセーフティネットを設けていないため注意)
        また、volumeの0.005未満の部分については切り捨てる。(Coincheck APIの仕様)

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
            pair = "btc_jpy"
        else:
            print("error: Coincheckでは現在BTCのみ扱っています。プログラムを停止します。")  # todo:エラーログを吐き出す。
            sys.exit()

        if order_type == OrderType.BUY:
            order_type_str = "market_buy"
        elif order_type == OrderType.SELL:
            order_type_str = "market_sell"
        else:
            print("error: 無効なOrderTypeが指定されています。プログラムを停止します。")  # todo: エラーログに吐き出す。
            sys.exit()

        if volume > 0.02:
            print("error: 注文の数量が大きすぎます。プログラムを停止します。")  # todo: エラーログを吐き出す。
            sys.exit()
        volume -= volume % 0.001  # 0.001 未満切り捨て
        path = "/api/exchange/orders"
        params = {
            "pair": pair,
            "order_type": order_type_str,
            "amount": volume,
        }

        # 買いの成行注文の場合、数量を仮想通貨単位から円単位に変換する必要がある。非常に使いづらい。
        # とりあえずBTCの場合のみ対応...
        if order_type == OrderType.BUY:
            error_code, ticker_info = self.fetch_ticker_info(CryptoType.BTC)
            if error_code != WebAPIErrorCode.OK:
                print("warn: Coincheckとの通信に失敗しました。")  # todo: エラーログに吐き出す。
                return WebAPIErrorCode.FAIL_CONNECTION
            market_buy_amount = int(ticker_info.best_sell_order * volume) + 500 # 100円分バッファ
            params["market_buy_amount"] = market_buy_amount
            if market_buy_amount > 50000:
                print("error: 注文の数量が大きすぎます。プログラムを停止します。")  # todo: エラーログを吐き出す。
                sys.exit()

        timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        url = self.api_endpoint + path
        text = timestamp + url + json.dumps(params)
        sign = hmac.new(bytes(self.api_secret_key.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).\
            hexdigest()
        headers = {
            "ACCESS-KEY" : self.api_key,
            "ACCESS-NONCE" : timestamp,
            "ACCESS-SIGNATURE" : sign,
            'Content-Type': 'application/json',
        }
        try:
            json_data = requests.post(url, data=json.dumps(params), headers=headers).json()
        except:
            print("warn: Coincheckとの通信に失敗しました。")  # todo: エラーログに吐き出す。
            return WebAPIErrorCode.FAIL_CONNECTION
        if json_data["success"] == False:
            print("warn: Coincheckへの売買注文に失敗しました。")
            print("エラーメッセージは " + json_data["error"] + " です。")
            return WebAPIErrorCode.FAIL_ORDER

        print("info: Coincheckへの注文に成功しました。売買種別は " + order_type_str + ", 数量は "
              + str(volume) + " です。")
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
        path = "/api/accounts/balance"
        timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        url = self.api_endpoint + path
        text = timestamp + url
        sign = hmac.new(bytes(self.api_secret_key.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).\
            hexdigest()
        headers = {
            "ACCESS-KEY" : self.api_key,
            "ACCESS-NONCE" : timestamp,
            "ACCESS-SIGNATURE" : sign
        }
        try:
            json_data = requests.get(url, timeout=(self.connect_timeout, self.read_timeout), headers=headers).json()
        except:
            print("warn: Coincheckとの通信に失敗しました。")  # todo: エラーログに吐き出す。
            return WebAPIErrorCode.FAIL_CONNECTION, TickerInfo()
        if json_data["success"] == False:
            print("warn: Coincheckからの残高取得に失敗しました。")
            print("エラーメッセージは " + json_data["error"] + " です。")
            return WebAPIErrorCode.FAIL_CONNECTION

        jpy = json_data["jpy"]
        btc = json_data["btc"]
        eth = json_data["eth"]
        balance_info = BalanceInfo(jpy, btc, eth)
        return WebAPIErrorCode.OK, balance_info
