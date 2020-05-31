#!/usr/bin/python
"""This Script is used to do arbitrage trading between binance and bittrex"""

import time, datetime, sys
from binance.client import Client
from bittrex.bittrex import Bittrex
from simple_settings import LazySettings

settings = LazySettings('Nexus_settings')

#Constants
myBinance = Client(settings.BINANCE_API_KEY, settings.BINANCE_API_SECRET) #Binance connect
myBittrex= Bittrex(settings.BITTREX_API_KEY, settings.BITTREX_API_SECRET, api_version='v1.1') #Bittrex connect
#End of constants

#Functions
def test_trex_api():
    '''Trex Api Call To Test Keys'''
    try:
        myBittrex.get_balance('BTC')
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Bittrex test_api:", error)
        else:
            pass

def test_nance_api():
    '''Nance Api Call To Test Keys'''
    try:
        myBinance.get_asset_balance(asset='BTC')
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Binance test_api:", error)
        else:
            pass

def get_trex_balance():
    '''Ensure account has funds to opperate script'''
    try:
        btc = myBittrex.get_balance('BTC')['result']['Available']
        btc = remove_exponent(str(btc))
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Bittrex get_balance:", error)
        else:
            pass
    try:
        Coin = myBittrex.get_balance(settings.COIN)['result']['Available']
        Coin = remove_exponent(str(Coin))
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Bittrex get_balance:", error)
        else:
            pass
    return btc,Coin

def get_nance_balance():
    '''Ensure account has funds to opperate script'''
    try:
        btc = myBinance.get_asset_balance(asset='BTC')['free']
        Coin = myBinance.get_asset_balance(asset=settings.COIN)['free']
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Binance get_balance:", error)
        else:
            pass
    return btc,Coin

def balance_debug():
    '''Check balances and print to user'''
    print("Balance Debug Stats:")
    print("Binance BTC Balance:", get_nance_balance()[0])
    print("Binance", settings.COIN, "Balance:", get_nance_balance()[1])
    print("Bittrex BTC Balance:", get_trex_balance()[0])
    print("Bittrex", settings.COIN, "Balance:", get_trex_balance()[1])
    print("")

def enough_balance_to_run():
    '''Check balances and see if there is enough settings.COIN/btc for 3 continuos runs'''
    btc_price = myBinance.get_ticker(symbol=settings.COIN_PAIR_BINANCE)['askPrice']
    needed_btc = float((float(btc_price)*float(settings.AMOUNT_TO_SELL))*3)
    needed_coin = float(float(settings.AMOUNT_TO_SELL)*3)
    is_enough = True
    if(float(get_nance_balance()[0])<needed_btc or
       float(get_trex_balance()[0])<needed_btc or
       float(get_nance_balance()[1])<needed_coin or
       float(get_trex_balance()[1])<needed_coin):
        is_enough = False
    return is_enough

def remove_exponent(value):
    '''Change 1e10 style numbers to satoshi'''
    decial = value.split('e')
    ret_val = format(((float(decial[0]))*(10**int(decial[1]))), '.8f')
    return ret_val

def get_prices():
    '''Check settings.COIN price at both exchanges'''
    try:
        nance_ask = myBinance.get_ticker(symbol=settings.COIN_PAIR_BINANCE)['askPrice']
        nance_bid = myBinance.get_ticker(symbol=settings.COIN_PAIR_BINANCE)['bidPrice']
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Binance get_prices:", error)
        else:
            pass

    try:
        trex_ask = myBittrex.get_ticker(settings.COIN_PAIR_BITTREX)['result']['Ask']
        trex_ask = remove_exponent(str(trex_ask))
        trex_bid = myBittrex.get_ticker(settings.COIN_PAIR_BITTREX)['result']['Bid']
        trex_ask = remove_exponent(str(trex_bid))
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Bittrex get_prices:", error)
        else:
            pass
        
    return trex_ask, trex_bid, nance_ask, nance_bid

def buy_trex(value):
    '''Buy at Bittrex'''
    total = value*float(get_prices()[1])
    try:
        if(not settings.GAIN_BTC):
            buy = myBittrex.buy_limit(market=settings.COIN_PAIR_BITTREX, quantity=total, rate=float(get_prices()[1])+0.00000002)
        else:
            buy = myBittrex.buy_limit(market=settings.COIN_PAIR_BITTREX, quantity=settings.AMOUNT_TO_SELL, rate=float(get_prices()[1])+0.00000002)
        print(buy)
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Bittrex, buy_bittrex:", error)
        else:
            pass
        
def sell_trex():
    '''Sell at Bittrex'''
    try:
        sell = myBittrex.sell_limit(market=settings.COIN_PAIR_BITTREX, quantity=settings.AMOUNT_TO_SELL, rate=float(get_prices()[2])-0.00000002)
        print(sell)
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Bittrex, sell_bittrex:", error)
        else:
            pass

def buy_nance(value):
    '''Buy coins at binance'''
    total = value*float(get_prices()[3])
    try:
        if(not settings.GAIN_BTC):
            buy = myBinance.order_market_buy(symbol=settings.COIN_PAIR_BINANCE,quantity=total)
        else:
            buy = myBinance.order_market_buy(symbol=settings.COIN_PAIR_BINANCE,quantity=settings.AMOUNT_TO_SELL)
        print(buy)
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Binance, buy_binance:", error)
        else:
            pass

def sell_nance():
    '''Sell coins at binance'''
    try:
        sell = myBinance.order_market_sell(symbol=settings.COIN_PAIR_BINANCE,quantity=settings.AMOUNT_TO_SELL)
        print(sell)
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Binance, sell_binance:", error)
        else:
            pass

def backend_logic():
    '''Determine high/low, diff percent, and if trade is needed'''
    trex_ask = float(get_prices()[0])
    trex_bid = float(get_prices()[1])
    nance_ask = float(get_prices()[2])
    nance_bid = float(get_prices()[3])
    traded = 0
    if(settings.DRY_RUN or settings.DEBUG > 0):
        print("")
        print("Pricing Debug Stats:")
        print("Binance Ask:", remove_exponent(str(nance_ask)))
        print("Bittrex Ask:", remove_exponent(str(trex_ask)))
        print("Binance Bid:", remove_exponent(str(nance_bid)))
        print("Bittrex Bid:", remove_exponent(str(trex_bid)))
        print("")
    
    if(nance_bid>trex_bid):
        diff = nance_bid-trex_ask
        percent = (diff/trex_ask)*100
        traded = 0
        if(settings.DRY_RUN or settings.DEBUG > 0):
            print("Binance > Bittrex")
            print("Difference:", round(percent, 2), "%")
            print("Needs to be:", settings.DESIRED_PERCENT_GAIN, "%")
            print("")
        if(percent > settings.DESIRED_PERCENT_GAIN and percent > 0):
            now = datetime.datetime.now()
            value = settings.AMOUNT_TO_SELL*nance_bid
            if(not settings.DRY_RUN and enough_balance_to_run()):
                sell_nance()
                buy_trex(value)
            print("")
            print("-"*30)
            print(now.strftime("%Y-%m-%d %H:%M:%S"))
            print("Trade Occurred! Sold at Binance for", remove_exponent(str(nance_bid)), "\nBought at Bittrex for", remove_exponent(str(trex_ask)))
            if(settings.GAIN_BTC):
                print("Total gain of", percent, "%, or", remove_exponent(str(diff)), "satoshi per", settings.COIN, "=", remove_exponent(str(diff))*settings.AMOUNT_TO_SELL)
            else:
                coin_amount = (float(remove_exponent(str(diff)))*trex_ask)*settings.AMOUNT_TO_SELL
                print("Total gain of", percent, "%, or", coin_amount, settings.COIN)
            print("-"*30)
            print("")
            traded = 1
        
    elif(trex_bid>nance_bid):
        diff = trex_bid-nance_ask
        percent = (diff/nance_ask)*100
        if(settings.DRY_RUN or settings.DEBUG > 0):
            print("Bittrex > Binance")
            print("Difference:", round(percent, 2), "%")
            print("Needs to be:", settings.DESIRED_PERCENT_GAIN, "%")
            print("")
        if(percent > settings.DESIRED_PERCENT_GAIN and percent > 0):
            value = settings.AMOUNT_TO_SELL*trex_bid
            if(not settings.DRY_RUN and enough_balance_to_run()):
                sell_trex()
                buy_nance(value)
            print("")
            print("-"*30)
            print("Trade Occurred! Sold at Bittrex for", remove_exponent(str(trex_bid)), "\nBought at Binance for", remove_exponent(str(nance_ask)))
            if(settings.GAIN_BTC):
                print("Total gain of", percent, "%, or", remove_exponent(str(diff)), "satoshi per", settings.COIN, "=", remove_exponent(str(diff))*settings.AMOUNT_TO_SELL)
            else:
                coin_amount = (float(remove_exponent(str(diff)))*nance_ask)*settings.AMOUNT_TO_SELL
                print("Total gain of", percent, "%, or", coin_amount, settings.COIN)
            print("-"*30)
            print("")
            traded = 1
    return traded

def nance_send_btc(btc_diff):
    '''Send btc from binance '''
    binance_btc_address = myBinance.get_deposit_address(asset='BTC')
    try:
        if(not settings.DRY_RUN):
            send = myBinance.withdraw(asset='BTC',address=binance_btc_address,amount=btc_diff)
            print(send)
        else:
            print("Dry Run - nance btc withdrawl amount:", btc_diff)
    except Exception as error:
        print("Error occurred binance, withdraw_btc:", error)

def trex_send_btc(btc_diff):
    '''Send btc from bittrex '''
    bittrex_btc_address = myBittrex.get_deposit_address('BTC')
    try:
        if(not settings.DRY_RUN):
            send = myBittrex.withdraw('BTC', btc_diff, bittrex_btc_address)
            print(send)
        else:
            print("Dry Run - trex btc withdrawl amount:", btc_diff)
    except Exception as error:
        print("Error occurred bittrex, withdraw_btc:", error)
    
def nance_send_coin(coin_diff):
    '''Send coins from binance'''
    binance_coin_address = myBinance.get_deposit_address(asset=settings.COIN)
    try:
        if(not settings.DRY_RUN):
            send = myBinance.withdraw(asset='BTC',address=binance_coin_address,amount=coin_diff)
            print(send)
        else:
            print("Dry Run - nance", settings.COIN, "withdrawl amount:", coin_diff)
    except Exception as error:
        print("Error occurred binance, withdraw_coin:", error)

def trex_send_coin(coin_diff):
    '''Send coins from bittrex'''
    bittrex_coin_address = myBittrex.get_deposit_address(settings.COIN)
    try:
        if(not settings.DRY_RUN):
            send = myBittrex.withdraw(settings.COIN, coin_diff, bittrex_coin_address)
            print(send)
        else:
            print("Dry Run - trex", settings.COIN, "withdrawl amount:", coin_diff)
    except Exception as error:
        print("Error occurred bittrex, withdraw_coin:", error)

def equalize_balances():
    '''Equalize balances at both exchanges for next run'''
    nance_btc = float(get_nance_balance()[0])
    nance_coin = float(get_nance_balance()[1])
    trex_btc = float(get_trex_balance()[0])
    trex_coin = float(get_trex_balance()[1])
    btc_high = max(nance_btc, trex_btc)
    coin_high = max(nance_coin, trex_coin)
    if(float(nance_btc) > 0 and float(trex_btc) > 0):
        if(btc_high == nance_btc):
            btc_diff = (nance_btc-trex_btc)/2
            nance_send_btc(btc_diff)
        else:
            btc_diff = (trex_btc-nance_btc)/2
            trex_send_btc(btc_diff)
            
        if(coin_high == nance_coin):
            coin_diff = (nance_coin-trex_coin)/2
            nance_send_coin(coin_diff)
        else:
            coin_diff = (trex_coin-nance_coin)/2
            trex_send_coin(coin_diff)
        time.sleep(1800)
    else:
        pass

def main(COUNTER):
    '''Main function, pull everything together to run'''
    if(enough_balance_to_run() or settings.DRY_RUN):
        try:
            test_trex_api()
            test_nance_api()
        except:
            sys.exit()
        traded = backend_logic()
        if(COUNTER%10 == 0 and COUNTER != 0):
            print("Run-Count:", COUNTER)
            balance_debug()
        if(traded == 1 and not enough_balance_to_run()):
            if(traded == 1 and not settings.DRY_RUN):
                if(settings.ENABLE_WITHDRAWLS):
                    equalize_balances()
                print("Sleeping 5 min")
                time.sleep(settings.SLEEP_AFTER_TRADE)
                balance_debug()
        elif(traded == 0):
            print("Sleeping 3, then re-run")
            time.sleep(settings.SLEEP_BETWEEN_CYCLE)
    else:
        print("Please Check Balances!")
#End Of Functions

#Print Title, And Run
print("-"*30)
print("Welcome to the L8nit3 Arb Bot")
print("-"*30)
print("")
print("1)Enter Settings")
print("2)Run Bot")
print("3).......")
print("4)PROFIT! $$")
print("")
print("_"*30)
print("")
time.sleep(4)
if(settings.GAIN_BTC):
    print("Stack sats mode: gain BTC.")
else:
    print("Stack", settings.COIN, "mode: gain", settings.COIN)
print("Dry run mode active:", settings.DRY_RUN)
print("Debug level:", settings.DEBUG)
print("")
btc_price = myBinance.get_ticker(symbol=settings.COIN_PAIR_BINANCE)['askPrice']
btc_amount = (float(btc_price)*float(settings.AMOUNT_TO_SELL))*3
print("needed btc per account:", round(btc_amount, 8))
print("needed", settings.COIN, " per account:", float(settings.AMOUNT_TO_SELL)*3)
print("")
balance_debug()
COUNTER = 0
while True:
    main(COUNTER)
    COUNTER = COUNTER+1
