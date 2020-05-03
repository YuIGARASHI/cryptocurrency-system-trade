from src.common.common import ExchangeType
from src.common.common import CryptoType
from src.common.common import FileAccessErrorCode
import json

class ConfigReader:
    @staticmethod
    def get_use_crypto_types(config_path="../config/config.json"):
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
        crypto_name_type_dic = {
            "BTC": CryptoType.BTC,
            "ETH": CryptoType.ETH,
            "BCH": CryptoType.BCH,
            "XRP": CryptoType.XRP,
            "LTC": CryptoType.LTC
        }
        file = None
        try:
            file = open(config_path, 'r')
            json_load = json.load(file)
            crypto_type_list = []
            for crypto_name in json_load["use_cryptocurrency"]:
                if not crypto_name_type_dic.get(crypto_name):
                    print("warn: 無効な仮想通貨名が指定されています。")  # todo: エラーログに吐き出す。
                    return FileAccessErrorCode.FAIL_READ, []
                crypto_type_list.append(crypto_name_type_dic[crypto_name])
            return FileAccessErrorCode.OK, crypto_type_list
        except:
            print("warn: コンフィグファイルのオープンに失敗しました。")  # todo: エラーログに吐き出す。
            return FileAccessErrorCode.FAIL_OPEN, []
        finally:
            if file:
                file.close()


    @staticmethod
    def get_use_exchange_types(config_path="../config/config.json"):
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
        exchange_name_type_dic = {
            "bitflyer": ExchangeType.BITFLYER,
            "coincheck": ExchangeType.COINCHECK,
            "gmo": ExchangeType.GMO,
            "zaif": ExchangeType.ZAIF,
            "huobi": ExchangeType.HUOBI_JP,
            "bitbank": ExchangeType.BITBANK,
            "liquid": ExchangeType.LIQUID
        }
        file = None
        try:
            file = open(config_path, 'r')
            json_load = json.load(file)
            exchange_type_list = []
            for exchange_name in json_load["use_exchange"]:
                if not exchange_name_type_dic.get(exchange_name):
                    print("warn: 無効な取引所名が指定されています。")  # todo: エラーログに吐き出す。
                    return FileAccessErrorCode.FAIL_READ, []
                exchange_type_list.append(exchange_name_type_dic[exchange_name])
            return FileAccessErrorCode.OK, exchange_type_list
        except:
            print("warn: コンフィグファイルのオープンに失敗しました。")  # todo: エラーログに吐き出す。
            return FileAccessErrorCode.FAIL_OPEN, []
        finally:
            if file:
                file.close()
