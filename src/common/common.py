'''
リポジトリ全体で共通して使うクラスや列挙型を定義する。
'''

class CryptoType(Enum):
    BTC = 0
    ETH = 1

class ExchangeType(Enum):
    BITFLYER = 0
    COINCHECK = 1
    GMO = 2

class PriceInfo:
    def __init__(self, timestamp, price, exchange):
        self.timestamp = timestamp # UTC
        self.price    = price      # JPY
        self.exchange = exchange   # 取引所
