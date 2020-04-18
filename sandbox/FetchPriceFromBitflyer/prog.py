'''
bitflyerのAPIをつかっていろいろやってみる.
https://lightning.bitflyer.com/docs
'''

from enum import Enum
import sys
import requests
import json
import codecs
import pprint
import time

class TickerInfo:
    def __init__(self, timestamp, price, exchange, best_bid, best_ask, best_bid_volume, best_ask_volume):
        self.timestamp = timestamp             # UTC
        self.price    = price                  # JPY
        self.exchange = exchange               # 取引所
        self.best_bid = best_bid               # 売り
        self.best_ask = best_ask               # 買い
        self.best_bid_volume = best_bid_volume # 売りの量
        self.best_ask_volume = best_ask_volume # 買いの量

class CryptoType(Enum):
    BTC = 0
    ETH = 1
    
class ExchangeType(Enum):
    BITFLYER = 0
    COINCHECK = 1
    GMO = 2

class ExchangeHandler():
    '''
    取引所ごとのAPIの違いを吸収するラッパー。
    '''
    def __init__(self, exchange_type):
        if exchange_type == ExchangeType.BITFLYER:
            self.impl = BitflyerHandler()
        elif exchange_type == ExchangeType.COINCHECK:
            self.impl = CoincheckHandler()
        elif exchange_type == ExchangeType.GMO:
            self.impl = GmoHandler()
        else:
            print("error: Invalid exchange is specified!")
            sys.exit()
    
    def fetch_ticker(self, crypto_type):
        return self.impl.fetch_ticker(crypto_type)

class BitflyerHandler():
    '''
    BitflyerのAPIラッパークラス。
    https://lightning.bitflyer.com/docs
    '''
    def __init__(self):
        pass

    def fetch_ticker(self, crypto_type):
        '''
        現在時刻の指定された仮想通貨の価格を取得する.
        '''
        path = '/v1/ticker'
        url = 'https://api.bitflyer.com' + path
        params = {}
        if crypto_type == CryptoType.BTC:
            params["product_code"] = "BTC_JPY"
        elif crypto_type == CryptoType.ETH:
            params["product_code"] = "ETH_JPY"
        else:
            print("error: Invalid CryptoType is specified!")
            sys.exit()
        json_data = requests.get(url, params=params).json()
        
        timestamp = json_data["timestamp"].split(".")[0] # 秒の小数点以下切り捨て
        price     = str(json_data["ltp"]).split(".")[0]  # 小数点以下切り捨て
        best_bid  = str(json_data["best_bid"]).split(".")[0]  # 小数点以下切り捨て
        best_ask  = str(json_data["best_ask"]).split(".")[0]  # 小数点以下切り捨て
        best_bid_size  = str(json_data["best_bid_size"]).split(".")[0]  # 小数点以下切り捨て
        best_ask_size  = str(json_data["best_ask_size"]).split(".")[0]  # 小数点以下切り捨て
        return TickerInfo(timestamp, price, ExchangeType.BITFLYER, best_bid, best_ask, best_bid_size, best_ask_size)

class CoincheckHandler():
    '''
    CoincheckのAPIラッパークラス。
    '''
    pass

class GmoHandler():
    '''
    GMOビットコインのAPIラッパークラス。
    '''
    pass

if __name__=="__main__":
    bitflyer_handler = ExchangeHandler(ExchangeType.BITFLYER)
    ticker_info = bitflyer_handler.fetch_ticker(CryptoType.BTC)
    print(ticker_info.timestamp, ticker_info.price, ticker_info.exchange, ticker_info.best_bid, ticker_info.best_ask, ticker_info.best_bid_volume, ticker_info.best_ask_volume)
    
