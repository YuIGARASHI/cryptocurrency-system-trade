'''
システムトレードのエントリポイント。
'''

from src.common.common import CryptoType, TickerInfo, ExchangeType, WebAPIErrorCode
from src.web_handler.exchange_handler import ExchangeHandler
from src.util.config_reader import ConfigReader
from src.util.api_key_reader import APIKeyReader
import pprint

if __name__=='__main__':
    print("info: システムトレードを開始します。")

    handler = ExchangeHandler(ExchangeType.BITFLYER)
    handler.load_api_key()
    print(handler.impl.api_key)

    print("info: システムトレードを終了します。")