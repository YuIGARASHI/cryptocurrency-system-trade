from src.common.common import CryptoType, TickerInfo, ExchangeType, BalanceInfo
from src.common.common import WebAPIErrorCode, FileAccessErrorCode
from src.util.api_key_reader import APIKeyReader
import requests
import sys
import hmac


class BitflyerHandler:
    '''
    BitflyerのAPIラッパークラス。
    https://lightning.bitflyer.com/docs
    各リクエストは500回/分のリミットがかけられているため注意。
    '''

    def __init__(self):
        self.api_key = ""
        self.api_secret_key = ""
        self.connect_timeout = 3.0 # サーバとのコネクトタイムアウト
        self.read_timeout = 10.0   # サーバからの読み込みタイムアウト
        self.api_endpoint = 'https://api.bitflyer.com'

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
        path = '/v1/ticker'
        url = self.api_endpoint + path
        params = {}
        if crypto_type == CryptoType.BTC:
            params["product_code"] = "BTC_JPY"
        elif crypto_type == CryptoType.ETH:
            params["product_code"] = "ETH_JPY"
        else:
            print("error: 無効なCryptoTypeが指定されています。プログラムを停止します。")  # todo: エラーログに吐き出す。
            sys.exit()

        try:
            json_data = requests.get(url, params=params, timeout=(self.connect_timeout, self.read_timeout)).json()
        except:
            print("warn: Bitflyterとの通信に失敗しました。")  # todo: エラーログに吐き出す。
            return WebAPIErrorCode.FAIL_CONNECTION, TickerInfo()
        best_sell_order = float(json_data["best_bid"])
        best_buy_order = float(json_data["best_ask"])
        best_sell_order_volume = float(json_data["best_bid_size"])
        best_buy_order_volume = float(json_data["best_ask_size"])
        ticker_info = TickerInfo(crypto_type, ExchangeType.BITFLYER, best_sell_order, best_buy_order,
                                 best_sell_order_volume, best_buy_order_volume)
        return WebAPIErrorCode.OK, ticker_info

    def load_api_key(self):
        '''
        API Key, Secret keyをロードする。
        注文を扱うメソッドを呼ぶ前には本メソッドを実行する必要がある。

        Returns:
        --------
        error_code : FileAccessErrorCode
            ファイルアクセスエラーコード。
        '''
        error_code, api_key, api_secret_key = APIKeyReader.get_api_keys(ExchangeType.BITFLYER)
        if error_code != FileAccessErrorCode.OK:
            return error_code
        self.api_key = api_key
        self.api_secret_key = api_secret_key
        return FileAccessErrorCode.OK

    def make_buy_market_order(self, crypto_type, volume):
        '''
        成行注文（買い）を出す。

        Parameters:
        -----------
        crypto_type : CryptoType
            仮想通貨種別。
        volume : float
            数量。単位は仮想通貨による。
        timeout : int
            注文をキャンセルするまでの時間。[秒]
            この時間内に約定しなかった場合は cancel_expired_order が呼ばれた時点でキャンセルされる。

        Returns:
        --------
        error_code : WebAPIErrorCode
            WebAPIエラーコード。
        '''
        return WebAPIErrorCode.OK  # todo: 実装する

    def make_sell_market_order(self, crypto_type, volume):
        '''
        成行注文（売り）を出す。

        Parameters:
        -----------
        crypto_type : CryptoType
            仮想通貨種別。
        volume : float
            数量。単位は仮想通貨による。
        timeout : int
            注文をキャンセルするまでの時間。[秒]
            この時間内に約定しなかった場合は cancel_expired_order が呼ばれた時点でキャンセルされる。

        Returns:
        --------
        error_code : WebAPIErrorCode
            WebAPIエラーコード。
        '''
        return WebAPIErrorCode.OK  # todo: 実装する

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
        return WebAPIErrorCode.OK, BalanceInfo()  # todo: 実装する

