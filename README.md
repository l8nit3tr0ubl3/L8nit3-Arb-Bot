# L8nit3's Arbitration Bot
##
This is currently used to find arbitration trade oppourtunities  
between crypto pairs at Binanvce and Bittrex.

IT IS A WORK IN PROGRESS, and is in no way ready for ANYONE to use  
in a real setting on a real account. Do so at your own risk!!!

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

# Coming Soon:
##
- CCXT based re-write for many new features including:  
    - Multiple more exchange options.  
    - Create a list of pairs in settings and run all in one instance of the script.  
    - Cleaner, faster running for better results and more stable profit.  
- Auto balance equalization after trading for continuous 24/7/365 running (partially implemented)  
- Option to exchange BTC to USDT/USDC/DOGE to pay less fees during equalization.  