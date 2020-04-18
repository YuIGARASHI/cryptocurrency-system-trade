class BitflyerHandler():
    '''
    BitflyerのAPIラッパークラス。
    https://lightning.bitflyer.com/docs
    '''
    def __init__(self):
        pass

    def fetch_price(self, crypto_type):
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
        price     = str(json_data["ltp"]).split(".")[0]  # 小数点以下切り捨て
        return PriceInfo(timestamp, price, ExchangeType.BITFLYER)