BITTREX_API_KEY = ''
BITTREX_API_SECRET = ''
BINANCE_API_KEY = ''
BINANCE_API_SECRET = ''
COIN = 'NXS' #Coin to use
COIN_PAIR_BITTREX = 'BTC-NXS' #Pair at bittrex
COIN_PAIR_BINANCE = 'NXSBTC' #Pair at binance
AMOUNT_TO_SELL = 50 #Amount of chosen coin to sell each trade
DESIRED_PERCENT_GAIN = 1.5 #Desired gain every trade
DEBUG = 0 #0=off 1=stats 2=stats+errors
DRY_RUN = True #No withdrawl or trades, just test
ENABLE_WITHDRAWLS = False #trade, but dont auto-equalize balances
GAIN_BTC = False #True = stack sats, False = stack coin
SLEEP_BETWEEN_CYCLE = 3 #Sleep between price checks
SLEEP_AFTER_TRADE = 300 #Sleep after trade
