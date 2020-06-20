#!/usr/bin/python
"""This Script is used to find arbitrage pairs between binance and bittrex"""

from binance.client import Client
from bittrex.bittrex import Bittrex
from simple_settings import LazySettings
settings = LazySettings('settings')

myBinance = Client(settings.BINANCE_API_KEY, settings.BINANCE_API_SECRET)
myBittrex = Bittrex(settings.BITTREX_API_KEY, settings.BITTREX_API_SECRET, api_version='v1.1')

quote_currencies = ['BTC', 'ETH', 'USDT']

def get_trex_list(base):
    test_coins = []
    for coin in myBittrex.get_markets()['result']:
        if coin['BaseCurrency'] == base:
            test_coins.append(coin['MarketCurrency'])
    return test_coins

def get_nance_list(base, coin_list):
    test_coins = []
    final_list = []
    for pair in myBinance.get_exchange_info()['symbols']:
        if pair['quoteAsset'] == base:
            test_coins.append(pair['baseAsset'])
    for test in test_coins:
        if test in coin_list:
            final_list.append(test)
    return final_list

print("Coins available on both exchanges")
for currency in quote_currencies:
    print("{0} pairs:".format(currency))
    coin_list = get_trex_list(currency)
    last = get_nance_list(currency, coin_list)
    print(str(last) + "\n")
