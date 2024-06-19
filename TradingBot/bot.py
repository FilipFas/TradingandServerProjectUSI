import os
import logging
import pandas as pd
import ta
import asyncio
import websockets
import json
from binance.client import AsyncClient
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException
import ssl
import certifi
from collections import deque
import uuid  # To generate unique trade IDs

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Store the candlestick data using deque for efficient appends and pops
kline_data = deque(maxlen=1000)

# Environment variables for API keys
current_directory = os.path.dirname(os.path.abspath(__file__))
API_path = os.path.join(current_directory, "api_key.json")

# Fetch API keys
def get_API(api_path):
    try:
        with open(api_path, 'r') as binance_credentials:
            credentials = json.load(binance_credentials)
        api_key = credentials['binance']['api_key']
        api_secret = credentials['binance']['api_secret']
        return api_key, api_secret
    except (FileNotFoundError, KeyError) as e:
        logging.error(f"Error loading API keys: {e}")
        exit(1)

api_keys = get_API(API_path)
API_KEY, API_SECRET = api_keys

# Global position dictionary
current_position = {'BTCUSDT': 0}  # Neutral position
trade_ids = {'BTCUSDT': None}  # Track trade IDs

# Global variable to store the LOT_SIZE, MIN_NOTIONAL, and TICK_SIZE filters
LOT_SIZE = None
MIN_NOTIONAL = None
TICK_SIZE = None

pending_order = None

# DataFrame to store trade results
csv_filename = 'trade_results.csv'
if not os.path.isfile(csv_filename):
    trade_results = pd.DataFrame(columns=['trade_id', 'ticker', 'date', 'nav', 'type', 'signal_price', 'quantity', 'opened', 'closed', 'vol', 'returns', 'entry_time', 'closing_time'])
    trade_results.to_csv(csv_filename, index=False)
else:
    trade_results = pd.read_csv(csv_filename)

async def fetch_lot_size_and_min_notional(client, symbol):
    global LOT_SIZE, MIN_NOTIONAL, TICK_SIZE
    try:
        exchange_info = await client.futures_exchange_info()
        for s in exchange_info['symbols']:
            if s['symbol'] == symbol:
                for f in s['filters']:
                    if f['filterType'] == 'LOT_SIZE':
                        LOT_SIZE = f
                    elif f['filterType'] == 'MIN_NOTIONAL':
                        MIN_NOTIONAL = f
                    elif f['filterType'] == 'PRICE_FILTER':
                        TICK_SIZE = float(f['tickSize'])
                break
    except BinanceAPIException as e:
        logging.error(f"Error fetching trading rules: {e}")
        LOT_SIZE = {'minQty': '0.001', 'maxQty': '1000', 'stepSize': '0.001'}
        MIN_NOTIONAL = {'notional': '10.00'}
        TICK_SIZE = 0.1
        logging.info("Using default LOT_SIZE, MIN_NOTIONAL, and TICK_SIZE values")

    logging.info(f"LOT_SIZE: {LOT_SIZE}, MIN_NOTIONAL: {MIN_NOTIONAL}, TICK_SIZE: {TICK_SIZE}")

def adjust_quantity(quantity, price):
    global LOT_SIZE, MIN_NOTIONAL
    if LOT_SIZE and MIN_NOTIONAL:
        min_qty = float(LOT_SIZE['minQty'])
        max_qty = float(LOT_SIZE['maxQty'])
        step_size = float(LOT_SIZE['stepSize'])
        min_notional = float(MIN_NOTIONAL['notional'])

        quantity = max(min_qty, min(max_qty, quantity))
        quantity = quantity - (quantity % step_size)
        notional_value = quantity * price

        if notional_value < min_notional:
            quantity = max(min_qty, min(max_qty, min_notional / price))
            quantity = quantity - (quantity % step_size)

    if quantity == 0:
        quantity = float(LOT_SIZE['minQty']) if LOT_SIZE else 0.00001

    quantity_precision = len(str(step_size).split('.')[1])
    return f'{quantity:.{quantity_precision}f}'

def adjust_price(price, increment=0.1):
    global TICK_SIZE
    tick_size = TICK_SIZE if TICK_SIZE else 0.1
    price = round(price + increment, len(str(tick_size).split('.')[1]))
    return price

async def changepos(symbol, position):
    global current_position
    if position == 'long':
        current_position[symbol] = 1
    elif position == 'short':
        current_position[symbol] = -1
    else:
        current_position[symbol] = 0

async def check_order_status(client, order_id, symbol='BTCUSDT'):
    try:
        order = await client.futures_get_order(symbol=symbol, orderId=order_id)
        return order['status'] == 'FILLED'
    except BinanceAPIException as e:
        logging.error(f"Error checking order status: {e}")
        return False

async def check_balance(client, asset):
    try:
        balance = await client.futures_account_balance()
        for b in balance:
            if b['asset'] == asset:
                return float(b['balance'])
        return 0.0
    except Exception as e:
        logging.error(f"Error fetching balance for {asset}: {e}")
        return 0.0

async def ensure_initial_balance(client, asset, required_balance):
    balance = await check_balance(client, asset)
    if balance < required_balance:
        logging.error(f"Insufficient {asset} balance to start trading. Required: {required_balance}, Available: {balance}")
        return False
    return True

async def record_trade(trade_id, ticker, date, trade_type, signal_price, quantity, opened_price, closed_price, vol, returns, entry_time, closing_time, btc_price, btc_balance, usdt_balance, filename='trade_results.csv'):
    nav = btc_balance * btc_price + usdt_balance
    new_trade = pd.DataFrame([{
        'trade_id': trade_id,
        'ticker': ticker,
        'date': date,
        'nav': nav,
        'type': trade_type,
        'signal_price': signal_price,
        'quantity': quantity,
        'opened': opened_price,
        'closed': closed_price,
        'vol': vol,
        'returns': returns,
        'entry_time': entry_time,
        'closing_time': closing_time
    }])
    global trade_results
    trade_results = pd.concat([trade_results, new_trade], ignore_index=True)
    trade_results.to_csv(filename, index=False)
    logging.info(f"Trade recorded and saved to {filename}")

async def update_trade(trade_id, closed_price, closing_time, filename='trade_results.csv'):
    global trade_results
    trade_results.loc[trade_results['trade_id'] == trade_id, 'closed'] = closed_price
    trade_results.loc[trade_results['trade_id'] == trade_id, 'closing_time'] = closing_time
    trade_results.to_csv(filename, index=False)
    logging.info(f"Trade with ID {trade_id} updated with closing information.")

async def get_market_price(client, symbol):
    try:
        ticker = await client.futures_symbol_ticker(symbol=symbol)
        return float(ticker['price'])
    except BinanceAPIException as e:
        logging.error(f"Error fetching market price: {e}")
        return None

async def cancel_order(client, order_id, symbol):
    try:
        await client.futures_cancel_order(symbol=symbol, orderId=order_id)
        logging.info(f"Canceled order: {order_id}")
    except BinanceAPIException as e:
        logging.error(f"Error canceling order: {e}")
        # Check the order status if cancel fails
        order_filled = await check_order_status(client, order_id, symbol)
        if order_filled:
            logging.info(f"Order {order_id} was actually filled. Updating position.")
            return 'FILLED'
        else:
            return 'NOT_FILLED'

def validate_notional_value(quantity, price):
    notional_value = quantity * price
    min_notional = float(MIN_NOTIONAL['notional'])
    return notional_value >= min_notional

async def handle_long_order(client, symbol, lastrow, usdt_balance, btc_price, current_time):
    try:
        order_quantity = 0.01
        order_quantity = adjust_quantity(order_quantity, lastrow['close'])
        market_price = await get_market_price(client, symbol)
        if market_price is None:
            return None, await check_balance(client, 'BTC'), usdt_balance
        order_price = adjust_price(market_price, increment=100)  # Adjusted to buy at $100 more than the current price

        if validate_notional_value(float(order_quantity), order_price):
            logging.info(f"Placing BUY order for {order_quantity} BTC at {order_price} USDT")
            order = await client.futures_create_order(
                symbol=symbol, side="BUY", type="LIMIT", timeInForce="GTC",
                quantity=order_quantity, price=order_price,
                recvWindow=5000
            )
            await asyncio.sleep(5)
            order_filled = await check_order_status(client, order['orderId'], symbol)
            if not order_filled:
                cancel_status = await cancel_order(client, order['orderId'], symbol)
                if cancel_status != 'FILLED':
                    return None, await check_balance(client, 'BTC'), await check_balance(client, 'USDT')
                else:
                    await changepos(symbol, 'long')
            else:
                await changepos(symbol, 'long')  # Update position to long after order fill

            # Record the trade when opened
            trade_id = str(uuid.uuid4())
            trade_ids[symbol] = trade_id
            await record_trade(
                trade_id=trade_id, ticker=symbol, date=current_time, trade_type='long',
                signal_price=lastrow['close'], quantity=order_quantity,
                opened_price=order_price, closed_price=None, vol=lastrow['volume'],
                returns=None, entry_time=current_time, closing_time=None,
                btc_price=btc_price, btc_balance=await check_balance(client, 'BTC'), usdt_balance=await check_balance(client, 'USDT')
            )
            return order, await check_balance(client, 'BTC'), await check_balance(client, 'USDT')
        else:
            logging.error("Order not placed: Notional value below minimum required.")
            return None, await check_balance(client, 'BTC'), usdt_balance
    except BinanceAPIException as e:
        logging.error(f"Error creating BUY order: {e}")
    return None, await check_balance(client, 'BTC'), usdt_balance

async def handle_short_order(client, symbol, lastrow, btc_balance, btc_price, current_time):
    try:
        order_quantity = 0.01
        order_quantity = adjust_quantity(order_quantity, lastrow['close'])
        market_price = await get_market_price(client, symbol)
        if market_price is None:
            return None, btc_balance, await check_balance(client, 'USDT')
        order_price = adjust_price(market_price, increment=-100)  # Adjusted to sell at $100 less than the current price

        if validate_notional_value(float(order_quantity), order_price):
            logging.info(f"Placing SELL (short) order for {order_quantity} BTC at {order_price} USDT")
            order = await client.futures_create_order(
                symbol=symbol, side="SELL", type="LIMIT", timeInForce="GTC",
                quantity=order_quantity, price=order_price,
                recvWindow=5000
            )
            await asyncio.sleep(5)
            order_filled = await check_order_status(client, order['orderId'], symbol)
            if not order_filled:
                cancel_status = await cancel_order(client, order['orderId'], symbol)
                if cancel_status != 'FILLED':
                    return None, await check_balance(client, 'BTC'), await check_balance(client, 'USDT')
                else:
                    await changepos(symbol, 'short')
            else:
                await changepos(symbol, 'short')  # Update position to short after order fill

            # Record the trade when opened
            trade_id = str(uuid.uuid4())
            trade_ids[symbol] = trade_id
            await record_trade(
                trade_id=trade_id, ticker=symbol, date=current_time, trade_type='short',
                signal_price=lastrow['close'], quantity=order_quantity,
                opened_price=order_price, closed_price=None, vol=lastrow['volume'],
                returns=None, entry_time=current_time, closing_time=None,
                btc_price=btc_price, btc_balance=await check_balance(client, 'BTC'), usdt_balance=await check_balance(client, 'USDT')
            )
            return order, await check_balance(client, 'BTC'), await check_balance(client, 'USDT')
        else:
            logging.error("Order not placed: Notional value below minimum required.")
            return None, btc_balance, await check_balance(client, 'USDT')
    except BinanceAPIException as e:
        logging.error(f"Error creating SELL (short) order: {e}")
    return None, btc_balance, await check_balance(client, 'USDT')

async def close_long_position(client, symbol, lastrow, btc_balance, btc_price, current_time):
    try:
        order_quantity = 0.01
        order_quantity = adjust_quantity(order_quantity, lastrow['close'])
        market_price = await get_market_price(client, symbol)
        if market_price is None:
            return None, btc_balance, await check_balance(client, 'USDT')
        order_price = adjust_price(market_price, increment=-100)  # Adjusted to sell at $100 less than the current price

        if validate_notional_value(float(order_quantity), order_price):
            logging.info(f"Placing SELL order for {order_quantity} BTC at {order_price} USDT to close long position.")
            order = await client.futures_create_order(
                symbol=symbol, side="SELL", type="LIMIT", timeInForce="GTC",
                quantity=order_quantity, price=order_price,
                recvWindow=5000
            )
            await asyncio.sleep(5)
            order_filled = await check_order_status(client, order['orderId'], symbol)
            if not order_filled:
                cancel_status = await cancel_order(client, order['orderId'], symbol)
                if cancel_status != 'FILLED':
                    return None, await check_balance(client, 'BTC'), await check_balance(client, 'USDT')
                else:
                    await changepos(symbol, 'neutral')
            else:
                await changepos(symbol, 'neutral')  # Update position to neutral after order fill

            # Update the trade record when closed
            trade_id = trade_ids[symbol]
            await update_trade(
                trade_id=trade_id, closed_price=order_price, closing_time=current_time
            )
            trade_ids[symbol] = None
            return order, await check_balance(client, 'BTC'), await check_balance(client, 'USDT')
        else:
            logging.error("Order not placed: Notional value below minimum required.")
            return None, btc_balance, await check_balance(client, 'USDT')
    except BinanceAPIException as e:
        logging.error(f"Error creating SELL order: {e}")
    return None, btc_balance, await check_balance(client, 'USDT')

async def close_short_position(client, symbol, lastrow, usdt_balance, btc_price, current_time):
    try:
        order_quantity = 0.01
        order_quantity = adjust_quantity(order_quantity, lastrow['close'])
        market_price = await get_market_price(client, symbol)
        if market_price is None:
            return None, await check_balance(client, 'BTC'), usdt_balance
        order_price = adjust_price(market_price, increment=100)  # Adjusted to buy at $100 more than the current price
        required_usdt = float(order_quantity) * order_price

        if usdt_balance >= required_usdt and validate_notional_value(float(order_quantity), order_price):
            logging.info(f"Placing BUY order for {order_quantity} BTC at {order_price} USDT to close short position.")
            order = await client.futures_create_order(
                symbol=symbol, side="BUY", type="LIMIT", timeInForce="GTC",
                quantity=order_quantity, price=order_price,
                recvWindow=5000
            )
            await asyncio.sleep(5)
            order_filled = await check_order_status(client, order['orderId'], symbol)
            if not order_filled:
                cancel_status = await cancel_order(client, order['orderId'], symbol)
                if cancel_status != 'FILLED':
                    return None, await check_balance(client, 'BTC'), await check_balance(client, 'USDT')
                else:
                    await changepos(symbol, 'neutral')
            else:
                await changepos(symbol, 'neutral')  # Update position to neutral after order fill

            # Update the trade record when closed
            trade_id = trade_ids[symbol]
            await update_trade(
                trade_id=trade_id, closed_price=order_price, closing_time=current_time
            )
            trade_ids[symbol] = None
            return order, await check_balance(client, 'BTC'), await check_balance(client, 'USDT')
        else:
            logging.error("Order not placed: Notional value below minimum required or insufficient USDT balance.")
            return None, await check_balance(client, 'BTC'), usdt_balance
    except BinanceAPIException as e:
        logging.error(f"Error creating BUY order: {e}")
    return None, await check_balance(client, 'BTC'), usdt_balance

async def close_all_positions(client, symbol):
    try:
        open_orders = await client.futures_get_open_orders(symbol=symbol)
        for order in open_orders:
            await client.futures_cancel_order(symbol=symbol, orderId=order['orderId'])
            logging.info(f"Canceled order: {order['orderId']}")

        btc_balance = await check_balance(client, 'BTC')
        usdt_balance = await check_balance(client, 'USDT')

        if btc_balance > 0:
            order_quantity = adjust_quantity(btc_balance, 1)
            await client.futures_create_order(
                symbol=symbol, side="SELL", type="MARKET", quantity=order_quantity
            )
            logging.info(f"Sold {order_quantity} BTC to close position.")

        if current_position[symbol] == -1:
            order_quantity = adjust_quantity(abs(current_position[symbol]), 1)
            await client.futures_create_order(
                symbol=symbol, side="BUY", type="MARKET", quantity=order_quantity
            )
            logging.info(f"Bought {order_quantity} BTC to close short position.")

        await changepos(symbol, 'neutral')
        logging.info("All positions closed and set to neutral.")
    except BinanceAPIException as e:
        logging.error(f"Error closing positions: {e}")

async def check_current_position(client, symbol):
    try:
        positions = await client.futures_position_information()
        for position in positions:
            if position['symbol'] == symbol:
                pos_amt = float(position['positionAmt'])
                if pos_amt > 0:
                    await changepos(symbol, 'long')
                elif pos_amt < 0:
                    await changepos(symbol, 'short')
                else:
                    await changepos(symbol, 'neutral')
                logging.info(f"Position updated to {current_position[symbol]} after reconnection.")
    except BinanceAPIException as e:
        logging.error(f"Error checking current position: {e}")

async def trade_logic(client, data):
    global pending_order
    try:
        lastrow = data.iloc[-1]
        symbol = 'BTCUSDT'
        current_time = lastrow.name
        btc_price = lastrow['close']

        long_condition = (lastrow['a'] == True) and (lastrow['c'] == False)
        short_condition = (lastrow['c'] == True) and (lastrow['a'] == False)
        close_long_condition = (lastrow['b'] == True)
        close_short_condition = (lastrow['d'] == True)

        btc_balance = await check_balance(client, 'BTC')
        usdt_balance = await check_balance(client, 'USDT')
        logging.info(f"Current BTC balance: {btc_balance}")
        logging.info(f"Current USDT balance: {usdt_balance}")
        logging.info(f"Current position: {current_position[symbol]}")

        if pending_order:
            order_filled = await check_order_status(client, pending_order['orderId'], symbol)
            if order_filled:
                logging.info(f"Order {pending_order['orderId']} filled.")
                if pending_order is not None:
                    await asyncio.sleep(1)
                    btc_balance = await check_balance(client, 'BTC')
                    usdt_balance = await check_balance(client, 'USDT')
                    logging.info(f"Updated BTC balance: {btc_balance}")
                    logging.info(f"Updated USDT balance: {usdt_balance}")
                    await record_trade(
                        trade_id=str(uuid.uuid4()), ticker=symbol, date=current_time, trade_type='long' if current_position[symbol] == 1 else 'short',
                        signal_price=lastrow['close'], quantity=pending_order['origQty'],
                        opened_price=pending_order['price'], closed_price=None, vol=lastrow['volume'],
                        returns=None, entry_time=current_time, closing_time=None,
                        btc_price=btc_price, btc_balance=btc_balance, usdt_balance=usdt_balance
                    )
                pending_order = None
                if current_position[symbol] == 1 and close_long_condition:
                    await changepos(symbol, 'neutral')
                    logging.info(f"Position updated to NEUTRAL after closing LONG.")
                elif current_position[symbol] == -1 and close_short_condition:
                    await changepos(symbol, 'neutral')
                    logging.info(f"Position updated to NEUTRAL after closing SHORT.")

        if pending_order is None:
            if current_position[symbol] == 0:
                if long_condition:
                    pending_order, btc_balance, usdt_balance = await handle_long_order(client, symbol, lastrow, usdt_balance, btc_price, current_time)
                elif short_condition:
                    pending_order, btc_balance, usdt_balance = await handle_short_order(client, symbol, lastrow, btc_balance, btc_price, current_time)
            elif current_position[symbol] == 1:
                if close_long_condition:
                    pending_order, btc_balance, usdt_balance = await close_long_position(client, symbol, lastrow, btc_balance, btc_price, current_time)
                elif short_condition:
                    pending_order, btc_balance, usdt_balance = await close_long_position(client, symbol, lastrow, btc_balance, btc_price, current_time)
                    if pending_order:
                        await changepos(symbol, 'neutral')
            elif current_position[symbol] == -1:
                if close_short_condition:
                    pending_order, btc_balance, usdt_balance = await close_short_position(client, symbol, lastrow, usdt_balance, btc_price, current_time)
                elif long_condition:
                    pending_order, btc_balance, usdt_balance = await close_short_position(client, symbol, lastrow, usdt_balance, btc_price, current_time)
                    if pending_order:
                        await changepos(symbol, 'neutral')
    except Exception as e:
        logging.error(f"Error in trade logic: {e}")

async def main():
    client = None
    while True:
        try:
            client = await AsyncClient.create(API_KEY, API_SECRET, testnet=True)
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            await fetch_lot_size_and_min_notional(client, 'BTCUSDT')
            if not await ensure_initial_balance(client, 'USDT', 1000):
                logging.error("Insufficient initial balance. Exiting.")
                return

            async with websockets.connect('wss://fstream.binance.com/ws/btcusdt@kline_3m', ssl=ssl_context) as websocket:
                await check_current_position(client, 'BTCUSDT')  # Check and update position after reconnection
                while True:
                    try:
                        response = await websocket.recv()
                        response = json.loads(response)
                        kline = response['k']

                        kline_data.append({
                            'timestamp': pd.to_datetime(kline['t'], unit='ms'),
                            'open': float(kline['o']),
                            'high': float(kline['h']),
                            'low': float(kline['l']),
                            'close': float(kline['c']),
                            'volume': float(kline['v'])
                        })
                        if len(kline_data) > 20:
                            df = pd.DataFrame(kline_data)
                            df['RSI'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
                            bb = ta.volatility.BollingerBands(df['close'], window=20, window_dev=1)
                            df['upper_bb'] = bb.bollinger_hband()
                            df['lower_bb'] = bb.bollinger_lband()

                            df['shifted_Close'] = df['close'].shift(1)

                            df['a'] = (df['RSI'] < 30) & (df['shifted_Close'] < df['lower_bb'])
                            df['b'] = (df['RSI'] > 70) & (df['shifted_Close'] > df['upper_bb'])
                            df['c'] = (df['RSI'] > 70) & (df['shifted_Close'] > df['upper_bb'])
                            df['d'] = (df['RSI'] < 30) & (df['shifted_Close'] < df['lower_bb'])

                            await trade_logic(client, df)
                    except websockets.ConnectionClosedError as e:
                        logging.error(f"WebSocket connection closed: {e}")
                        await close_all_positions(client, 'BTCUSDT')
                        await client.close_connection()
                        await asyncio.sleep(10)
                        break
                    except Exception as e:
                        logging.error(f"Error in WebSocket connection or processing: {e}")
                        if client:
                            await close_all_positions(client, 'BTCUSDT')
                            await client.close_connection()
                        await asyncio.sleep(10)
                        break
        except Exception as e:
            logging.error(f"Error in initial setup or during the reconnect loop: {e}")
        finally:
            if client:
                await client.close_connection()
                client = None
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
