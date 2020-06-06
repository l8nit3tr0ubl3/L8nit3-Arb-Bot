#!/usr/bin/python
"""This Script is used to do arbitrage trading between binance and bittrex"""

import time, datetime, sys
from binance.client import Client
from bittrex.bittrex import Bittrex
from simple_settings import LazySettings

settings = LazySettings('Nexus_settings')

#Constants
myBinance = Client(settings.BINANCE_API_KEY, settings.BINANCE_API_SECRET) #Binance connect
myBittrex = Bittrex(settings.BITTREX_API_KEY, settings.BITTREX_API_SECRET, api_version='v1.1') #Bittrex connect
#End of constants

#Functions
def get_trex_balance():
    '''Ensure account has funds to opperate script'''
    try:
        btc = myBittrex.get_balance('BTC')['result']['Available']
        btc = remove_exponent(str(btc))
        if(btc == None):
            btc = 0.0
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Bittrex get_balance:", error)
        else:
            pass
    try:
        Coin = myBittrex.get_balance(settings.COIN)['result']['Available']
        Coin = remove_exponent(str(Coin))
        if(Coin == None):
            Coin = 0.0
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
    '''Check balances and see if there is enough settings.COIN/btc'''
    btc_price = myBinance.get_ticker(symbol=make_coin_pair()[1])['askPrice']
    needed_btc = float((float(btc_price)*float(settings.AMOUNT_TO_TRADE))*settings.DESIRED_CYCLES)
    needed_coin = float(float(settings.AMOUNT_TO_TRADE)*settings.DESIRED_CYCLES)
    is_enough = True
    if(float(get_nance_balance()[0])<needed_btc or
       float(get_trex_balance()[0])<needed_btc or
       float(get_nance_balance()[1])<needed_coin or
       float(get_trex_balance()[1])<needed_coin):
        is_enough = False
    return is_enough

def make_coin_pair():
    coin_symbol = settings.COIN
    bittrex_pair = "BTC-" + coin_symbol
    binance_pair = coin_symbol + "BTC"
    return bittrex_pair, binance_pair

def remove_exponent(value):
    '''Change 1e10 style numbers to satoshi'''
    decial = value.split('e')
    ret_val = format(((float(decial[0]))*(10**int(decial[1]))), '.8f')
    ret_val = float(ret_val)
    return ret_val

def get_prices():
    '''Check settings.COIN price at both exchanges'''
    try:
        nance_ask = float(myBinance.get_ticker(symbol=make_coin_pair()[1])['askPrice'])
        nance_bid = float(myBinance.get_ticker(symbol=make_coin_pair()[1])['bidPrice'])
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Binance get_prices:", error)
        else:
            pass

    try:
        trex_ask = float(myBittrex.get_ticker(make_coin_pair()[0])['result']['Ask'])
        trex_bid = float(myBittrex.get_ticker(make_coin_pair()[0])['result']['Bid'])
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Bittrex get_prices:", error)
        else:
            pass
        
    return trex_ask, trex_bid, nance_ask, nance_bid

def buy_trex(value):
    '''Buy at Bittrex'''
    total = value*get_prices()[1]
    try:
        if(not settings.GAIN_BTC):
            buy = myBittrex.buy_limit(market=make_coin_pair()[0], quantity=total, rate=get_prices()[1]+0.00000001)
        else:
            buy = myBittrex.buy_limit(market=make_coin_pair()[0], quantity=settings.AMOUNT_TO_TRADE+1, rate=get_prices()[1]+0.00000001)
        print(buy)
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Bittrex, buy_bittrex:", error)
        else:
            pass
        
def sell_trex():
    '''Sell at Bittrex'''
    try:
        sell = myBittrex.sell_limit(market=make_coin_pair()[0], quantity=settings.AMOUNT_TO_TRADE, rate=get_prices()[2]-0.00000001)
        print(sell)
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Bittrex, sell_bittrex:", error)
        else:
            pass

def buy_nance(value):
    '''Buy coins at binance'''
    total = value*get_prices()[3]
    try:
        if(not settings.GAIN_BTC):
            buy = myBinance.order_market_buy(symbol=make_coin_pair()[1],quantity=total)
        else:
            buy = myBinance.order_market_buy(symbol=make_coin_pair()[1],quantity=settings.AMOUNT_TO_TRADE+1)
        print(buy)
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Binance, buy_binance:", error)
        else:
            pass

def sell_nance():
    '''Sell coins at binance'''
    try:
        sell = myBinance.order_market_sell(symbol=make_coin_pair()[1],quantity=settings.AMOUNT_TO_TRADE)
        print(sell)
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Binance, sell_binance:", error)
        else:
            pass

def check_liquidity(Binance, Bittrex):
    '''Used to check orderbook before making a trade to ensure liquidity for trade. '''
    liquid = 0
    if(Binance > 0 and Bittrex == 0):
        Bittrex_Ask_Orderbook = float(myBittrex.get_orderbook('BTC-NXS')['result']['sell'][0]['Quantity'])
        Binance_Bid_Orderbook = float(myBinance.get_order_book(symbol='NXSBTC')['bids'][0][1])
        if(Bittrex_Ask_Orderbook > settings.AMOUNT_TO_TRADE and Binance_Bid_Orderbook > (settings.AMOUNT_TO_TRADE*1.1)):
           liquid = 1
            
    elif(Bittrex > 0 and Binance == 0):
        Bittrex_Bid_Orderbook = myBittrex.get_orderbook('BTC-NXS')['result']['buy'][0]['Quantity']
        Binance_Ask_Orderbook = myBinance.get_order_book(symbol='NXSBTC')['asks'][0][1]
        if(Bittrex_Bid_Orderbook > settings.AMOUNT_TO_TRADE and Binance_Ask_Orderbook > (settings.AMOUNT_TO_TRADE*1.1)):
           liquid = 1
    return liquid
        
def backend_logic():
    '''Determine high/low, diff percent, and if trade is needed'''
    trex_ask = get_prices()[0]
    trex_bid = get_prices()[1]
    nance_ask = get_prices()[2]
    nance_bid = get_prices()[3]
    traded = 0
    Binance = 0
    Bittrex = 0
    if(settings.DRY_RUN or settings.DEBUG > 0):
        print("")
        print("Pricing Debug Stats:")
        print("Binance Ask:", nance_ask)
        print("Bittrex Ask:", trex_ask)
        print("Binance Bid:", nance_bid)
        print("Bittrex Bid:", trex_bid)
        print("")
        
    if(nance_bid>trex_ask): #Binance market sell price > bittrex market buy price
        diff = nance_bid-trex_ask
        percent = (diff/nance_ask)*100
        Binance = 1
        Bittrex = 0
        if(settings.DRY_RUN or settings.DEBUG > 0):
            print("Binance Market SELL Price > Bittrex Market BUY Price")
            print("Difference between Binance SELL and Bittrex BUY Price:", round(percent, 2), "%")
            print("Needs to be:", settings.DESIRED_PERCENT_GAIN, "%")
            print("")
        if(percent > settings.DESIRED_PERCENT_GAIN and percent > 0):
            now = datetime.datetime.now()
            value = settings.AMOUNT_TO_TRADE*nance_bid
            if(enough_balance_to_run() or settings.DRY_RUN):
                liquid = check_liquidity(Binance, Bittrex)
                if(liquid > 0):
                    if(not settings.DRY_RUN):
                        sell_nance()
                        buy_trex(value)
                    print("")
                    print("-"*30)
                    print(now.strftime("%Y-%m-%d %H:%M:%S"))
                    print("Trade Occurred! Sold at Binance for", nance_bid, "\nBought at Bittrex for", remove_exponent(str(trex_ask)))
                    if(settings.GAIN_BTC):
                        print("Total gain of", percent, "%, or", remove_exponent(str(diff)), "satoshi per", settings.COIN, "=", remove_exponent(str(diff))*settings.AMOUNT_TO_TRADE)
                    else:
                        coin_amount = (float(remove_exponent(str(diff)))*trex_ask)*settings.AMOUNT_TO_TRADE
                        print("Total gain of", percent, "%")
                        print("-"*30)
                        print("")
                        traded = 1
                else:
                    print("Trade conditions met, but lacking liquidity in orderbooks")
        
    elif(trex_bid>nance_ask): # IF bittrex market sell price > binance market buy
        diff = trex_bid-nance_ask
        percent = (diff/trex_ask)*100
        Binance = 0
        Bittrex = 1
        if(settings.DRY_RUN or settings.DEBUG > 0):
            print("Bittrex Market SELL Price > Binance Market BUY Price")
            print("Difference between Bittrex SELL and Binance BUY Price:", round(percent, 2), "%")
            print("Needs to be:", settings.DESIRED_PERCENT_GAIN, "%")
            print("")
        if(percent > settings.DESIRED_PERCENT_GAIN and percent > 0):
            value = settings.AMOUNT_TO_TRADE*trex_bid
            if(enough_balance_to_run() or settings.DRY_RUN):
                liquid = check_liquidity(Binance, Bittrex)
                if(liquid > 0):
                    if(not settings.DRY_RUN):
                        sell_trex()
                        buy_nance(value)
                    print("")
                    print("-"*30)
                    print("Trade Occurred! Sold at Bittrex for", remove_exponent(str(trex_bid)), "\nBought at Binance for", nance_ask)
                    if(settings.GAIN_BTC):
                        print("Total gain of", percent, "%, or", remove_exponent(str(diff)), "satoshi per", settings.COIN, "=", remove_exponent(str(diff))*settings.AMOUNT_TO_TRADE)
                    else:
                        coin_amount = (float(remove_exponent(str(diff)))*nance_ask)*settings.AMOUNT_TO_TRADE
                        print("Total gain of", percent, "%")
                        print("-"*30)
                        print("")
                        traded = 1                    
                else:
                    print("Trade conditions met, but lacking liquidity in orderbooks")
    else:
        if(settings.DRY_RUN or settings.DEBUG > 0):
            print("Waiting for:", settings.DESIRED_PERCENT_GAIN, "% Bid/Ask price difference.")
            print("")
    return traded

def nance_send_btc(btc_diff):
    '''Send btc from binance '''
    binance_btc_address = myBinance.get_deposit_address(asset='BTC')['address']
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
    bittrex_btc_address = myBittrex.get_deposit_address('BTC')['result']['Address']
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
    binance_coin_address = myBinance.get_deposit_address(asset=settings.COIN)['address']
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
    bittrex_coin_address = myBittrex.get_deposit_address(settings.COIN)['result']['Address']
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
    if(nance_btc > 0 and trex_btc > 0):
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
        time.sleep(3600)
    else:
        pass

def main(COUNTER, TRADE_COUNTER):
    '''Main function, pull everything together to run'''
    if(enough_balance_to_run() or settings.DRY_RUN):
        traded = backend_logic()
        if(traded == 1):
            TRADE_COUNTER = TRADE_COUNTER+1
            print("Sleeping after trade.")
            time.sleep(settings.SLEEP_AFTER_TRADE)
        if(COUNTER%10 == 0 and COUNTER != 0):
            print("Run-Count:", COUNTER)
            print("Trade-Count:", TRADE_COUNTER)
            balance_debug()
        if(traded == 1 and not enough_balance_to_run()):
            if(not settings.DRY_RUN):
                if(settings.ENABLE_WITHDRAWLS):
                    equalize_balances()
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
print("Liquidity Module: Active")
print("Withdrawls Enabled:", settings.ENABLE_WITHDRAWLS)
print("Debug level:", settings.DEBUG)
print("")
btc_price = myBinance.get_ticker(symbol=make_coin_pair()[1])['askPrice']
btc_amount = (float(btc_price)*float(settings.AMOUNT_TO_TRADE))*settings.DESIRED_CYCLES
print("needed btc per account:", round(btc_amount, 8))
print("needed", settings.COIN, " per account:", float(settings.AMOUNT_TO_TRADE)*settings.DESIRED_CYCLES)
print("")
balance_debug()
COUNTER = 0
TRADE_COUNTER = 0
while True:
    try:
        main(COUNTER, TRADE_COUNTER)
        COUNTER = COUNTER+1
    except:
        main(COUNTER, TRADE_COUNTER)
        COUNTER = COUNTER+1
