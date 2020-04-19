from src.common.common import CryptoType
from src.common.common import TickerInfo
from src.common.common import ExchangeType
from src.common.common import WebAPIErrorCode
from src.common.common import FileAccessErrorCode
from src.common.common import BalanceInfo
import requests
import sys


class BitflyerHandler:
    '''
    BitflyerのAPIラッパークラス。
    https://lightning.bitflyer.com/docs
    '''

    def __init__(self):
        pass

    @staticmethod
    def fetch_ticker_info(crypto_type):
        path = '/v1/ticker'
        url = 'https://api.bitflyer.com' + path
        params = {}
        if crypto_type == CryptoType.BTC:
            params["product_code"] = "BTC_JPY"
        elif crypto_type == CryptoType.ETH:
            params["product_code"] = "ETH_JPY"
        else:
            print("error: 無効なCryptoTypeが指定されています。プログラムを停止します。")  # todo: エラーログに吐き出す。
            sys.exit()

        try:
            json_data = requests.get(url, params=params).json()
            timestamp = json_data["timestamp"].split(".")[0]  # 秒の小数点以下切り捨て
            price = str(json_data["ltp"]).split(".")[0]  # 小数点以下切り捨て
            best_bid = str(json_data["best_bid"]).split(".")[0]  # 小数点以下切り捨て
            best_ask = str(json_data["best_ask"]).split(".")[0]  # 小数点以下切り捨て
            best_bid_volume = str(json_data["best_bid_size"]).split(".")[0]  # 小数点以下切り捨て
            best_ask_volume = str(json_data["best_ask_size"]).split(".")[0]  # 小数点以下切り捨て
            ticker_info = TickerInfo(crypto_type, timestamp, price, ExchangeType.BITFLYER,
                                     best_bid, best_ask, best_bid_volume, best_ask_volume)
            return WebAPIErrorCode.OK, ticker_info
        except:
            print("warn: Bitflyterとの通信に失敗しました。")  # todo: エラーログに吐き出す。
            return WebAPIErrorCode.FAIL_CONNECTION, TickerInfo()

    def load_api_key(self):
        return FileAccessErrorCode.OK  # todo: 実装する

    def make_bid_limit_order(self, crypto_type, price, volume, timeout):
        return WebAPIErrorCode.OK  # todo: 実装する

    def make_ask_limit_order(self, crypto_type, price, volume, timeout):
        return WebAPIErrorCode.OK  # todo: 実装する

    def make_bid_market_order(self, crypto_type, volume, timeout):
        return WebAPIErrorCode.OK  # todo: 実装する

    def make_ask_market_order(self, crypto_type, volume, timeout):
        return WebAPIErrorCode.OK  # todo: 実装する

    def cancel_expired_order(self):
        return FileAccessErrorCode.OK  # todo: 実装する

    def fetch_balance(self):
        return WebAPIErrorCode.OK, BalanceInfo()  # todo: 実装する
