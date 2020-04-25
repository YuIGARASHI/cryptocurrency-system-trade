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


class BalanceInfo:
    '''
    取引所の残高情報。
    '''
    def __init__(self, yen=0, btc=0, eth=0):
        self.YEN = yen
        self.BTC = btc
        self.ETH = eth

    def print_myself(self):
        print(">>>>>>>>>> BalanceInfo <<<<<<<<<<")
        print("YEN: " + str(self.YEN))
        print("BTC: " + str(self.BTC))
        print("ETH: " + str(self.ETH))


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
    FAIL_ORDER = 2       # 注文失敗


class FileAccessErrorCode(Enum):
    '''
    ローカルファイルアクセスエラーコード。
    '''
    OK = 0,         # 成功
    FAIL_OPEN = 1,  # ファイルオープン失敗
    FAIL_READ = 2,  # ファイル読み込み失敗
    FAIL_WRITE = 3  # ファイル書き出し失敗

class OrderType(Enum):
    '''
    注文の売買種別。
    '''
    INVALID = 0  # 無効値
    BUY = 1,     # 売り
    SELL = 2     # 買い

class TickerInfo:
    def __init__(self, crypto_type=CryptoType.INVALID, exchange=ExchangeType.INVALID,
                 best_sell_order=-1, best_buy_order=-1, best_sell_order_volume=-1, best_buy_order_volume=-1):
        '''
        Parameters:
        -----------
        crypto_type : CryptoType
            仮想通貨種別。
        exchange : ExchangeType
            取引所種別。
        best_sell_order : float
            現在板に出ている売り注文の最安値。[円]
        best_buy_order : float
            現在板に出ている買い注文の最高値。[円]
        best_sell_order_volume : float
            現在板に出ている最安の売り注文の数量。単位は仮想通貨による。
        best_buy_order_volume : float
            現在板に出ている最高の買い注文の数量。単位は仮想通貨による。
        '''
        self.crypto_type = crypto_type
        self.exchange = exchange
        self.best_sell_order = best_sell_order
        self.best_buy_order = best_buy_order
        self.best_sell_order_volume = best_sell_order_volume
        self.best_buy_order_volume = best_buy_order_volume

    def print_myself(self):
        print(">>>>>>>>>> TickerInfo <<<<<<<<<<")
        print("crypt_type: " + str(self.crypto_type))
        print("exchange: " + str(self.exchange))
        print("best_sell_order: " +str(self.best_sell_order))
        print("best_buy_order: " + str(self.best_buy_order))
        print("best_sell_order_volume: " + str(self.best_sell_order_volume))
        print("best_buy_order_volume: " + str(self.best_buy_order_volume))
