import unittest
from src.util.config_reader import *

class ConfigReaderTest(unittest.TestCase):
    '''
    ConfigReaderの単体テストクラス。
    '''

    def test_get_use_crypto_types_1(self):
        '''
        正常系テストケース。
        '''
        code, crypto_list = ConfigReader.get_use_crypto_types("config/config_test1.json")
        self.assertEqual(code, FileAccessErrorCode.OK)
        expected_crypto_list = [
            CryptoType.BTC,
            CryptoType.ETH,
            CryptoType.BCH,
            CryptoType.XRP,
            CryptoType.LTC
        ]
        self.assertEqual(crypto_list, expected_crypto_list)

    def test_get_use_crypto_types_2(self):
        '''
        正常系テストケース。
        '''
        code, crypto_list = ConfigReader.get_use_crypto_types("config/config_test2.json")
        self.assertEqual(code, FileAccessErrorCode.OK)
        expected_crypto_list = [
            CryptoType.BTC,
            CryptoType.BCH,
        ]
        self.assertEqual(crypto_list, expected_crypto_list)

    def test_get_use_crypto_types_3(self):
        '''
        異常系テストケース。無効な仮想通貨名称が記載されているケース。
        '''
        code, crypto_list = ConfigReader.get_use_crypto_types("config/config_test3.json")
        self.assertEqual(code, FileAccessErrorCode.FAIL_READ)

    def test_get_use_crypto_types_4(self):
        '''
        異常系テストケース。ファイルが存在しないケース。
        '''
        code, crypto_list = ConfigReader.get_use_crypto_types("config/config_test4.json")
        self.assertEqual(code, FileAccessErrorCode.FAIL_OPEN)

    def test_get_use_exchange_types_1(self):
        '''
        正常系テストケース。
        '''
        code, exchange_list = ConfigReader.get_use_exchange_types("config/config_test1.json")
        self.assertEqual(code, FileAccessErrorCode.OK)
        expected_exchange_list = [
            ExchangeType.GMO,
            ExchangeType.COINCHECK,
            ExchangeType.BITFLYER,
            ExchangeType.ZAIF,
            ExchangeType.HUOBI_JP,
            ExchangeType.BITBANK,
            ExchangeType.LIQUID
        ]
        self.assertEqual(exchange_list, expected_exchange_list)

    def test_get_use_exchange_types_2(self):
        '''
        正常系テストケース。
        '''
        code, exchange_list = ConfigReader.get_use_exchange_types("config/config_test2.json")
        self.assertEqual(code, FileAccessErrorCode.OK)
        expected_exchange_list = [
            ExchangeType.GMO,
            ExchangeType.BITFLYER,
            ExchangeType.ZAIF,
            ExchangeType.LIQUID
        ]
        self.assertEqual(exchange_list, expected_exchange_list)

    def test_get_use_exchange_types_3(self):
        '''
        異常系テストケース。無効な取引所が指定されているケース。
        '''
        code, exchange_list = ConfigReader.get_use_exchange_types("config/config_test3.json")
        self.assertEqual(code, FileAccessErrorCode.FAIL_READ)

    def test_get_use_exchange_types_4(self):
        '''
        異常系テストケース。ファイルが存在しないケース。
        '''
        code, exchange_list = ConfigReader.get_use_exchange_types("config/config_test4.json")
        self.assertEqual(code, FileAccessErrorCode.FAIL_OPEN)


if __name__=="__main__":
    unittest.main()