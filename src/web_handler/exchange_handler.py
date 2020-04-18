from enum import Enum
import sys
import requests
import json
import codecs
import pprint
import time

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
