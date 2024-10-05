
'''
Investment account information

We need to know the available balance and the hold balance for each account.
The available balance is the amount of money that is available to trade.
The hold balance is the amount of money that is currently in an open order.

'''

import sys
import signal
import os
from dotenv import load_dotenv



from coinbase.rest import RESTClient

def signal_handler(sig, frame):
    print("You pressed Ctrl+C! Exiting...")
    sys.exit(0)

def main():

    signal.signal(signal.SIGINT, signal_handler)

    load_dotenv()
    api_key = os.environ['COINBASE_API_KEY']
    api_secret = os.environ['COINBASE_API_SECRET']

    client = RESTClient(api_key=api_key, api_secret=api_secret)

    accounts = client.get_accounts()

    accounts = accounts['accounts']

    for a in accounts:
            av = a['available_balance']['value']
            hold = a['hold']['value']
            available_balance = float(av)
            hold_balance = float(hold)

            if available_balance > 0.0 or hold_balance > 0.0:
                print(f"{a['name']}: available balance: {av}, {available_balance:.4f} hold balance: {hold}, {hold_balance:.4f}")
            
if __name__ == '__main__':
    main()

