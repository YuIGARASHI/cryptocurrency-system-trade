import unittest
from typing import Dict, Any

from src.util.api_key_reader import *


class APIKeyReaderTest(unittest.TestCase):
    '''
    APIKeyReaderの単体テストクラス。
    '''

    def setUp(self):
        self.exchange_list = [
            ExchangeType.BITFLYER,
            ExchangeType.COINCHECK,
            ExchangeType.GMO,
            ExchangeType.ZAIF,
            ExchangeType.LIQUID,
            ExchangeType.BITBANK,
            ExchangeType.HUOBI_JP
        ]
        self.exchange_name_map = {
            ExchangeType.BITFLYER: "bitflyer",
            ExchangeType.COINCHECK: "coincheck",
            ExchangeType.GMO: "gmo",
            ExchangeType.ZAIF: "zaif",
            ExchangeType.LIQUID: "liquid",
            ExchangeType.BITBANK: "bitbank",
            ExchangeType.HUOBI_JP: "huobi"
        }

    def test_get_api_keys_1(self):
        '''
        正常系テストケース。
        '''
        file_path = "config/api_keys_test1.json"
        for exchange in self.exchange_list:
            code, api_key, secret_key = APIKeyReader.get_api_keys(exchange, file_path)
            self.assertEqual(code, FileAccessErrorCode.OK)
            self.assertEqual(api_key, self.exchange_name_map[exchange] + "_api_key")
            self.assertEqual(secret_key, self.exchange_name_map[exchange] + "_secret_key")

    def test_get_api_keys_2(self):
        '''
        異常系テストケース。
        コンフィグファイルにZaifが存在しないにもかかわらず、ZaifのAPIキーを取得しようとした場合。
        '''
        file_path = "config/api_keys_test2.json"
        for exchange in self.exchange_list:
            code, api_key, secret_key = APIKeyReader.get_api_keys(exchange, file_path)
            if exchange == ExchangeType.ZAIF:
                self.assertEqual(code, FileAccessErrorCode.FAIL_READ)
            else:
                self.assertEqual(code, FileAccessErrorCode.OK)
                self.assertEqual(api_key, self.exchange_name_map[exchange] + "_api_key")
                self.assertEqual(secret_key, self.exchange_name_map[exchange] + "_secret_key")

    def test_get_api_keys_3(self):
        '''
        異常系テストケース。ファイルが存在しない場合。
        '''
        file_path = "config/api_keys_test3.json"
        for exchange in self.exchange_list:
            code, api_key, secret_key = APIKeyReader.get_api_keys(exchange, file_path)
            self.assertEqual(code, FileAccessErrorCode.FAIL_OPEN)

if __name__=="__main__":
    unittest.main()