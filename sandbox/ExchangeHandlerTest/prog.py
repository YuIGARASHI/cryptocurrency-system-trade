import sys
sys.path.append('../../')

from src.common.common import CryptoType, TickerInfo, ExchangeType, WebAPIErrorCode
from src.web_handler.exchange_handler import ExchangeHandler
from zaifapi import ZaifTradeApi

if __name__=="__main__":
    zaif_handler = ExchangeHandler(ExchangeType.ZAIF)
    zaif_handler.load_api_key()
    code, balance = zaif_handler.fetch_balance()
    zaif_handler.make_buy_market_order(CryptoType.BTC, volume=0.01)