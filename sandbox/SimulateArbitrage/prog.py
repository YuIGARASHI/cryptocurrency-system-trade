'''
システムトレードのエントリポイント。
'''

from src.common.common import CryptoType, TickerInfo, ExchangeType, WebAPIErrorCode
from src.web_handler.exchange_handler import ExchangeHandler
from src.util.config_reader import ConfigReader
from src.util.api_key_reader import APIKeyReader
import pprint
import time
import codecs
from itertools import permutations
import math

exchange_name_map = {
    ExchangeType.LIQUID: "LQ",
    ExchangeType.HUOBI_JP: "HU",
    ExchangeType.GMO: "GMO",
    ExchangeType.BITBANK: "BB",
    ExchangeType.ZAIF: "ZA"
}
crypto_name_map = {
    CryptoType.BTC: "BTC",
    CryptoType.XRP: "XRP",
    CryptoType.BCH: "BCH",
    CryptoType.ETH: "ETH",
    CryptoType.LTC: "LTC"
}

def similate_arbitrage(crypto_type, exchanges, ofs):
    handler_map = {}
    for exchange in exchanges:
        handler_map[exchange] = ExchangeHandler(exchange)
    # 見出し出力
    headline_str = ""
    for (ex1, ex2) in permutations(exchanges, 2):
        headline_str += exchange_name_map[ex1]+"_"+exchange_name_map[ex2]+","
    print(headline_str)
    ofs.write(headline_str+"\n")
    while True:
        error_flag = True
        sell_map = {}
        buy_map = {}
        line_str = ""
        for exchange in exchanges:
            code, info = handler_map[exchange].fetch_ticker_info(crypto_type)
            sell_map[exchange] = info.best_sell_order
            buy_map[exchange] = info.best_buy_order
            error_flag = error_flag and (code == WebAPIErrorCode.OK)
        if not error_flag: # 取引所のうちひとつでもエラーならcontinue
            time.sleep(2)
            continue
        for (ex1, ex2) in permutations(exchanges, 2):
            # 10万円当たりの利益に変換
            line_str += str(math.floor((buy_map[ex1] - sell_map[ex2]) * (100000 / sell_map[ex2])))+","
        print(line_str)
        ofs.write(line_str+"\n")
        ofs.flush()
        time.sleep(2)

if __name__=='__main__':
    exchanges = [
        #ExchangeType.ZAIF,
        ExchangeType.BITBANK,
        ExchangeType.GMO,
        ExchangeType.HUOBI_JP,
        ExchangeType.LIQUID
    ]
    crypto_type = CryptoType.XRP
    ofs = codecs.open("data/result_" + crypto_name_map[crypto_type] + ".csv", "w")
    similate_arbitrage(crypto_type, exchanges, ofs)