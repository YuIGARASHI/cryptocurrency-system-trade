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

class PriceInfo:
    def __init__(self, timestamp, price, exchange):
        self.timestamp = timestamp # UTC
        self.price    = price      # JPY
        self.exchange = exchange   # 取引所

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
    
    def fetch_price(self, crypto_type):
        return self.impl.fetch_price(crypto_type)

class BitflyerHandler():
    '''
    BitflyerのAPIラッパークラス。
    https://lightning.bitflyer.com/docs
    '''
    def __init__(self):
        pass

    def fetch_price(self, crypto_type):
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
        return PriceInfo(timestamp, price, ExchangeType.BITFLYER)

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
    price_info = bitflyer_handler.fetch_price(CryptoType.BTC)
    print(price_info.timestamp, price_info.price, price_info.exchange)
    
