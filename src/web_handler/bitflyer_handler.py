from src.common.common import CryptoType, TickerInfo, ExchangeType, BalanceInfo
from src.common.common import WebAPIErrorCode, FileAccessErrorCode
from src.util.api_key_reader import APIKeyReader
import requests
import sys
import hmac


class BitflyerHandler:
    '''
    BitflyerのAPIラッパークラス。
    https://lightning.bitflyer.com/docs
    各リクエストは500回/分のリミットがかけられているため注意。
    '''

    def __init__(self):
        self.api_key = ""
        self.api_secret_key = ""
        self.connect_timeout = 3.0 # サーバとのコネクトタイムアウト
        self.read_timeout = 10.0   # サーバからの読み込みタイムアウト
        self.api_endpoint = 'https://api.bitflyer.com'

    def fetch_ticker_info(self, crypto_type):
        path = '/v1/ticker'
        url = self.api_endpoint + path
        params = {}
        if crypto_type == CryptoType.BTC:
            params["product_code"] = "BTC_JPY"
        elif crypto_type == CryptoType.ETH:
            params["product_code"] = "ETH_JPY"
        else:
            print("error: 無効なCryptoTypeが指定されています。プログラムを停止します。")  # todo: エラーログに吐き出す。
            sys.exit()

        try:
            json_data = requests.get(url, params=params, timeout=(self.connect_timeout, self.read_timeout)).json()
        except:
            print("warn: Bitflyterとの通信に失敗しました。")  # todo: エラーログに吐き出す。
            return WebAPIErrorCode.FAIL_CONNECTION, TickerInfo()
        best_sell_order = float(json_data["best_bid"])
        best_buy_order = float(json_data["best_ask"])
        best_sell_order_volume = float(json_data["best_bid_size"])
        best_buy_order_volume = float(json_data["best_ask_size"])
        ticker_info = TickerInfo(crypto_type, ExchangeType.BITFLYER, best_sell_order, best_buy_order,
                                 best_sell_order_volume, best_buy_order_volume)
        return WebAPIErrorCode.OK, ticker_info

    def load_api_key(self):
        error_code, api_key, api_secret_key = APIKeyReader.get_api_keys(ExchangeType.BITFLYER)
        if error_code != FileAccessErrorCode.OK:
            return error_code
        self.api_key = api_key
        self.api_secret_key = api_secret_key
        return FileAccessErrorCode.OK

    def make_buy_market_order(self, crypto_type, volume):
        return WebAPIErrorCode.OK  # todo: 実装する

    def make_sell_market_order(self, crypto_type, volume):
        return WebAPIErrorCode.OK  # todo: 実装する

    def fetch_balance(self):
        '''
        このへんが参考になりそう。
        https://www.doraxdora.com/blog/2018/03/14/4181/
        '''
        return WebAPIErrorCode.OK, BalanceInfo()  # todo: 実装する

