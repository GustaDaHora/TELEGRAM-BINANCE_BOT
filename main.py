import requests
import time
import re
from binance.client import Client
from binance.enums import *

# Initialize the Binance client
binance_api_key = 'binance_api_key'
binance_api_secret = 'binance_api_secret'
client = Client(api_key=binance_api_key, api_secret=binance_api_secret, testnet=True)

# Telegram Bot API endpoint
telegram_bot_token = 'telegram_bot_token'
telegram_url = f'https://api.telegram.org/bot{telegram_bot_token}/getUpdates'
printed_messages = set()

def parse_message(message):
    details = {}

    try:
        details['pair'] = re.search(r"Pair: \$(.*) \(", message).group(1).replace("/", "")
    except AttributeError:
        print("Error parsing pair.")
        return None

    details['direction'] = 'BUY' if '⬆️LONG' in message else 'SELL'

    try:
        details['position_size'] = [float(x) for x in re.search(r"Position Size: (\d+) - (\d+)%", message).groups()]
    except AttributeError:
        print("Error parsing position size.")
        return None

    try:
        details['leverage'] = [int(x) for x in re.search(r"Leverage : (\d+) -(\d+)X", message).groups()]
    except AttributeError:
        print("Error parsing leverage.")
        return None

    try:
        entry = re.search(r"ENTRY : ([\d.]+) - ([\d.]+)", message).groups()
        details['entry_min'] = float(entry[0])
        details['entry_max'] = float(entry[1])
    except AttributeError:
        print("Error parsing entry.")
        return None

    try:
        details['stop_loss'] = float(re.search(r"STOP LOSS: (\d+)", message).group(1))
    except AttributeError:
        print("Error parsing stop loss.")
        return None

    details['targets'] = [float(x) for x in re.findall(r"🔘Target \d+ - ([\d.]+)", message)]

    if not details['targets']:
        print("Error parsing targets.")
        return None

    return details

def set_leverage(symbol, leverage):
    try:
        response = client.futures_change_leverage(symbol=symbol, leverage=leverage)
        return response
    except Exception as e:
        print(f"Error setting leverage: {e}")
        return str(e)

def place_limit_order(symbol, side, quantity, price):
    try:
        order = client.create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=quantity,
            price=str(price)
        )
        return order
    except Exception as e:
        print(f"Error placing limit order: {e}")
        return str(e)

def place_stop_loss_order(symbol, side, quantity, stop_price):
    try:
        order = client.create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_STOP_LOSS,
            quantity=quantity,
            stopPrice=str(stop_price)
        )
        return order
    except Exception as e:
        print(f"Error placing stop loss order: {e}")
        return str(e)

def place_take_profit_order(symbol, side, quantity, target_price):
    try:
        order = client.create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_TAKE_PROFIT,
            quantity=quantity,
            stopPrice=str(target_price)
        )
        return order
    except Exception as e:
        print(f"Error placing take profit order: {e}")
        return str(e)

def execute_trading_strategy(details):
    symbol = details['pair'] + 'USDT'
    side = SIDE_BUY if details['direction'] == 'BUY' else SIDE_SELL
    position_size = details['position_size'][0] / 100  # Using the minimum size
    leverage = details['leverage'][0]  # Using the minimum leverage

    leverage_response = set_leverage(symbol, leverage)
    print("Leverage Response:", leverage_response)

    # Calculate entry quantity (assuming the use of minimum entry price for quantity calculation)
    entry_price = (details['entry_min'] + details['entry_max']) / 2
    quantity = position_size  # Adjust based on your balance and entry price

    entry_order_response = place_limit_order(symbol, side, quantity, entry_price)
    print("Entry Order Response:", entry_order_response)

    time.sleep(10)

    stop_loss_order_response = place_stop_loss_order(symbol, SIDE_SELL if side == SIDE_BUY else SIDE_BUY, quantity, details['stop_loss'])
    print("Stop Loss Order Response:", stop_loss_order_response)

    for target in details['targets']:
        take_profit_order_response = place_take_profit_order(symbol, SIDE_SELL if side == SIDE_BUY else SIDE_BUY, quantity / len(details['targets']), target)
        print("Take Profit Order Response:", take_profit_order_response)

def process_telegram_messages():
    try:
        while True:
            response = requests.get(telegram_url)

            if response.status_code == 200:
                data = response.json()

                if 'retry_after' in data:
                    print(f'Rate limiting detected. Waiting {data["retry_after"]} seconds before retrying.')
                    time.sleep(data['retry_after'])
                    continue

                updates = data.get('result', [])

                for update in updates:
                    if 'message' in update:
                        message_id = update['message'].get('message_id')

                        if message_id not in printed_messages:
                            printed_messages.add(message_id)
                            text = update['message'].get('text', '')
                            print(text)
                            order_info = parse_message(text)
                            print(order_info)
                            if order_info:
                                execute_trading_strategy(order_info)

            else:
                print('Error:', response.status_code)

            time.sleep(5)
    except KeyboardInterrupt:
        print('Execution stopped by user.')

process_telegram_messages()