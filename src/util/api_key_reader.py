from src.common.common import ExchangeType
from src.common.common import FileAccessErrorCode
import json


class APIKeyReader:
    @staticmethod
    def get_api_keys(exchange_type):
        '''
        API Keyとsecret Keyを取得する。

        Parameters:
        -----------
        exchange_type : ExchangeType
            取引所種別。

        Returns:
        --------
        error_code : FileAccessErrorCode
            ファイルアクセスエラーコード。
        api_key : string
            API key。
        api_secret_key : string
            API secret key。
        '''
        try:
            json_open = open("../config/api_keys.json", 'r')
            json_load = json.load(json_open)
            key_object = None
            if exchange_type == ExchangeType.BITFLYER:
                key_object = json_load["bitflyer"]
            elif exchange_type == ExchangeType.COINCHECK:
                key_object = json_load["coincheck"]
            elif exchange_type == ExchangeType.GMO:
                key_object = json_load["gmo"]
            else:
                print("warn: 無効な仮想通貨名が指定されています。")  # todo: エラーログに吐き出す。
                return FileAccessErrorCode.FAIL_READ, "", ""
            return FileAccessErrorCode.OK, key_object["api_key"], key_object["api_secret_key"]
        except:
            print("warn: コンフィグファイルのオープンに失敗しました。")  # todo: エラーログに吐き出す。
            return FileAccessErrorCode.FAIL_OPEN, "", ""