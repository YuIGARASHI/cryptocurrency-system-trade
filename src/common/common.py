'''
リポジトリ全体で共通して使うクラスや列挙型を定義する。
'''
from enum import Enum


class CryptoType(Enum):
    '''
    仮想通貨種別。
    '''
    INVALID = 0
    BTC = 1
    ETH = 2


class BalanceInfo(Enum):
    '''
    取引所の残高情報。
    '''
    def __init__(self, YEN=0, BTC=0, ETH=0):
        self.YEN = YEN
        self.BTC = BTC
        self.ETH = ETH


class ExchangeType(Enum):
    '''
    取引所種別。

    '''
    INVALID = 0
    BITFLYER = 1
    COINCHECK = 2
    GMO = 3


class WebAPIErrorCode(Enum):
    '''
    WebAPIエラーコード。
    '''
    OK = 0,              # 呼び出し成功
    FAIL_CONNECTION = 1  # 通信失敗


class FileAccessErrorCode(Enum):
    '''
    ローカルファイルアクセスエラーコード。
    '''
    OK = 0,         # 成功
    FAIL_OPEN = 1,  # ファイルオープン失敗
    FAIL_READ = 2,  # ファイル読み込み失敗
    FAIL_WRITE = 3  # ファイル書き出し失敗


class TickerInfo:
    def __init__(self, crypto_type=CryptoType.INVALID, timestamp="", price=-1, exchange=ExchangeType.INVALID,
                 best_bid=-1, best_ask=-1, best_bid_volume=-1, best_ask_volume=-1):
        '''
        Parameters:
        -----------
        crypto_type : CryptoType
            仮想通貨種別。
        timestamp : string
            UTCタイムスタンプ。
        price : int
            仮想通貨価格。[円]
        exchange : ExchangeType
            取引所種別。
        best_bid : int
            売り注文の最安値。[円]
        best_ask : int
            買い注文の最高値。[円]
        best_bid_volume : int
            最安の売り注文の数量。単位は仮想通貨による。
        best_ask_volume : int
            最高の買い注文の数量。単位は仮想通貨による。
        '''
        self.crypto_type = crypto_type
        self.timestamp = timestamp
        self.price = price
        self.exchange = exchange
        self.best_bid = best_bid
        self.best_ask = best_ask
        self.best_bid_volume = best_bid_volume
        self.best_ask_volume = best_ask_volume
