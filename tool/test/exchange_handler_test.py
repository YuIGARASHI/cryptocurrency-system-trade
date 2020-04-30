import unittest
from src.common.common import *
from src.web_handler.exchange_handler import *
from src.web_handler.bitflyer_handler import *
from src.web_handler.gmo_handler import *
from src.web_handler.coincheck_handler import *


class ExchangeHandlerTest(unittest.TestCase):
    '''
    ExchangeHandlerの単体テストクラス。
    '''
    def setUp(self):
        self.exchange_types = [ExchangeType.GMO, ExchangeType.BITFLYER, ExchangeType.COINCHECK]
        self.exchange_handler_class = {
            ExchangeType.GMO: GmoHandler,
            ExchangeType.BITFLYER: BitflyerHandler,
            ExchangeType.COINCHECK: CoincheckHandler
        }

    def test_init(self):
        '''
        コンストラクタのテスト。
        '''
        for exchange_type in self.exchange_types:
            handler = ExchangeHandler(exchange_type)
            self.assertIsInstance(handler, ExchangeHandler)
            self.assertIsInstance(handler.impl, self.exchange_handler_class[exchange_type])
            self.assertEqual(handler.impl.api_key, "")
            self.assertEqual(handler.impl.api_secret_key, "")
            self.assertEqual(handler.impl.connect_timeout, 3.0)
            self.assertEqual(handler.impl.read_timeout, 10.0)

    def test_fetch_ticker_info(self):
        for exchange_type in self.exchange_types:
            handler = ExchangeHandler(exchange_type)
            error_code, info = handler.fetch_ticker_info(CryptoType.BTC)
            self.assertTrue(error_code in [WebAPIErrorCode.OK, WebAPIErrorCode.FAIL_CONNECTION])
            self.assertIsInstance(info, TickerInfo)
            if error_code == WebAPIErrorCode.OK:
                # 無効値ではないことをチェック
                self.assertTrue(info != TickerInfo())


class GMOHandlerTest(unittest.TestCase):
    '''
    GMOHandlerの単体テストクラス。
    '''
    def setUp(self):
        self.handler = GmoHandler()

    def test_init(self):
        self.assertEqual(self.handler.api_private_endpoint, "https://api.coin.z.com/private")
        self.assertEqual(self.handler.api_public_endpoint, "https://api.coin.z.com/public")


class CoincheckHandlerTest(unittest.TestCase):
    '''
    CoincheckHandlerの単体テストクラス。
    '''
    def setUp(self):
        self.handler = CoincheckHandler()

    def test_init(self):
        self.assertEqual(self.handler.api_endpoint, "https://coincheck.com")

    def test_fetch_ticker_info(self):
        # 無効な仮想通貨種別でシステムエラーが発生する
        error_code, info = self.handler.fetch_ticker_info(CryptoType.ETH)
        self.assertIs(error_code, WebAPIErrorCode.SYS_ERROR)


if __name__=="__main__":
    unittest.main()