from src.common.common import ExchangeType
from src.common.common import CryptoType
from src.common.common import FileAccessErrorCode
import json

class ConfigReader:
    @staticmethod
    def get_use_crypto_types():
        '''
        アービトラージで用いる仮想通貨種別一覧を取得する。

        Params:
        -------
        config_path : string
            コンフィグファイルパス。

        Returns:
        --------
        error_code : FileAccessErrorCode
            ファイルアクセスエラーコード。
        crypto_type_list : array-like (CryptoType)
            使用する仮想通貨種別一覧。
        '''
        try:
            json_open = open("../config/config.json", 'r')
            json_load = json.load(json_open)
            crypto_type_list = []
            for crypto_name in json_load["use_cryptocurrency"]:
                if crypto_name == "BTC":
                    crypto_type_list.append(CryptoType.BTC)
                elif crypto_name == "ETH":
                    crypto_type_list.append(CryptoType.ETH)
                else:
                    print("warn: 無効な仮想通貨名が指定されています。")  # todo: エラーログに吐き出す。
                    return FileAccessErrorCode.FAIL_READ, []
            return FileAccessErrorCode.OK, crypto_type_list
        except:
            print("warn: コンフィグファイルのオープンに失敗しました。")  # todo: エラーログに吐き出す。
            return FileAccessErrorCode.FAIL_OPEN, []


    @staticmethod
    def get_use_exchange_types():
        '''
        アービトラージで用いる取引所一覧を取得する。

        Parameters:
        -----------
        config_path : string
            コンフィグファイルパス。

        Returns:
        --------
        error_code : FileAccessErrorCode
            ファイルアクセスエラーコード。
        exchange_type_list : array-like (ExchangeType)
            使用する取引所一覧。
        '''
        try:
            json_open = open("../config/config.json", 'r')
            json_load = json.load(json_open)
            exchange_type_list = []
            for exchange_name in json_load["use_exchange"]:
                if exchange_name == "bitflyer":
                    exchange_type_list.append(ExchangeType.BITFLYER)
                elif exchange_name == "coincheck":
                    exchange_type_list.append(ExchangeType.COINCHECK)
                elif exchange_name == "gmo":
                    exchange_type_list.append(ExchangeType.GMO)
                else:
                    print("warn: 無効な取引所名が指定されています。")  # todo: エラーログに吐き出す。
                    return FileAccessErrorCode.FAIL_READ, []
            return FileAccessErrorCode.OK, exchange_type_list
        except:
            print("warn: コンフィグファイルのオープンに失敗しました。")  # todo: エラーログに吐き出す。
            return FileAccessErrorCode.FAIL_OPEN, []
