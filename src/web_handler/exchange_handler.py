import sys
from src.common.common import CryptoType, TickerInfo, ExchangeType
from src.web_handler.bitflyer_handler import BitflyerHandler
from src.web_handler.coincheck_handler import CoincheckHandler
from src.web_handler.gmo_handler import GmoHandler


class ExchangeHandler:
    '''
    取引所ごとのAPIの違いを吸収するラッパークラス。
    '''
    def __init__(self, exchange_type):
        '''
        仮想通貨の取引所を登録する。
        想定していない取引所が指定された場合はプログラムを停止する。

        Parameters:
        -----------
        exchange_type : ExchangeType
            仮想通貨取引所の種類。
        '''
        if exchange_type == ExchangeType.BITFLYER:
            self.impl = BitflyerHandler()
        elif exchange_type == ExchangeType.COINCHECK:
            self.impl = CoincheckHandler()
        elif exchange_type == ExchangeType.GMO:
            self.impl = GmoHandler()
        else:
            print("error: 無効なExchangeTypeが指定されています。プログラムを停止します。")  # todo:エラーログに吐き出す
            sys.exit()
    
    def fetch_ticker_info(self, crypto_type):
        '''
        板情報オブジェクトを取得する。
        想定していない仮想通貨が指定された場合はプログラムを停止する。

        Parameters:
        -----------
        crypto_type : CryptoType
            仮想通貨の種類。

        Returns:
        --------
        error_code : WebAPIErrorCode
        　WebAPIエラーコード。
        ticker_info : TickerInfo
        　板情報オブジェクト。
        '''
        return self.impl.fetch_ticker_info(crypto_type)

    def load_api_key(self):
        '''
        API Key, Secret keyをロードする。
        注文を扱うメソッドを呼ぶ前には本メソッドを実行する必要がある。

        Returns:
        --------
        error_code : FileAccessErrorCode
            ファイルアクセスエラーコード。
        '''
        self.impl.load_api_key()

    def make_ask_order(self, crypto_type, price, volume, timeout):
        '''
        売り注文を出す。
        price > 0 であれば指値注文、price <= 0 であれば成り行き注文を出す。

        Parameters:
        -----------
        crypto_type : CryptoType
            仮想通貨種別。
        price : int
            指値。[円]
        volume : int
            数量。単位は仮想通貨による。
        timeout : int
            注文をキャンセルするまでの時間。[秒]
            この時間内に約定しなかった場合は cancel_expired_order が呼ばれた時点でキャンセルされる。

        Returns:
        --------
        error_code : WebAPIErrorCode
            WebAPIエラーコード。
        '''
        self.impl.make_bid_order(crypto_type, price, volume, timeout)

    def make_bid_order(self, crypto_type, price, volume, timeout):
        '''
        買い注文を出す。
        price > 0 であれば指値注文、price <= 0 であれば成り行き注文を出す。

        Parameters:
        -----------
        crypto_type : CryptoType
            仮想通貨種別。
        price : int
            指値。[円]
        volume : int
            数量。単位は仮想通貨による。
        timeout : int
            注文をキャンセルするまでの時間。[秒]
            この時間内に約定しなかった場合は cancel_expired_order が呼ばれた時点でキャンセルされる。

        Returns:
        --------
        error_code : WebAPIErrorCode
            WebAPIエラーコード。
        '''
        self.impl.make_bid_order(crypto_type, price, volume, timeout)

    def cancel_expired_order(self):
        '''
        期限切れの注文をキャンセルする。

        Returns:
        --------
        error_code : WebAPIErrorCode
            WebAPIエラーコード。
        '''
        self.impl.cancel_expired_order()

    def fetch_balance(self):
        '''
        取引所に預けている残高を取得する。

        Returns:
        --------
        error_code : WebAPIErrorCode
            WebAPIエラーコード。
        balance_info : BalanceInfo
            残高情報。
        '''
        self.impl.fetch_balance()
