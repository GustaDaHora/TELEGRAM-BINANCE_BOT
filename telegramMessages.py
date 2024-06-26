import requests
import time

bot_token = '6602472961:AAGb-GL71Xr3DUPaCxzbQbrvH3GvvVsTQEg'
url = f'https://api.telegram.org/bot{bot_token}/getUpdates'

printed_messages = set()

def get_updates():
    try:
        while True:
            response = requests.get(url)
            if response.status_code == 200:
                # Parse the JSON response
                data = response.json()
                # Check if rate limiting occurred
                if 'retry_after' in data:

                    print(f'Rate limiting detected. Waiting {data["retry_after"]} seconds before retrying.')
                    time.sleep(data['retry_after'])
                    continue  
                updates = data.get('result', [])

                for update in updates:
                    # Check if the update contains a message
                    if 'message' in update:
                        message_id = update['message'].get('message_id')
                        # Check if this message has already been printed
                        if message_id not in printed_messages:
                            # Add the message ID to the set of printed messages
                            printed_messages.add(message_id)
                            text = update['message'].get('text', '')
                            print(text)
            else:
                print('Error:', response.status_code)

            # Add a delay before checking for updates again (e.g., every 5 seconds)
            time.sleep(10)
    except KeyboardInterrupt:
        print('Execution stopped by user.')

get_updates()
