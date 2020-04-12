'''
bitflyerのAPIをつかっていろいろやってみる.
https://lightning.bitflyer.com/docs
'''

from enum import Enum
import sys
import requests
import json
import codecs
import pprint
import time

class PriceInfo:
    def __init__(self, timestamp, price):
        self.timestamp = timestamp
        self.price    = price #JPY

class CryptoType(Enum):
    BTC = 0
    ETH = 1

def fetch_price_from_bitflyer(crypto_type):
    '''
    現在時刻の指定された仮想通貨の価格を取得する.
    '''
    path = '/v1/ticker'
    url = 'https://api.bitflyer.com' + path
    params = {}
    if crypto_type == CryptoType.BTC:
        params["product_code"] = "BTC_JPY"
    elif crypto_type == CryptoType.ETH:
        params["product_code"] = "ETH_JPY"
    else:
        print("error: Invalid CryptoType is specified!")
        sys.exit()
    json_data = requests.get(url, params=params).json()
    
    timestamp = json_data["timestamp"].split(".")[0] # 秒の小数点以下切り捨て
    price     = str(json_data["ltp"]).split(".")[0] # 小数点以下切り捨て
    return PriceInfo(timestamp, price)

if __name__=="__main__":
    # 1秒ごとに価格を取得しファイルに出力
    file_name = "data/price_" + str(time.time()).split(".")[0] + ".csv"
    before_btc_price = -1
    before_eth_price = -1
    while True:
        ofs = codecs.open(file_name, "a", "utf-8")
        try:
            btc_price_info = fetch_price_from_bitflyer(CryptoType.BTC)
            eth_price_info = fetch_price_from_bitflyer(CryptoType.ETH)
        except:
            continue
        if before_btc_price == -1 or before_eth_price == -1:
            before_btc_price = btc_price_info.price
            before_eth_price = eth_price_info.price
            continue
        diff_btc_price = str(int(btc_price_info.price) - int(before_btc_price))
        diff_eth_price = str((int(eth_price_info.price) - int(before_eth_price)) * 50) # ethは差分が比較しやすいよう50倍にする
        ofs.write(btc_price_info.timestamp+","+btc_price_info.price+","+eth_price_info.price+","+diff_btc_price+","+diff_eth_price+"\n")
        print(btc_price_info.timestamp+","+btc_price_info.price+","+eth_price_info.price+","+diff_btc_price+","+diff_eth_price)
        before_btc_price = btc_price_info.price
        before_eth_price = eth_price_info.price
        ofs.close()
        time.sleep(2)
        

    
    