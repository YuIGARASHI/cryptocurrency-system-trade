import sys
sys.path.append('../../')

from src.common.common import CryptoType, TickerInfo, ExchangeType, WebAPIErrorCode
from src.web_handler.exchange_handler import ExchangeHandler
from src.util.config_reader import ConfigReader
from src.util.api_key_reader import APIKeyReader
import pprint
import time
import codecs
import math

initial_balance = -9999

def check_balance(btc, btc_handler, yen, yen_handler):
    code, btc_balance_info = btc_handler.fetch_balance()
    if code != WebAPIErrorCode.OK:
        print("取引所に繋がりませんでした")
        return False
    code, yen_balance_info = yen_handler.fetch_balance()
    if code != WebAPIErrorCode.OK:
        print("取引所に繋がりませんでした")
        return False
    if float(btc_balance_info.BTC) < float(btc):
        print("BTC残高が足りませんでした")
        return False
    if float(yen_balance_info.YEN) < float(yen):
        print("YEN残高が足りませんでした")
        return False
    return True


def check_price_for_arbitrage(bb_handler, liquid_handler):
    '''
    2つのBTCの価格を確認して、取引したほうがよさそうか返す。
    現状かなりやっつけ実装なのでちゃんとリファクタする。
    Returns:
    --------
    should_order : bool
        取引を出したほうがよさそうか否か。よさそうな場合True。
    buy_exchange_type : ExchangeType
        買いの注文を出すべき取引所。
    sell_exchange_type : ExchangeType
        売りの注文を出すべき取引所。
    volume : float
        売買数量
    '''
    error_code, bb_ticker_info = bb_handler.fetch_ticker_info(CryptoType.BTC)
    if error_code != WebAPIErrorCode.OK:
        return False, ExchangeType.INVALID, ExchangeType.INVALID, 0
    error_code, liquid_ticker_info = liquid_handler.fetch_ticker_info(CryptoType.BTC)
    if error_code != WebAPIErrorCode.OK:
        return False, ExchangeType.INVALID, ExchangeType.INVALID, 0
    error_code, bb_balance_info = bb_handler.fetch_balance()
    if error_code != WebAPIErrorCode.OK:
        return False, ExchangeType.INVALID, ExchangeType.INVALID, 0
    error_code, liquid_balance_info = liquid_handler.fetch_balance()
    if error_code != WebAPIErrorCode.OK:
        return False, ExchangeType.INVALID, ExchangeType.INVALID, 0

    # 残高を確認して、しきい値を算出
    liquid_buy_threshold = 1500
    bb_buy_threshold = 500
    if liquid_balance_info.BTC >= 0.09:
        liquid_buy_threshold = 2000
        bb_buy_threshold = -500
    elif bb_balance_info.BTC >= 0.09:
        liquid_buy_threshold = 500
        bb_buy_threshold = 1000
    elif liquid_balance_info.BTC < bb_balance_info.BTC:
        liquid_buy_threshold = 1000
    elif bb_balance_info.BTC < liquid_balance_info.BTC:
        bb_buy_threshold = 0

    # 価格差があるかチェック
    # Liquidで買って、BBで売るパターン
    diff = bb_ticker_info.best_buy_order - liquid_ticker_info.best_sell_order
    print("Liquid買い: " + str(diff))
    if  diff >= liquid_buy_threshold:
        if min(bb_ticker_info.best_buy_order_volume, liquid_ticker_info.best_sell_order_volume) < 0.01:
            False, ExchangeType.INVALID, ExchangeType.INVALID, 0
        volume = 0.01 # いったん固定でやってみる
        # 残高チェック
        need_yen = volume * bb_ticker_info.best_buy_order
        if not check_balance(btc=volume, btc_handler=bb_handler, yen=need_yen, yen_handler=liquid_handler):
            return False, ExchangeType.INVALID, ExchangeType.INVALID, 0
        return True, ExchangeType.LIQUID, ExchangeType.BITBANK, volume

    # BBで買って、Liquidで売るパターン
    diff = liquid_ticker_info.best_buy_order - bb_ticker_info.best_sell_order
    print("BB買い: " + str(diff))
    if diff >= bb_buy_threshold:
        if min(liquid_ticker_info.best_buy_order_volume, bb_ticker_info.best_sell_order_volume) < 0.01:
            return False, ExchangeType.INVALID, ExchangeType.INVALID, 0
        volume = 0.01 # いったん固定でやってみる
        need_yen = volume * liquid_ticker_info.best_buy_order
        if not check_balance(btc=volume, btc_handler=liquid_handler, yen=need_yen, yen_handler=bb_handler):
            return False, ExchangeType.INVALID, ExchangeType.INVALID, 0
        return True, ExchangeType.BITBANK, ExchangeType.LIQUID, volume

    return False, ExchangeType.INVALID, ExchangeType.INVALID, 0



def make_order_for_arbitrage(bb_handler, liquid_handler, buy_exchange, sell_exchange, volume):
    '''
    実際に売買の注文を出す。
    '''

    # BBで買って、Liquidで売るパターン
    if buy_exchange == ExchangeType.BITBANK and sell_exchange == ExchangeType.LIQUID:
        error_code = bb_handler.make_buy_market_order(CryptoType.BTC, volume)
        if error_code != WebAPIErrorCode.OK:
            return
        liquid_handler.make_sell_market_order(CryptoType.BTC, volume) # こっちだけ失敗した場合どうしよう

    # Liquidで買って、BBで売るパターン
    if buy_exchange == ExchangeType.LIQUID and sell_exchange == ExchangeType.BITBANK:
        error_code = liquid_handler.make_buy_market_order(CryptoType.BTC, volume)
        if error_code != WebAPIErrorCode.OK:
            return
        bb_handler.make_sell_market_order(CryptoType.BTC, volume) # こっちだけ失敗した場合どうしよう

def print_total_balance(bb_handler, liquid_handler, initial_balance):
    '''
    現在の資産残高を表示する。
    リファレンス実装なので、とりあえずBTCのみ。
    '''
    error_code, bb_balance = bb_handler.fetch_balance()
    if error_code != WebAPIErrorCode.OK:
        return
    error_code, liquid_balance = liquid_handler.fetch_balance()
    if error_code != WebAPIErrorCode.OK:
        return
    error_code, bb_ticker_info = bb_handler.fetch_ticker_info(CryptoType.BTC)
    if error_code != WebAPIErrorCode.OK:
        return
    error_code, liquid_ticker_info = liquid_handler.fetch_ticker_info(CryptoType.BTC)
    if error_code != WebAPIErrorCode.OK:
        return
    bb_total_balance = float(bb_balance.YEN) + float(bb_balance.BTC) * float(bb_ticker_info.best_buy_order)
    liquid_total_balance = float(liquid_balance.YEN) + float(liquid_balance.BTC) * float(liquid_ticker_info.best_buy_order)
    diff = math.floor(float(math.floor(float(bb_balance.YEN) + float(liquid_balance.YEN))) - float(initial_balance))
    print(">>>>>> 合計 " + "{:,}".format(math.floor(bb_total_balance + liquid_total_balance)) +
          " >>>>> 現金 " + "{:,}".format(math.floor(float(bb_balance.YEN) + float(liquid_balance.YEN))) + " (" + str(diff) + ") " +
          " >>>>> BTC "  + str(float(bb_balance.BTC) + float(liquid_balance.BTC)) +
          "( BB: " + str(bb_balance.BTC) +", Liquid: " + str(liquid_balance.BTC) + " )")
    # if bb_total_balance+liquid_total_balance < 210000:
    #     print("資産状況がしきい値を下回ったのでアービトラージを停止します。")
    #     sys.exit()



if __name__=='__main__':
    print("info: システムトレードを開始します。")

    # 初期化
    bb_handler = ExchangeHandler(ExchangeType.BITBANK)
    bb_handler.load_api_key()
    liquid_handler = ExchangeHandler(ExchangeType.LIQUID)
    liquid_handler.load_api_key()

    # 初期残高の計算
    initial_balance = -9999
    error_code, bb_balance = bb_handler.fetch_balance()
    if error_code != WebAPIErrorCode.OK:
        sys.exit()
    error_code, liquid_balance = liquid_handler.fetch_balance()
    if error_code != WebAPIErrorCode.OK:
        sys.exit()
    initial_balance = math.floor(float(bb_balance.YEN) + float(liquid_balance.YEN))

    # メインループ
    timespan = 2 # 秒
    time.sleep(timespan)
    while True:
        print_total_balance(bb_handler=bb_handler, liquid_handler=liquid_handler, initial_balance=initial_balance)

        should_order, buy_exchange_type, sell_exchange_type, volume = \
            check_price_for_arbitrage(bb_handler=bb_handler, liquid_handler=liquid_handler)
        print()
        if not should_order:
            time.sleep(timespan)
            continue
        print("!! アービトラージを実施します !!")
        make_order_for_arbitrage(bb_handler=bb_handler, liquid_handler=liquid_handler,
                                 buy_exchange=buy_exchange_type, sell_exchange=sell_exchange_type, volume=volume)
        time.sleep(timespan)


    print("info: システムトレードを終了します。")