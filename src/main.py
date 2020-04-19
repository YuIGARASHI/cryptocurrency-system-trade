'''
システムトレードのエントリポイント。
'''

from src.common.common import CryptoType, TickerInfo, ExchangeType, WebAPIErrorCode
from src.web_handler.exchange_handler import ExchangeHandler

if __name__=='__main__':
    print("info: システムトレードを開始します。")

    bitflyer_handler = ExchangeHandler(ExchangeType.BITFLYER)
    error_code, ticker_info = bitflyer_handler.fetch_ticker_info(CryptoType.BTC)
    assert error_code, WebAPIErrorCode.OK

    print("info: システムトレードを終了します。")