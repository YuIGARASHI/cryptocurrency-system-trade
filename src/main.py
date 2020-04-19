'''
システムトレードのエントリポイント。
'''

from src.common.common import CryptoType, TickerInfo, ExchangeType, WebAPIErrorCode
from src.web_handler.exchange_handler import ExchangeHandler
from src.util.config_reader import ConfigReader
import pprint

if __name__=='__main__':
    print("info: システムトレードを開始します。")

    error_code, use_crypto_types = ConfigReader.GetUseCryptoTypes("../config/config.json")
    pprint.pprint(use_crypto_types)
    error_code, use_exchange_types = ConfigReader.GetUseExchangeTypes("../config/config.json")
    pprint.pprint(use_exchange_types)

    print("info: システムトレードを終了します。")