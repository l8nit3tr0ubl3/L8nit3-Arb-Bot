# L8nit3's Arbitration Bot
##
This is currently used to find arbitration trade oppourtunities  
between crypto pairs at Binance and Bittrex.

IT IS A WORK IN PROGRESS, and is in no way ready for ANYONE to use  
in a real setting on a real account. Do so at your own risk!!!

# Requirements  
##  
- pip install python-bittrex  
- pip install python-binance  
- pip install simple_settings  

# Features:
##
- Uses an external settings file, allow multiple instances to be run  
for different coin pairs.  
- Demo only mode that disabled trading and withdrawls. Output is still  
displayed for debugging purposes. 
- Choose your desired percent gain per trade within settings.  
- Multiple debug output levels for a cleaner terminal.  
- 2 gaining modes, one stacks sats, the other stack your desired coin.  
- Set a desired sleep time between trades to avoid overtrading the same signal.  
- Liquidity module, only trade if orderbook has sufficient liquidity to make BOTH trades.    
- Flip-Mode: Once a trade happens, do not trade again until opposite trade can occur.   
(eg. Bought Binance, wait untill buy Bittrex. Avoid needing to equalize balances.)  
- Check multiple coin pairs in one instance. 
- Profit-tracking per coin. (percent_earned_per_trade/2 to account for both account balances)  
- Accounts for trading fees in percentages displayed and in backend calculations  

# Coming Soon:
##
- CCXT based re-write for many new features including:  
    - Multiple more exchange options.  
    - ~Create a list of pairs in settings and run all in one instance of the script.~ - DONE  
    - Cleaner, faster running for better results and more stable profit.  
- Auto balance equalization after trading for continuous 24/7/365 running (partially implemented)  
- Option to exchange BTC to USDT/USDC/DOGE to pay less fees during equalization.  

# Screenshot
##
![image of bot](https://i.imgur.com/g9Cwulr.jpg)
