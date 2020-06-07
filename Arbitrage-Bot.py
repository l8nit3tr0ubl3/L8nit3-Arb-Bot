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
    print("Withdrawls Enabled:", settings.ENABLE_WITHDRAWLS)
    print("_"*30)
    print("")
    time.sleep(4)

def get_trex_balance(COIN):
    '''Ensure account has funds to opperate script'''
    try:
        btc = myBittrex.get_balance('BTC')['result']['Available']
        if(btc == None):
            btc = 0.0
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Bittrex get_balance:", error)
        else:
            pass
    try:
        Coin = myBittrex.get_balance(COIN)['result']['Available']
        if(Coin == None):
            Coin = 0.0
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Bittrex get_balance:", error)
        else:
            pass
    return btc,Coin

def get_nance_balance(COIN):
    '''Ensure account has funds to opperate script'''
    try:
        btc = myBinance.get_asset_balance(asset='BTC')['free']
        Coin = myBinance.get_asset_balance(asset=COIN)['free']
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Binance get_balance:", error)
        else:
            pass
    return btc,Coin

def balance_debug(COIN):
    '''Check balances and print to user'''
    print("Balance Debug Stats:")
    print("Binance Balances: BTC={0} {1}={2}".format(get_nance_balance(COIN)[0], COIN, get_nance_balance(COIN)[1]))
    print("Bittrex Balances: BTC={0} {1}={2}".format(get_trex_balance(COIN)[0], COIN, get_trex_balance(COIN)[1]))
    print("")

def enough_balance_to_run(COIN):
    '''Check balances and see if there is enough COIN/btc'''
    btc_price = myBinance.get_ticker(symbol=make_coin_pair(COIN)[1])['askPrice']
    needed_btc = float((float(btc_price)*float(AMOUNT_TO_TRADE))*settings.DESIRED_CYCLES)
    needed_coin = float(float(AMOUNT_TO_TRADE)*settings.DESIRED_CYCLES)
    is_enough = True
    if(float(get_nance_balance(COIN)[0])<needed_btc or
       float(get_trex_balance(COIN)[0])<needed_btc or
       float(get_nance_balance(COIN)[1])<needed_coin or
       float(get_trex_balance(COIN)[1])<needed_coin):
        is_enough = False
    return is_enough

def make_coin_pair(COIN):
    '''Take COIN and make correct pair for each exchange'''
    coin_symbol = COIN
    bittrex_pair = "BTC-" + coin_symbol
    binance_pair = coin_symbol + "BTC"
    return bittrex_pair, binance_pair

def get_prices(COIN):
    '''Check COIN price at both exchanges'''
    try:
        nance_ask = float(myBinance.get_ticker(symbol=make_coin_pair(COIN)[1])['askPrice'])
        nance_bid = float(myBinance.get_ticker(symbol=make_coin_pair(COIN)[1])['bidPrice'])
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Binance get_prices:", error)
        else:
            pass

    try:
        trex_ask = float(myBittrex.get_ticker(make_coin_pair(COIN)[0])['result']['Ask'])
        trex_bid = float(myBittrex.get_ticker(make_coin_pair(COIN)[0])['result']['Bid'])
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Bittrex get_prices:", error)
        else:
            pass
        
    return trex_ask, trex_bid, nance_ask, nance_bid

def buy_trex(value, COIN):
    '''Buy at Bittrex'''
    try:
        if(not settings.GAIN_BTC):
            buy = myBittrex.buy_limit(market=make_coin_pair(COIN)[0], quantity=value, rate=get_prices()[1]+0.00000001)
        else:
            buy = myBittrex.buy_limit(market=make_coin_pair(COIN)[0], quantity=AMOUNT_TO_TRADE+settings.WITHDRAWL_FEE_COIN, rate=get_prices()[1]+0.00000001)
        print(buy)
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Bittrex, buy_bittrex:", error)
        else:
            pass
        
def sell_trex(COIN):
    '''Sell at Bittrex'''
    try:
        sell = myBittrex.sell_limit(market=make_coin_pair(COIN)[0], quantity=AMOUNT_TO_TRADE, rate=get_prices()[2]-0.00000001)
        print(sell)
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Bittrex, sell_bittrex:", error)
        else:
            pass

def buy_nance(value, COIN):
    '''Buy coins at binance'''
    try:
        if(not settings.GAIN_BTC):
            buy = myBinance.order_market_buy(symbol=make_coin_pair(COIN)[1],quantity=value)
        else:
            buy = myBinance.order_market_buy(symbol=make_coin_pair(COIN)[1],quantity=AMOUNT_TO_TRADE+settings.WITHDRAWL_FEE_COIN)
        print(buy)
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Binance, buy_binance:", error)
        else:
            pass

def sell_nance(COIN):
    '''Sell coins at binance'''
    try:
        sell = myBinance.order_market_sell(symbol=make_coin_pair(COIN)[1],quantity=AMOUNT_TO_TRADE)
        print(sell)
    except Exception as error:
        if(settings.DEBUG == 2):
            print("Error occurred Binance, sell_binance:", error)
        else:
            pass

def check_liquidity(Binance, Bittrex, COIN, AMOUNT_TO_TRADE):
    '''Used to check orderbook before making a trade to ensure liquidity for trade. '''
    liquid = 0
    if(Binance > 0 and Bittrex == 0):
        Bittrex_Ask_Orderbook = float(myBittrex.get_orderbook(make_coin_pair(COIN)[0])['result']['sell'][0]['Quantity'])
        Binance_Bid_Orderbook = float(myBinance.get_order_book(symbol=make_coin_pair(COIN)[1])['bids'][0][1])
        if(Bittrex_Ask_Orderbook > AMOUNT_TO_TRADE and Binance_Bid_Orderbook > (AMOUNT_TO_TRADE*1.1)):
           liquid = 1
            
    elif(Bittrex > 0 and Binance == 0):
        Bittrex_Bid_Orderbook = myBittrex.get_orderbook(make_coin_pair(COIN)[0])['result']['buy'][0]['Quantity']
        Binance_Ask_Orderbook = myBinance.get_order_book(symbol=make_coin_pair(COIN)[1])['asks'][0][1]
        if(Bittrex_Bid_Orderbook > AMOUNT_TO_TRADE and Binance_Ask_Orderbook > (AMOUNT_TO_TRADE*1.1)):
           liquid = 1
    return liquid
        
def backend_logic(COIN, AMOUNT_TO_TRADE, DESIRED_PERCENT_GAIN):
    '''Determine high/low, diff percent, and if trade is needed'''
    trex_ask = get_prices(COIN)[0]
    trex_bid = get_prices(COIN)[1]
    nance_ask = get_prices(COIN)[2]
    nance_bid = get_prices(COIN)[3]
    traded = 0
        
    if((nance_bid>trex_ask) and ((settings.FLIP_MODE and Binance == 0) or (not settings.FLIP_MODE))): #Binance market sell price > bittrex market buy price
        diff = nance_bid-trex_ask
        percent = (diff/nance_ask)*100
        Binance = 1
        Bittrex = 0
        if(settings.DRY_RUN or settings.DEBUG > 0):
            print("Binance {2} SELL Price {0} > Bittrex {2} BUY Price {1}".format(
                nance_bid, trex_ask, COIN))
            print("Potential Gain: {0}%".format(round(percent, 2)))
            print("Needs to be: {0}%".format(DESIRED_PERCENT_GAIN))
            print("")
        if(percent > DESIRED_PERCENT_GAIN and percent > 0):
            now = datetime.datetime.now()
            value = AMOUNT_TO_TRADE*(1.0+(DESIRED_PERCENT_GAIN/100))
            if(enough_balance_to_run(COIN) or settings.DRY_RUN):
                if(settings.LIQUIDITY_MODULE):
                    liquid = check_liquidity(Binance, Bittrex, COIN, AMOUNT_TO_TRADE)
                else:
                    print("Liquidity Module Skipping")
                    liquid = 1
                if(liquid > 0):
                    if(not settings.DRY_RUN):
                        sell_nance(COIN)
                        buy_trex(value, COIN)
                    print("")
                    print("-"*30)
                    print(now.strftime("%Y-%m-%d %H:%M:%S"))
                    print("Trade Occurred! Sold at Binance for {0}\nBought at Bittrex for {1}"
                          .format(nance_bid, trex_ask))
                    if(settings.GAIN_BTC):
                        print("Total gain of {0}%, or {1} satoshi per {2} = {3}"
                              .format(percent, diff, COIN, diff*AMOUNT_TO_TRADE))
                    else:
                        print("Total gain of {0}%".format(percent))
                        print("-"*30)
                        print("")
                        traded = 1
                else:
                    print("#Trade conditions met, but lacking liquidity in orderbooks#")
                    print("")
        
    elif((trex_bid>nance_ask)  and ((settings.FLIP_MODE and Bittrex == 0) or (not settings.FLIP_MODE))): # IF bittrex market sell price > binance market buy
        diff = trex_bid-nance_ask
        percent = (diff/trex_ask)*100
        Binance = 0
        Bittrex = 1
        if(settings.DRY_RUN or settings.DEBUG > 0):
            print("Bittrex {2} SELL Price {0} > Binance {2} BUY Price {1}".format(
                trex_bid, nance_ask, COIN))
            print("Potential Gain: {0}%".format(round(percent, 2)))
            print("Needs to be: {0}%".format(DESIRED_PERCENT_GAIN))
            print("")
        if(percent > DESIRED_PERCENT_GAIN and percent > 0):
            value = AMOUNT_TO_TRADE*(1.0+(DESIRED_PERCENT_GAIN/100))
            if(enough_balance_to_run(COIN) or settings.DRY_RUN):
                if(settings.LIQUIDITY_MODULE):
                    liquid = check_liquidity(Binance, Bittrex, COIN, AMOUNT_TO_TRADE)
                else:
                    print("Liquidity Module Skipping")
                    liquid = 1
                if(liquid > 0):
                    if(not settings.DRY_RUN):
                        sell_trex(COIN)
                        buy_nance(value, COIN)
                    print("")
                    print("-"*30)
                    print("Trade Occurred! Sold at Bittrex for {0} \nBought at Binance for {1}"
                          .format(trex_bid, nance_ask))
                    if(settings.GAIN_BTC):
                        print("Total gain of {0}%, or {1} satoshi per {2} = {3}"
                              .format(percent, diff, COIN, diff*AMOUNT_TO_TRADE))
                    else:
                        print("Total gain of {0}%".format(percent))
                        print("-"*30)
                        print("")
                        traded = 1
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
            print("Pricing Debug Stats:")
            print("{3} Binance Sell: {0} | Bittrex Buy: {1} Potential Gain={2}%".format(nance_bid, trex_ask, round(percent2, 2), COIN))
            print("{3} Bittrex Sell: {0} | Binance Buy: {1} Potential Gain={2}%".format(trex_bid, nance_ask, round(percent1, 2), COIN))
            if(not settings.FLIP_MODE):
                print("Waiting for positive Bid/Ask price difference.")
            else:
                print("Waiting for opposite trade to be profitable.")
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
    
def nance_send_coin(coin_diff, COIN):
    '''Send coins from binance'''
    binance_coin_address = myBinance.get_deposit_address(asset=COIN)['address']
    try:
        if(not settings.DRY_RUN):
            send = myBinance.withdraw(asset='BTC',address=binance_coin_address,amount=coin_diff)
            print(send)
        else:
            print("Dry Run - nance", COIN, "withdrawl amount:", coin_diff)
    except Exception as error:
        print("Error occurred binance, withdraw_coin:", error)

def trex_send_coin(coin_diff, COIN):
    '''Send coins from bittrex'''
    bittrex_coin_address = myBittrex.get_deposit_address(COIN)['result']['Address']
    try:
        if(not settings.DRY_RUN):
            send = myBittrex.withdraw(COIN, coin_diff, bittrex_coin_address)
            print(send)
        else:
            print("Dry Run - trex", COIN, "withdrawl amount:", coin_diff)
    except Exception as error:
        print("Error occurred bittrex, withdraw_coin:", error)

def equalize_balances(COIN):
    '''Equalize balances at both exchanges for next run'''
    nance_btc = float(get_nance_balance(COIN)[0])
    nance_coin = float(get_nance_balance(COIN)[1])
    trex_btc = float(get_trex_balance(COIN)[0])
    trex_coin = float(get_trex_balance(COIN)[1])
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

def main(COUNTER, TRADE_COUNTER, COIN, AMOUNT_TO_TRADE, DESIRED_PERCENT_GAIN):
    '''Main function, pull everything together to run'''
    if(enough_balance_to_run(COIN) or settings.DRY_RUN):
        traded = backend_logic(COIN, AMOUNT_TO_TRADE, DESIRED_PERCENT_GAIN)
        if(traded == 1):
            TRADE_COUNTER = TRADE_COUNTER+1
            print("Sleeping after trade.")
            time.sleep(settings.SLEEP_AFTER_TRADE)
        if(COUNTER%10 == 0 and COUNTER != 0):
            print("Run-Count:", COUNTER)
            print("Trade-Count:", TRADE_COUNTER)
            for COIN in settings.COIN_LIST:
                balance_debug(COIN)
        if(traded == 1 and not enough_balance_to_run(COIN) and settings.ENABLE_WITHDRAWLS):
            if(not settings.DRY_RUN):
                equalize_balances(COIN)
                balance_debug(COIN)
        elif(traded == 0):
            time.sleep(settings.SLEEP_BETWEEN_CYCLE)
    else:
        print("Please Check Balances!")

def print_needed(COIN, AMOUNT_TO_TRADE):
    btc_price = myBinance.get_ticker(symbol=make_coin_pair(COIN)[1])['askPrice']
    btc_amount = (float(btc_price)*float(AMOUNT_TO_TRADE))*settings.DESIRED_CYCLES
    print("Needed BTC per account:", round(btc_amount, 8))
    print("Needed", COIN, " per account:", float(AMOUNT_TO_TRADE)*settings.DESIRED_CYCLES)
#End Of Functions

#Print Title, And Run
print_title()
for COIN in settings.COIN_LIST:
    AMOUNT_TO_TRADE = settings.COIN_LIST[COIN][0]
    DESIRED_PERCENT_GAIN = settings.COIN_LIST[COIN][1]
    print_needed(COIN, AMOUNT_TO_TRADE)
    print("Target percent:", DESIRED_PERCENT_GAIN, "\n")
COUNTER = 0
TRADE_COUNTER = 0
RETRY = 0

while True:
    print("_"*30)
    for COIN in settings.COIN_LIST:
        AMOUNT_TO_TRADE = settings.COIN_LIST[COIN][0]
        DESIRED_PERCENT_GAIN = settings.COIN_LIST[COIN][1]
        try:
            main(COUNTER, TRADE_COUNTER, COIN, AMOUNT_TO_TRADE, DESIRED_PERCENT_GAIN)
        except:
            time.sleep(3)
            while(RETRY<3):
                print("Script crashed, retrying......")
                print_title()
                main(COUNTER, TRADE_COUNTER, COIN, AMOUNT_TO_TRADE, DESIRED_PERCENT_GAINE)
                RETRY += 1
    COUNTER = COUNTER+1
    print("_"*30)
