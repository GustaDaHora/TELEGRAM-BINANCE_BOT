import requests

bot_token = 'bot_token'
url = f'https://api.telegram.org/bot{bot_token}/getMe'

response = requests.get(url)

if response.status_code == 200:
    print("sucess", response.json())
else:
    print('Error:')
