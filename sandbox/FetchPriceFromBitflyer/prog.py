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

def fetch_price_from_bitflyer(crypto_type):
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
    price     = str(json_data["ltp"]).split(".")[0] # 小数点以下切り捨て
    return PriceInfo(timestamp, price)

def fetch_price_from_coincheck(crypto_type):
    pass

def fetch_price_form_gmo(crypto_type):
    pass

if __name__=="__main__":
    pass
        

    
    
