from binance.client import Client

api_key = 'api_key'
api_secret = 'api_secret'

client = Client(api_key=api_key, api_secret=api_secret, testnet=True)
ticker = client.get_symbol_ticker(symbol='BTCUSDT')
print(ticker)
