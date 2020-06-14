BINANCE_API_KEY = 'API_KEY_HERE'
BINANCE_API_SECRET = 'API_SECRET_HERE'
BITTREX_API_KEY = 'API_KEY_HERE'
BITTREX_API_SECRET = 'API_SECRET_HERE'
COIN_LIST = {'NXS':['150', '2.5'],
             'KMD': ['10', '3.2'],
             'DOGE': ['2000', '6'],
             'LTC': ['0.1', '4'],
             'PIVX':['25', '2']} #Coin : Amount : percent
DEBUG = 1 #0=off 1=stats 2=stats+errors
DESIRED_CYCLES = 1 #Number of trades before equalize, if FLIP_MODE set to 0
DRY_RUN = False #No withdrawl or trades, just test
FLIP_MODE = True #Flip buy and sell so no withdrawl is needed
GAIN_BTC = True #True = stack sats, False = stack coin
LIQUIDITY_MODULE = True #Check orrderbook before trading
SLEEP_AFTER_TRADE = 0.1 #Sleep after trade
SLEEP_BETWEEN_CYCLE = 0.1 #Sleep between price checks
