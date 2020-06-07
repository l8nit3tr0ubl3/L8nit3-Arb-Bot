AMOUNT_TO_TRADE = 290 #Amount of chosen coin to sell each trade
BINANCE_API_KEY = 'API_KEY_HERE'
BINANCE_API_SECRET = 'API_SECRET_HERE'
BITTREX_API_KEY = 'API_KEY_HERE'
BITTREX_API_SECRET = 'API_SECRET_HERE'
COIN_LIST = {'NXS':['5', '4'], 'DASH':['0.1', '3'], 'LTC':['0.1', '3.5']} #Coin to use : Amount to trade : percent gain
DEBUG = 1 #0=off 1=stats 2=stats+errors
DESIRED_CYCLES = 1 #Number of trades before equalize
DRY_RUN = True #No withdrawl or trades, just test
ENABLE_WITHDRAWLS = False #trade, but dont auto-equalize balances
FLIP_MODE = False #Flip buy and sell so no withdrawl is needed
GAIN_BTC = True #True = stack sats, False = stack coin
LIQUIDITY_MODULE = True #Check orrderbook before trading
SLEEP_AFTER_TRADE = 120 #Sleep after trade
SLEEP_BETWEEN_CYCLE = 1 #Sleep between price checks
WITHDRAWL_FEE_COIN = 0.25
