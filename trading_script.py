import MetaTrader5 as mt5
import pandas as pd
import time  # Importing time module for sleep functionality
import streamlit as st

st.write("My first trading Automation")

# Initialize MT5 connection
if not mt5.initialize():
    print(f"Failed to initialize, error code: {mt5.last_error()}")
else:
    print("MT5 initialized successfully")

# Check account info
account_info = mt5.account_info()
if account_info is None:
    print("Failed to retrieve account info")
else:
    print(f"Account Info: {account_info}")

# Select the EURUSD symbol
symbol = "EURUSDm"  # Using the mini version
if not mt5.symbol_select(symbol):
    print(f"Failed to select symbol: {symbol}, Error code: {mt5.last_error()}")
else:
    print(f"Symbol {symbol} selected")

    # Get the last 100 bars of 1-minute data for EURUSD
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 100)

    if rates is None or len(rates) == 0:
        print(f"Failed to retrieve data for {symbol}. Error code: {mt5.last_error()}")
    else:
        rates_df = pd.DataFrame(rates)

        # Check if 'time' column exists before accessing it
        if 'time' in rates_df.columns:
            rates_df['time'] = pd.to_datetime(rates_df['time'], unit='s')
            print(rates_df.head())
        else:
            print("No 'time' column found in the data")

        # Check for open positions
        open_positions = mt5.positions_get()
        if open_positions:
            print(f"Open Positions: {open_positions}")
        else:
            print("No open positions.")

        # Define a buy order for EURUSD
        trade_request = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': symbol,
            'volume': 0.1,  # Adjust this based on your account and strategy
            'type': mt5.ORDER_TYPE_SELL,
            'price': mt5.symbol_info_tick(symbol).ask,
            'deviation': 20,
            'magic': 234000,
            'comment': "Test sell order for EURUSD",
            'type_time': mt5.ORDER_TIME_GTC,
            'type_filling': mt5.ORDER_FILLING_IOC,
        }

        # Send the trade request with extended retry mechanism
        for attempt in range(5):  # Retry up to 5 times
            result = mt5.order_send(trade_request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"Order placed successfully, retcode: {result.retcode}")
                break
            else:
                print(f"Order failed, retcode: {result.retcode}. Retrying in 5 seconds...")
                time.sleep(5)  # Wait for 5 seconds before retrying

# Shutdown MT5 connection
mt5.shutdown()
