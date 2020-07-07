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
import datetime

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


def check_price_for_arbitrage(gmo_handler, liquid_handler):
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
    error_code, gmo_ticker_info = gmo_handler.fetch_ticker_info(CryptoType.BTC)
    if error_code != WebAPIErrorCode.OK:
        return False, ExchangeType.INVALID, ExchangeType.INVALID, 0
    error_code, liquid_ticker_info = liquid_handler.fetch_ticker_info(CryptoType.BTC)
    if error_code != WebAPIErrorCode.OK:
        return False, ExchangeType.INVALID, ExchangeType.INVALID, 0
    error_code, gmo_balance_info = gmo_handler.fetch_balance()
    if error_code != WebAPIErrorCode.OK:
        return False, ExchangeType.INVALID, ExchangeType.INVALID, 0
    error_code, liquid_balance_info = liquid_handler.fetch_balance()
    if error_code != WebAPIErrorCode.OK:
        return False, ExchangeType.INVALID, ExchangeType.INVALID, 0

    # 残高を確認して、しきい値を算出
    liquid_buy_threshold = 1200
    gmo_buy_threshold = 1200
    if gmo_balance_info.BTC >= 0.08:
        gmo_buy_threshold = 1500
    if liquid_balance_info.BTC >= 0.08:
        liquid_buy_threshold = 1500

    # 価格差があるかチェック
    # Liquidで買って、GMOで売るパターン
    diff = gmo_ticker_info.best_buy_order - liquid_ticker_info.best_sell_order
    print("Liquid買い: " + str(diff))
    if  diff >= liquid_buy_threshold:
        if min(gmo_ticker_info.best_buy_order_volume, liquid_ticker_info.best_sell_order_volume) < 0.01:
            False, ExchangeType.INVALID, ExchangeType.INVALID, 0
        volume = 0.01 # いったん固定でやってみる
        # 残高チェック
        need_yen = volume * gmo_ticker_info.best_buy_order
        if not check_balance(btc=volume, btc_handler=gmo_handler, yen=need_yen, yen_handler=liquid_handler):
            return False, ExchangeType.INVALID, ExchangeType.INVALID, 0
        return True, ExchangeType.LIQUID, ExchangeType.GMO, volume

    # GMOで買って、Liquidで売るパターン
    diff = liquid_ticker_info.best_buy_order - gmo_ticker_info.best_sell_order
    print("GMO買い: " + str(diff))
    if diff >= gmo_buy_threshold:
        if min(liquid_ticker_info.best_buy_order_volume, gmo_ticker_info.best_sell_order_volume) < 0.01:
            return False, ExchangeType.INVALID, ExchangeType.INVALID, 0
        volume = 0.01 # いったん固定でやってみる
        need_yen = volume * liquid_ticker_info.best_buy_order
        if not check_balance(btc=volume, btc_handler=liquid_handler, yen=need_yen, yen_handler=gmo_handler):
            return False, ExchangeType.INVALID, ExchangeType.INVALID, 0
        return True, ExchangeType.GMO, ExchangeType.LIQUID, volume

    return False, ExchangeType.INVALID, ExchangeType.INVALID, 0



def make_order_for_arbitrage(gmo_handler, liquid_handler, buy_exchange, sell_exchange, volume):
    '''
    実際に売買の注文を出す。
    '''

    # GMOで買って、Liquidで売るパターン
    if buy_exchange == ExchangeType.GMO and sell_exchange == ExchangeType.LIQUID:
        error_code = liquid_handler.make_sell_market_order(CryptoType.BTC, volume)
        if error_code != WebAPIErrorCode.OK:
            return
        gmo_handler.make_buy_market_order(CryptoType.BTC, volume) # こっちだけ失敗したらどうしよう


    # Liquidで買って、GMOで売るパターン
    if buy_exchange == ExchangeType.LIQUID and sell_exchange == ExchangeType.GMO:
        error_code = liquid_handler.make_buy_market_order(CryptoType.BTC, volume)
        if error_code != WebAPIErrorCode.OK:
            return
        gmo_handler.make_sell_market_order(CryptoType.BTC, volume) # こっちだけ失敗した場合どうしよう

def print_total_balance(gmo_handler, liquid_handler, initial_balance):
    '''
    現在の資産残高を表示する。
    リファレンス実装なので、とりあえずBTCのみ。
    '''
    error_code, gmo_balance = gmo_handler.fetch_balance()
    if error_code != WebAPIErrorCode.OK:
        return
    error_code, liquid_balance = liquid_handler.fetch_balance()
    if error_code != WebAPIErrorCode.OK:
        return
    error_code, gmo_ticker_info = gmo_handler.fetch_ticker_info(CryptoType.BTC)
    if error_code != WebAPIErrorCode.OK:
        return
    error_code, liquid_ticker_info = liquid_handler.fetch_ticker_info(CryptoType.BTC)
    if error_code != WebAPIErrorCode.OK:
        return
    gmo_total_balance = float(gmo_balance.YEN) + float(gmo_balance.BTC) * float(gmo_ticker_info.best_buy_order)
    liquid_total_balance = float(liquid_balance.YEN) + float(liquid_balance.BTC) * float(liquid_ticker_info.best_buy_order)
    diff = math.floor(float(math.floor(float(gmo_balance.YEN) + float(liquid_balance.YEN))) - float(initial_balance))
    print(">>>>>> 合計 " + "{:,}".format(math.floor(gmo_total_balance + liquid_total_balance)) +
          " >>>>> 現金 " + "{:,}".format(math.floor(float(gmo_balance.YEN) + float(liquid_balance.YEN))) + " (" + str(diff) + ") " +
          " >>>>> BTC "  + str(float(gmo_balance.BTC) + float(liquid_balance.BTC)) +
          "( GMO: " + str(gmo_balance.BTC) +", Liquid: " + str(liquid_balance.BTC) + " )")
    #file = codecs.open("trade_log.csv", "a")
    #dt_now = datetime.datetime.now()
    #file.write(dt_now.strftime('%Y年%m月%d日 %H:%M:%S') + "," + str(math.floor(float(gmo_balance.YEN) + float(liquid_balance.YEN))) + "\n")
    #file.close()
    if gmo_total_balance+liquid_total_balance < 210000:
        print("資産状況がしきい値を下回ったのでアービトラージを停止します。")
        sys.exit()



if __name__=='__main__':
    print("info: システムトレードを開始します。")

    # 初期化
    gmo_handler = ExchangeHandler(ExchangeType.GMO)
    gmo_handler.load_api_key()
    liquid_handler = ExchangeHandler(ExchangeType.LIQUID)
    liquid_handler.load_api_key()

    # 初期残高の計算
    initial_balance = -9999
    file = codecs.open("trade_log.csv", "r")
    content = file.read()
    initial_balance = float(content.splitlines()[0].split(",")[1])

    # メインループ
    timespan = 1.5 # 秒
    time.sleep(timespan)
    before_should_order = False #1つ前のループのshould_order値
    while True:
        # 初期残高の取得
        if initial_balance == -9999:
            error_code, gmo_balance = gmo_handler.fetch_balance()
            if error_code != WebAPIErrorCode.OK:
                time.sleep(timespan)
                continue
            error_code, liquid_balance = liquid_handler.fetch_balance()
            if error_code != WebAPIErrorCode.OK:
                time.sleep(timespan)
                continue
            initial_balance = math.floor(float(gmo_balance.YEN) + float(liquid_balance.YEN))

        print_total_balance(gmo_handler=gmo_handler, liquid_handler=liquid_handler, initial_balance=initial_balance)

        should_order, buy_exchange_type, sell_exchange_type, volume = \
            check_price_for_arbitrage(gmo_handler=gmo_handler, liquid_handler=liquid_handler)
        print()
        if not should_order:
            before_should_order = False
            time.sleep(timespan)
            continue
        if not before_should_order:
            # 前回はFalseだったけど、今回はTrueである特殊ケース
            # 例外的にsleepしない
            before_should_order = True
            continue
        print("!! アービトラージを実施します !!")
        make_order_for_arbitrage(gmo_handler=gmo_handler, liquid_handler=liquid_handler,
                                 buy_exchange=buy_exchange_type, sell_exchange=sell_exchange_type, volume=volume)
        time.sleep(timespan)


    print("info: システムトレードを終了します。")