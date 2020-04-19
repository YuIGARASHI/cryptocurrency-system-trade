from src.common.common import CryptoType
from src.common.common import TickerInfo
from src.common.common import ExchangeType
from src.common.common import WebAPIErrorCode
from src.common.common import FileAccessErrorCode
from src.common.common import BalanceInfo
import requests
import sys


class CoincheckHandler:
    def __init__(self):
        pass

    @staticmethod
    def fetch_ticker_info(crypto_type):
        return WebAPIErrorCode.OK, TickerInfo()  # todo: 実装する

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
