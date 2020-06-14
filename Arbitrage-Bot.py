#!/usr/bin/python
"""This Script is used to do arbitrage trading between binance and bittrex"""

import time, datetime
from binance.client import Client
from bittrex.bittrex import Bittrex
from simple_settings import LazySettings

#Constants
settings = LazySettings('settings')
myBinance = Client(settings.BINANCE_API_KEY, settings.BINANCE_API_SECRET)
myBittrex = Bittrex(settings.BITTREX_API_KEY, settings.BITTREX_API_SECRET, api_version='v1.1')
#End of constants

#Variables
COUNTER = 0
TRADE_COUNTER = 0
RETRY = 0
PROFIT_TRACKER = {}
BUY_LIST = {}
#End Of Variables

#Functions
def print_title():
    print("-"*30)
    print("Welcome to the L8nit3 Arb Bot")
    print("-"*30)
    print("1)Enter Settings")
    print("2)Run Bot")
    print("3).......")
    print("4)PROFIT! $$")
    print("_"*30)
    print("Debug level:", settings.DEBUG)
    print("Dry run mode active:", settings.DRY_RUN)
    print("Flip mode active:", settings.FLIP_MODE)
    print("Liquidity Module Active:", settings.LIQUIDITY_MODULE)
    print("Stacking BTC Mode:", settings.GAIN_BTC)
    print("_"*30)
    print("")
    time.sleep(4)

def get_trex_balance(COIN, BASE):
    '''Ensure account has funds to opperate script'''
    try:
        btc = myBittrex.get_balance(BASE)['result']['Available']
        if btc == None:
            btc = 0.0
    except Exception as error:
        if settings.DEBUG == 2:
            print("Error occurred Bittrex get_balance:", error)
        time.sleep(0.1)
        btc = myBittrex.get_balance(BASE)['result']['Available']
    try:
        Coin = myBittrex.get_balance(COIN)['result']['Available']
        if Coin == None:
            Coin = 0.0
    except Exception as error:
        if settings.DEBUG == 2:
            print("Error occurred Bittrex get_balance:", error)
        time.sleep(0.1)
        Coin = myBittrex.get_balance(COIN)['result']['Available']
    return btc, Coin

def get_nance_balance(COIN, BASE):
    '''Ensure account has funds to opperate script'''
    try:
        btc = myBinance.get_asset_balance(asset=BASE)['free']
        Coin = myBinance.get_asset_balance(asset=COIN)['free']
    except Exception as error:
        if settings.DEBUG == 2:
            print("Error occurred Binance get_balance:", error)
        time.sleep(0.1)
        btc = myBinance.get_asset_balance(asset=BASE)['free']
        Coin = myBinance.get_asset_balance(asset=COIN)['free']
    return btc, Coin

def balance_debug(COIN, BASE):
    '''Check balances and print to user'''
    print("Binance Balances: {0}={1} {2}={3}".format(BASE, get_nance_balance(COIN, BASE)[0],
                                                     COIN, get_nance_balance(COIN, BASE)[1]))
    print("Bittrex Balances: {0}={1} {2}={3}".format(BASE, get_trex_balance(COIN, BASE)[0],
                                                     COIN, get_trex_balance(COIN, BASE)[1]))
    print("")

def enough_balance_to_run(COIN, BASE):
    '''Check balances and see if there is enough COIN/btc'''
    btc_price = myBinance.get_ticker(symbol=make_coin_pair(COIN, BASE)[1])['askPrice']
    needed_btc = float((float(btc_price)*float(AMOUNT_TO_TRADE))*settings.DESIRED_CYCLES)
    needed_coin = float(float(AMOUNT_TO_TRADE)*settings.DESIRED_CYCLES)
    is_enough = True
    if(float(get_nance_balance(COIN, BASE)[0]) < needed_btc or
       float(get_trex_balance(COIN, BASE)[0]) < needed_btc or
       float(get_nance_balance(COIN, BASE)[1]) < needed_coin or
       float(get_trex_balance(COIN, BASE)[1]) < needed_coin):
        is_enough = False
    return is_enough

def make_coin_pair(COIN, BASE):
    '''Take COIN and make correct pair for each exchange'''
    coin_symbol = COIN
    bittrex_pair = BASE + "-" + coin_symbol
    binance_pair = coin_symbol + BASE
    return bittrex_pair, binance_pair

def get_prices(COIN, BASE):
    '''Check COIN price at both exchanges'''
    try:
        nance_ask = float(myBinance.get_ticker(symbol=make_coin_pair(COIN, BASE)[1])['askPrice'])
        nance_bid = float(myBinance.get_ticker(symbol=make_coin_pair(COIN, BASE)[1])['bidPrice'])
    except Exception as error:
        if settings.DEBUG == 2:
            print("Error occurred Binance get_prices:", error)
        time.sleep(0.1)
        nance_ask = float(myBinance.get_ticker(symbol=make_coin_pair(COIN, BASE)[1])['askPrice'])
        nance_bid = float(myBinance.get_ticker(symbol=make_coin_pair(COIN, BASE)[1])['bidPrice'])

    try:
        trex_ask = float(myBittrex.get_ticker(make_coin_pair(COIN, BASE)[0])['result']['Ask'])
        trex_bid = float(myBittrex.get_ticker(make_coin_pair(COIN, BASE)[0])['result']['Bid'])
    except Exception as error:
        if settings.DEBUG == 2:
            print("Error occurred Bittrex get_prices:", error)
        time.sleep(0.1)
        trex_ask = float(myBittrex.get_ticker(make_coin_pair(COIN, BASE)[0])['result']['Ask'])
        trex_bid = float(myBittrex.get_ticker(make_coin_pair(COIN, BASE)[0])['result']['Bid'])

    return trex_ask, trex_bid, nance_ask, nance_bid

def buy_trex(value, COIN, BASE):
    '''Buy at Bittrex'''
    try:
        if not settings.GAIN_BTC:
            buy = myBittrex.buy_limit(market=make_coin_pair(COIN, BASE)[0],
                                      quantity=value, rate=get_prices()[1]+0.00000001)
        else:
            buy = myBittrex.buy_limit(market=make_coin_pair(COIN, BASE)[0],
                                      quantity=(AMOUNT_TO_TRADE*1.0035),
                                      rate=get_prices()[1]+0.00000001)
        print(buy)
    except Exception as error:
        if settings.DEBUG == 2:
            print("Error occurred Bittrex, buy_bittrex:", error)
        else:
            pass

def sell_trex(COIN, BASE):
    '''Sell at Bittrex'''
    try:
        sell = myBittrex.sell_limit(market=make_coin_pair(COIN, BASEE)[0],
                                    quantity=AMOUNT_TO_TRADE, rate=get_prices()[2]-0.00000001)
        print(sell)
    except Exception as error:
        if settings.DEBUG == 2:
            print("Error occurred Bittrex, sell_bittrex:", error)
        else:
            pass

def buy_nance(value, COIN, BASE):
    '''Buy coins at binance'''
    try:
        if not settings.GAIN_BTC:
            buy = myBinance.order_market_buy(symbol=make_coin_pair(COIN, BASE)[1], quantity=value)
        else:
            buy = myBinance.order_market_buy(symbol=make_coin_pair(COIN, BASE)[1],
                                             quantity=(AMOUNT_TO_TRADE*1.0035))
        print(buy)
    except Exception as error:
        if settings.DEBUG == 2:
            print("Error occurred Binance, buy_binance:", error)
        else:
            pass

def sell_nance(COIN, BASE):
    '''Sell coins at binance'''
    try:
        sell = myBinance.order_market_sell(symbol=make_coin_pair(COIN)[1],
                                           quantity=AMOUNT_TO_TRADE)
        print(sell)
    except Exception as error:
        if settings.DEBUG == 2:
            print("Error occurred Binance, sell_binance:", error)
        else:
            pass

def check_liquidity(COIN, AMOUNT_TO_TRADE, BASE):
    '''Used to check orderbook before making a trade to ensure liquidity for trade. '''
    liquid = 0
    if BUY_LIST[COIN]['Binance'] == 1:
        Bittrex_Ask_Orderbook = float(myBittrex.get_orderbook(make_coin_pair(COIN, BASE)[0])['result']['sell'][0]['Quantity'])
        Binance_Bid_Orderbook = float(myBinance.get_order_book(symbol=make_coin_pair(COIN, BASE)[1])['bids'][0][1])
        if(Bittrex_Ask_Orderbook > AMOUNT_TO_TRADE and Binance_Bid_Orderbook > (AMOUNT_TO_TRADE*1.05)):
            liquid = 1

    elif BUY_LIST[COIN]['Bittrex'] == 1:
        Bittrex_Bid_Orderbook = myBittrex.get_orderbook(make_coin_pair(COIN, BASE)[0])['result']['buy'][0]['Quantity']
        Binance_Ask_Orderbook = myBinance.get_order_book(symbol=make_coin_pair(COIN, BASE)[1])['asks'][0][1]
        if(Bittrex_Bid_Orderbook > AMOUNT_TO_TRADE and Binance_Ask_Orderbook > (AMOUNT_TO_TRADE*1.05)):
            liquid = 1
    return liquid
        
def backend_logic(COIN, AMOUNT_TO_TRADE, DESIRED_PERCENT_GAIN, BASE, Original_Coin):
    '''Determine high/low, diff percent, and if trade is needed'''
    trex_ask = get_prices(COIN, BASE)[0]
    trex_bid = get_prices(COIN, BASE)[1]
    nance_ask = get_prices(COIN, BASE)[2]
    nance_bid = get_prices(COIN, BASE)[3]
    traded = 0
        
    if((nance_bid>trex_ask) and ((settings.FLIP_MODE and BUY_LIST[Original_Coin+BASE]['Binance'] == 1) or (not settings.FLIP_MODE))):
        diff = nance_bid-trex_ask
        percent = (diff/trex_ask)*100
        if(settings.DRY_RUN or settings.DEBUG > 0):
            print("\nBinance {2} SELL Price {0} {3} > Bittrex {2} BUY Price {1} {3}".format(
                nance_bid, trex_ask, COIN, BASE))
            print("Potential Gain: {0}% - fees = {1}".format(round(percent, 2), round(percent-0.35, 2)))
            print("Needs to be: {0}% (including trade fees)".format(DESIRED_PERCENT_GAIN + 0.35))
        if percent > (DESIRED_PERCENT_GAIN + 0.35):
            now = datetime.datetime.now()
            value = AMOUNT_TO_TRADE*(1.0+(DESIRED_PERCENT_GAIN/100))
            if(enough_balance_to_run(COIN, BASE) or settings.DRY_RUN):
                if settings.LIQUIDITY_MODULE:
                    liquid = check_liquidity(COIN, AMOUNT_TO_TRADE, BASE)
                else:
                    print("Liquidity Module Skipping")
                    liquid = 1
                if liquid > 0:
                    if not settings.DRY_RUN:
                        sell_nance(COIN, BASE)
                        buy_trex(value, COIN, BASE)
                    print("")
                    print("-"*30)
                    print(now.strftime("%Y-%m-%d %H:%M:%S"))
                    print("Trade Occurred! Sold at Binance for {0}\nBought at Bittrex for {1}"
                          .format(nance_bid, trex_ask))
                    if settings.GAIN_BTC:
                        print("Total gain of {0}%, or {1} satoshi per {2} = {3}"
                              .format(percent-0.35, diff, COIN, diff*AMOUNT_TO_TRADE))
                    else:
                        print("Total gain of {0}%".format(percent- 0.35))
                        print("-"*30)
                        print("")
                        traded = 1
                    PROFIT_TRACKER[Original_Coin+BASE] = PROFIT_TRACKER[Original_Coin+BASE] + (diff*AMOUNT_TO_TRADE)
                    BUY_LIST[Original_Coin+BASE] = {'Bittrex':1, 'Binance':0}
                else:
                    print("#Trade conditions met, but lacking liquidity in orderbooks#")
                    print("")
        
    elif((trex_bid>nance_ask)  and ((settings.FLIP_MODE and BUY_LIST[Original_Coin+BASE]['Bittrex'] == 1) or (not settings.FLIP_MODE))):
        diff = trex_bid-nance_ask
        percent = (diff/nance_ask)*100
        if(settings.DRY_RUN or settings.DEBUG > 0):
            print("\nBittrex {2} SELL Price {0} {3} > Binance {2} BUY Price {1} {3}".format(
                trex_bid, nance_ask, COIN, BASE))
            print("Potential Gain: {0}% - fees = {1}".format(round(percent, 2), round(percent-0.35, 2)))
            print("Needs to be: {0}% (including trade fees)".format(DESIRED_PERCENT_GAIN + 0.35))
        if percent > (DESIRED_PERCENT_GAIN + 0.35):
            value = AMOUNT_TO_TRADE*(1.0+(DESIRED_PERCENT_GAIN/100))
            if(enough_balance_to_run(COIN, BASE) or settings.DRY_RUN):
                if settings.LIQUIDITY_MODULE:
                    liquid = check_liquidity(COIN, AMOUNT_TO_TRADE, BASE)
                else:
                    print("Liquidity Module Skipping")
                    liquid = 1
                if liquid > 0:
                    if not settings.DRY_RUN:
                        sell_trex(COIN, BASE)
                        buy_nance(value, COIN, BASE)
                    print("")
                    print("-"*30)
                    print("Trade Occurred! Sold at Bittrex for {0} \nBought at Binance for {1}"
                          .format(trex_bid, nance_ask))
                    if settings.GAIN_BTC:
                        print("Total gain of {0}%, or {1} satoshi per {2} = {3}"
                              .format(percent-0.35, diff, COIN, diff*AMOUNT_TO_TRADE))
                    else:
                        print("Total gain of {0}%".format(percent-0.35))
                        print("-"*30)
                        print("")
                        traded = 1
                    PROFIT_TRACKER[Original_Coin+BASE] = PROFIT_TRACKER[Original_Coin+BASE] + (diff*AMOUNT_TO_TRADE)
                    BUY_LIST[Original_Coin+BASE] = {'Bittrex':0, 'Binance':1}
                else:
                    print("#Trade conditions met, but lacking liquidity in orderbooks#")
                    print("")
    else:
        if(settings.DRY_RUN or settings.DEBUG > 0):
            diff1 = trex_bid-nance_ask
            percent1 = (diff1/trex_bid)*100
            diff2 = nance_bid-trex_ask
            percent2 = (diff2/nance_bid)*100
            print("")
            print("{3} Binance Sell: {0}{4} | Bittrex Buy: {1}{4} | Potential Gain={2}%".format(nance_bid, trex_ask, round(percent2-0.35, 2), COIN, BASE))
            print("{3} Bittrex Sell: {0}{4} | Binance Buy: {1}{4} | Potential Gain={2}%".format(trex_bid, nance_ask, round(percent1-0.35, 2), COIN, BASE))
            if not settings.FLIP_MODE:
                print("Waiting for positive Bid/Ask price difference.")
            elif(settings.FLIP_MODE and traded == 1):
                print("Waiting for opposite trade to be profitable.")
    return traded

def main(COUNTER, TRADE_COUNTER, COIN, AMOUNT_TO_TRADE, DESIRED_PERCENT_GAIN, BASE, Original_Coin):
    '''Main function, pull everything together to run'''
    if "-" in settings.COIN_LIST[COIN][2]:
        BASE = settings.COIN_LIST[COIN][2].split("-", 1)[0]
    if(enough_balance_to_run(COIN, BASE) or settings.DRY_RUN):
        traded = backend_logic(COIN, AMOUNT_TO_TRADE, DESIRED_PERCENT_GAIN, BASE, Original_Coin)
        if traded == 1:
            TRADE_COUNTER = TRADE_COUNTER+1
            print("Sleeping after trade.")
            time.sleep(settings.SLEEP_AFTER_TRADE)
        elif traded == 0:
            pass
    else:
        print("\nPlease Check {0} Balances!".format(Original_Coin))

def print_needed(COIN, AMOUNT_TO_TRADE, BASE):
    '''Print amount of BTC/COIN needed to trade'''
    if "-" in settings.COIN_LIST[COIN]:
        COIN = settings.COIN_LIST[COIN].split("-", 1)[0]
    btc_price = myBinance.get_ticker(symbol=make_coin_pair(COIN, BASE)[1])['askPrice']
    btc_amount = (float(btc_price)*float(AMOUNT_TO_TRADE))*settings.DESIRED_CYCLES
    print("Needed {0} per account: {1}".format(BASE, round(btc_amount, 8)))
    print("Needed", COIN, " per account:", float(AMOUNT_TO_TRADE)*settings.DESIRED_CYCLES)
#End Of Functions

#Print Title, And Run
print_title()
for COIN in settings.COIN_LIST:
    AMOUNT_TO_TRADE = settings.COIN_LIST[COIN][0]
    DESIRED_PERCENT_GAIN = settings.COIN_LIST[COIN][1]
    BASE = settings.COIN_LIST[COIN][2]
    if "-" in COIN:
        Original_Coin = COIN
        COIN = COIN.split("-", 1)[0]
    else:
        Original_Coin = COIN
    print("{0}:".format(Original_Coin))
    print("Target percent:", DESIRED_PERCENT_GAIN)
    print_needed(COIN, AMOUNT_TO_TRADE, BASE)
    balance_debug(COIN, BASE)
    PROFIT_TRACKER[Original_Coin+BASE] = 0.0
    BUY_LIST[Original_Coin+BASE] = {'Bittrex':1, 'Binance':1}

while True:
    print("_"*30)
    for COIN in settings.COIN_LIST:
        AMOUNT_TO_TRADE = float(settings.COIN_LIST[COIN][0])
        DESIRED_PERCENT_GAIN = float(settings.COIN_LIST[COIN][1])
        BASE = settings.COIN_LIST[COIN][2]
        if "-" in COIN:
            Original_Coin = COIN
            COIN = COIN.split("-", 1)[0]
        else:
            Original_Coin = COIN
        try:
            main(COUNTER, TRADE_COUNTER, COIN, AMOUNT_TO_TRADE, DESIRED_PERCENT_GAIN, BASE, Original_Coin)
        except Exception as e:
            time.sleep(3)
            while(RETRY<999999999999):
                print("Script crashed,{0} \nretrying......".format(e))
                print_title()
                main(COUNTER, TRADE_COUNTER, COIN, AMOUNT_TO_TRADE, DESIRED_PERCENT_GAIN, BASE, Original_Coin)
                RETRY += 1
    print("_"*30)
    if(COUNTER%10 == 0 and COUNTER != 0):
        print("")
        print("Run-Count:", COUNTER)
        print("Trade-Count:", TRADE_COUNTER)
        for COIN in settings.COIN_LIST:
            BASE = settings.COIN_LIST[COIN][2]
            if(PROFIT_TRACKER[Original_Coin+BASE] == 0):
                profit_amount = 0
            else:
                profit_amount = PROFIT_TRACKER[Original_Coin+BASE]
            print("Profit Tracking {0}: {1} {2}".format(COIN, profit_amount, BASE))
            if "-" in COIN:
                COIN = COIN.split("-", 1)[0]
            balance_debug(COIN, BASE)
    time.sleep(settings.SLEEP_BETWEEN_CYCLE)
    COUNTER = COUNTER+1
