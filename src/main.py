'''
システムトレードのエントリポイント。
'''

from src.common.common import CryptoType, TickerInfo, ExchangeType, WebAPIErrorCode
from src.web_handler.exchange_handler import ExchangeHandler
from src.util.config_reader import ConfigReader
from src.util.api_key_reader import APIKeyReader
import pprint
import time

'''
仮実装してみた感想。
1. arbitrage 関連のメソッドと reverse_trade するメソッドは別のクラスに切り出したほうがよさそう
2. それぞれのメソッドに毎度毎度 ExchangeHandler を渡すのがだるいので、メンバー変数として持たせたほうがよさそう
'''


def check_price_for_arbitrage(gmo_handler, coincheck_handler):
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
        return False, ExchangeType.INVALID, ExchangeType.INVALID, 0 # todo:無効値として定義すべき
    error_code, cc_ticker_info = coincheck_handler.fetch_ticker_info(CryptoType.BTC)
    if error_code != WebAPIErrorCode.OK:
        return False, ExchangeType.INVALID, ExchangeType.INVALID, 0 # todo:無効値として定義すべき

    # 価格差があるかチェック(とりあえず500円/BTCあれば取引実行)
    # Coincheckで買って、GMOで売るパターン
    diff = gmo_ticker_info.best_buy_order - cc_ticker_info.best_sell_order
    print("CC買い: " + str(diff))
    if  diff > 500:
        volume = min(gmo_ticker_info.best_buy_order_volume, cc_ticker_info.best_sell_order_volume)
        if volume < 0.005: # coincheckの数量制限に引っかかる
            return False, ExchangeType.INVALID, ExchangeType.INVALID, 0 # todo:無効値として定義すべき
        volume = min(volume, 0.01)  # 一回の取引で最大0.01BTCまで
        return True, ExchangeType.COINCHECK, ExchangeType.GMO, volume

    # GMOで買って、Coincheckで売るパターン
    diff = cc_ticker_info.best_buy_order - gmo_ticker_info.best_sell_order
    print("GMO買い: " + str(diff))
    if diff > 500:
        volume = min(cc_ticker_info.best_buy_order_volume, gmo_ticker_info.best_sell_order_volume)
        if volume < 0.005: # coincheckの数量制限にひっかかる
            return False, ExchangeType.INVALID, ExchangeType.INVALID, 0 # todo:無効値として定義すべき
        volume = min(volume, 0.01) # 一回の取引で最大0.01BTCまで
        return True, ExchangeType.GMO, ExchangeType.COINCHECK, volume

    return False, ExchangeType.INVALID, ExchangeType.INVALID, 0  # todo:無効値として定義すべき



def make_order_for_arbitrage(gmo_handler, coincheck_handler, buy_exchange, sell_exchange, volume):
    '''
    実際に売買の注文を出す。
    本来ならここに残高チェックを入れる必要があるが、リファレンス実装なのではぶいている。
    戻り値なし。
    '''
    # GMOで買って、Coincheckで売るパターン
    if buy_exchange == ExchangeType.GMO and sell_exchange == ExchangeType.COINCHECK:
        error_code = gmo_handler.make_buy_market_order(CryptoType.BTC, volume)
        if error_code != WebAPIErrorCode.OK:
            return
        coincheck_handler.make_sell_market_order(CryptoType.BTC, volume) # こっちだけ失敗した場合どうしよう

    # Coincheckで買って、GMOで売るパターン
    if buy_exchange == ExchangeType.COINCHECK and sell_exchange == ExchangeType.GMO:
        error_code = coincheck_handler.make_buy_market_order(CryptoType.BTC, volume)
        if error_code != WebAPIErrorCode.OK:
            return
        gmo_handler.make_sell_market_order(CryptoType.BTC, volume) # こっちだけ失敗した場合どうしよう

def print_total_balance(gmo_handler, coincheck_handler):
    '''
    現在の資産残高を表示する。
    リファレンス実装なので、とりあえずBTCのみ。
    '''
    error_code, gmo_balance = gmo_handler.fetch_balance()
    if error_code != WebAPIErrorCode.OK: # todo:この構文かなり繰り返すのでマクロ的な感じにしたい
        return
    error_code, cc_balance = coincheck_handler.fetch_balance()
    if error_code != WebAPIErrorCode.OK:
        return
    error_code, gmo_ticker_info = gmo_handler.fetch_ticker_info(CryptoType.BTC)
    if error_code != WebAPIErrorCode.OK:
        return
    error_code, cc_ticker_info = coincheck_handler.fetch_ticker_info(CryptoType.BTC)
    if error_code != WebAPIErrorCode.OK:
        return
    gmo_total_balance = float(gmo_balance.YEN) + float(gmo_balance.BTC) * float(gmo_ticker_info.best_buy_order)
    cc_total_balance = float(cc_balance.YEN) + float(cc_balance.BTC) * float(cc_ticker_info.best_buy_order)
    print(">>>>> 資産状況 " + str(gmo_total_balance + cc_total_balance)+" 円 <<<<<")



if __name__=='__main__':
    print("info: システムトレードを開始します。")

    # 初期化
    gmo_handler = ExchangeHandler(ExchangeType.GMO)
    gmo_handler.load_api_key()
    coincheck_handler = ExchangeHandler(ExchangeType.COINCHECK)
    coincheck_handler.load_api_key()

    # gmo_handler.make_sell_market_order(CryptoType.BTC, 0.02)

    # メインループ
    timespan = 2
    while True:
        print_total_balance(gmo_handler=gmo_handler, coincheck_handler=coincheck_handler)

        should_order, buy_exchange_type, sell_exchange_type, volume = \
            check_price_for_arbitrage(gmo_handler=gmo_handler, coincheck_handler=coincheck_handler)
        if not should_order:
            time.sleep(timespan)
            continue
        print("!! アービトラージを実施します !!")
        #make_order_for_arbitrage(gmo_handler=gmo_handler, coincheck_handler=coincheck_handler,
        #                         buy_exchange=buy_exchange_type, sell_exchange=sell_exchange_type, volume=volume)
        time.sleep(timespan)


    print("info: システムトレードを終了します。")