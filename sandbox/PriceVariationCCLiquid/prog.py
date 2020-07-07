import sys
sys.path.append('../../')

from src.common.common import CryptoType, TickerInfo, ExchangeType, WebAPIErrorCode
from src.web_handler.exchange_handler import ExchangeHandler
import math
import time

class GlobalVariable:
    price_down_count = 0

# parameters
BUY_PRICE_THRESHOLD = 1000
SELL_PRICE_THRESHOLD = 100
SLEEP_SPAN = 1  # 要チューニング。短ければよいわけでもない。
ORDER_BTC_VOLUME = 0.01
price_down_count_threshold = 3

def buy_if_chance(before_price, curr_price, bb_handler):
    '''
    買うべき場合かどうか判定し、買うべき場合には成行注文を出す。
    買った場合Trueを返す。
    '''
    diff = curr_price - before_price
    print("diff: " + str(diff))
    if  diff > BUY_PRICE_THRESHOLD:
        print("BTC買い注文を出します。サイズは " + str(ORDER_BTC_VOLUME) + " です。")
        bb_handler.make_buy_market_order(CryptoType.BTC, ORDER_BTC_VOLUME)
        GlobalVariable.price_down_count = 0
        return True
    return False

def sell_if_chance(before_price, curr_price, bb_handler):
    '''
    売るべきかどうか判定し、売るべき場合には成行注文を出す。
    '''
    diff = curr_price - before_price
    print("diff: " + str(diff))
    if GlobalVariable.price_down_count > price_down_count_threshold:
        print("BTC売り注文を出します。サイズは " + str(ORDER_BTC_VOLUME) + " です。")
        bb_handler.make_sell_market_order(CryptoType.BTC, ORDER_BTC_VOLUME)
        return True
    if diff < SELL_PRICE_THRESHOLD:
        GlobalVariable.price_down_count += 1
    else:
        GlobalVariable.price_down_count = 0
    return False

if __name__=='__main__':
    print("info: システムトレードを開始します。")

    bb_handler = ExchangeHandler(ExchangeType.BITBANK)
    bb_handler.load_api_key()
    cc_handler = ExchangeHandler(ExchangeType.COINCHECK)
    cc_handler.load_api_key()

    # 初期値計算
    code, info = bb_handler.fetch_balance()
    if code != WebAPIErrorCode.OK:
        print("BB残高の取得に失敗しました。")
        sys.exit(1)
    initial_balance = float(info.YEN)

    cc_price_before = -1
    btc_possess_flag = False
    while True:
        code, info = cc_handler.fetch_ticker_info(CryptoType.BTC)
        # 例外処理
        if code != WebAPIErrorCode.OK:
            time.sleep(SLEEP_SPAN)
            continue
        if cc_price_before == -1:
            cc_price_before = info.best_sell_order
            time.sleep(SLEEP_SPAN)
            continue
        # BTCを保持しているかどうかで条件分岐
        if btc_possess_flag:
            result = sell_if_chance(before_price=cc_price_before,
                                    curr_price=info.best_sell_order,
                                    bb_handler=bb_handler)
            if result:
                btc_possess_flag = (not btc_possess_flag)
        else:
            result = buy_if_chance(before_price=cc_price_before,
                                   curr_price=info.best_sell_order,
                                   bb_handler=bb_handler)
            if result:
                btc_possess_flag = (not btc_possess_flag)
        cc_price_before = info.best_sell_order
        # 残高を表示
        code, info = bb_handler.fetch_balance()
        if code != WebAPIErrorCode.OK:
            print("BB残高の取得に失敗しました。")
            time.sleep(SLEEP_SPAN)
            continue
        diff = math.floor(info.YEN - initial_balance)
        print(">>>> BB残高 現金:" + str(math.floor(info.YEN)) + "(" + str(diff)+ "), BTC:" + str(info.BTC))
        if diff > 15000:
            print("損失が予想値を超えたため停止します。")
            sys.exit(1)
        time.sleep(SLEEP_SPAN)

    print("info: システムトレードを終了します。")
