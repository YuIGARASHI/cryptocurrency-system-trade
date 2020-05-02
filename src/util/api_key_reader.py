from src.common.common import ExchangeType
from src.common.common import FileAccessErrorCode
import json


class APIKeyReader:
    @staticmethod
    def get_api_keys(exchange_type, file_path="../config/api_keys.json"):
        '''
        API Keyとsecret Keyを取得する。

        Parameters:
        -----------
        exchange_type : ExchangeType
            取引所種別。
        file_path : string
            API Keyファイルパス。

        Returns:
        --------
        error_code : FileAccessErrorCode
            ファイルアクセスエラーコード。
        api_key : string
            API key。
        api_secret_key : string
            API secret key。
        '''
        exchange_type_name_dic = {
            ExchangeType.BITFLYER: "bitflyer",
            ExchangeType.COINCHECK: "coincheck",
            ExchangeType.GMO: "gmo",
            ExchangeType.ZAIF: "zaif",
            ExchangeType.LIQUID: "liquid",
            ExchangeType.BITBANK: "bitbank",
            ExchangeType.HUOBI_JP: "huobi"
        }
        if not exchange_type_name_dic.get(exchange_type):
            print("warn: 無効な仮想通貨名が指定されています。")  # todo: エラーログに吐き出す。
            return FileAccessErrorCode.FAIL_READ, "", ""

        file = None
        try:
            file = open(file_path, 'r')
            json_load = json.load(file)
        except:
            print("warn: コンフィグファイルのオープンに失敗しました。")  # todo: エラーログに吐き出す。
            return FileAccessErrorCode.FAIL_OPEN, "", ""
        finally:
            if file:
                file.close()

        key_object = None
        try:
            key_object = json_load[exchange_type_name_dic[exchange_type]]
        except:
            print("warn: 指定された取引所のキーが存在しません。")
            return FileAccessErrorCode.FAIL_READ, "", ""
        return FileAccessErrorCode.OK, key_object["api_key"], key_object["api_secret_key"]
