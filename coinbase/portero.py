
'''
python portero.py --tp OP-USDC --iv 30 --bp 1.697 --tpt 1.5 --bs 550 --rs 'False'
'''

import time
import signal
import sys
import os
import argparse

from datetime import datetime, timezone
from dotenv import load_dotenv

from crypto_asset import CryptoAsset
from crypto_asset_history import crypto_asset_save_to_csv

from coinbase.rest import RESTClient
from json import dumps

def signal_handler(sig, frame):
    print("You pressed Ctrl+C! Exiting...")
    sys.exit(0)

def main():
    print("portero v0.1.0")
    load_dotenv()
    signal.signal(signal.SIGINT, signal_handler)

    api_key = os.environ['COINBASE_API_KEY']
    api_secret = os.environ['COINBASE_API_SECRET']

    trading_pair = "ETH-USDC"
    intervall = 10
    base_price = 0.0
    base_size = "0.0"
    run_simulated = 'True'
    hour_trigger_counter = 0

    stop_loss_percent = 1.25
    take_profit_percent = 1.25

    max_trigger_hit = False

    parser = argparse.ArgumentParser(description="Your program description")
    parser.add_argument("--tp", help="Trading pair to monitor")
    parser.add_argument("--iv", help="intervall in seconds")
    parser.add_argument("--bp", help="base price")
    parser.add_argument("--bs", help="base size")
    parser.add_argument("--tpt", help="take profit percent")
    parser.add_argument("--slp", help="stop loss percent")
    parser.add_argument("--rs", help="run simulated, without real trades")

    args = parser.parse_args()
    
    if args.tp:
        trading_pair = args.tp

    if args.iv:
        intervall = int(args.iv)

    if args.bp:
        base_price = float(args.bp)

    if base_price == 0.0:
        exit("Base price not set")

    if args.tpt:
        take_profit_percent = float(args.tpt)

    if args.bs:
        base_size = (args.bs)

    if args.slp:
        stop_loss_percent = float(args.slp)

    if base_size == "0.0":
        exit("Base size not set") 

    if args.rs:
        run_simulated = args.rs

    stop_loss = base_price - (base_price * stop_loss_percent / 100)
    take_profit = base_price + (base_price * take_profit_percent / 100)
    max_trigger = take_profit

    crypto_asset = CryptoAsset( trading_pair, base_price, base_price, stop_loss, take_profit, "none")

    client = RESTClient(api_key=api_key, api_secret=api_secret)
    while True:

        hour_trigger_counter += intervall

        asset = client.get_product(trading_pair)

        asset_price = float(asset["price"])
        diff = asset_price - base_price

        crypto_asset.current_price = asset_price
        crypto_asset.base_price = base_price
        crypto_asset.stop_loss_price = stop_loss
        crypto_asset.take_profit_price = take_profit
        crypto_asset.symbol = trading_pair
        crypto_asset.timestamp = time.time()
                        
        current_time = datetime.now().strftime("%D:%H:%M:%S")
        print(f"{current_time} - {trading_pair} c/b/l/p/d: {asset_price:.4f}/{base_price:.4f}/{stop_loss:.4f}/{take_profit:.4f}/{diff:.4f}")
        crypto_asset_save_to_csv(crypto_asset)


        '''
        Every hour, if the current price is above the base price, we adjust
        the stop loss to the current price - 0.5% and the take profit to the
        current price + 1.25%. This is to protect the profit and to avoid
        the stop loss being hit on a sudden price drop.
        '''
        if (hour_trigger_counter >= 300):
            hour_trigger_counter = 0
            if asset_price > base_price:
                base_price = asset_price
                stop_loss = base_price - (base_price * stop_loss_percent / 100)
                take_profit = base_price + (base_price * take_profit_percent / 100)
                max_trigger = take_profit
                max_trigger_hit = False               

        if asset_price <= stop_loss:
            print(f"Stop loss hit - selling for market price: {asset_price:.4f}")
            crypto_asset.action = "sell"
            crypto_asset_save_to_csv(crypto_asset)

            now = datetime.now(timezone.utc)
            order_index = int(now.day * 24 * 60 * 60 + now.second)

            if run_simulated == 'False':    
                # places a market order to sell base asset
                order = client.market_order_sell(
                    client_order_id=str(order_index),
                    product_id=trading_pair,
                    base_size=base_size
                )

                if 'success_response' in order:
                    order_id = order['success_response']['order_id']
                    fills = client.get_fills(order_id=order_id)
                    print(dumps(fills, indent=2))
                elif 'error_response' in order:
                    error_response = order['error_response']
                    print(error_response)

                break

        if asset_price >= max_trigger:
            max_trigger_hit = True
            max_trigger = asset_price
            stop_loss = asset_price - (asset_price * stop_loss_percent / 100)
            take_profit = asset_price - (asset_price * 0.5 / 100)
            print(f"New stop loss: {stop_loss}")

        if max_trigger_hit and asset_price < take_profit:
            print(f"Take profit hit - selling for market price {asset_price:.4f}")
            crypto_asset.action = "sell"
            crypto_asset_save_to_csv(crypto_asset)

            now = datetime.now(timezone.utc)
            order_index = int(now.day * 24 * 60 * 60 + now.second)


            if run_simulated == 'False':
                # places a market order to sell base asset
                order = client.market_order_sell(
                    client_order_id=str(order_index),
                    product_id=trading_pair,
                    base_size=base_size
                )

                if 'success_response' in order:
                    order_id = order['success_response']['order_id']
                    fills = client.get_fills(order_id=order_id)
                    print(dumps(fills, indent=2))
                elif 'error_response' in order:
                    error_response = order['error_response']
                    print(error_response)

                break


            break

        time.sleep(intervall)

if __name__ == "__main__":

    main()


