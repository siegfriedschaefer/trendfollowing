import sys
import signal
import os
import argparse
import time

from datetime import datetime, timezone
from dotenv import load_dotenv

from pybit.unified_trading import HTTP

def signal_handler(sig, frame):
    print("You pressed Ctrl+C! Exiting...")
    sys.exit(0)

def main():

    trading_pair = "ARBUSDC"
    base_price = 0.0
    base_size = "0.0"
    run_simulated = 'True'
    side = "None"

    signal.signal(signal.SIGINT, signal_handler)

    load_dotenv()

    parser = argparse.ArgumentParser(description="Bybit Order example")
    parser.add_argument("--tp", help="Trading pair to monitor")
    parser.add_argument("--bp", help="base price")
    parser.add_argument("--bs", help="base size")
    parser.add_argument("--sd", help="Sell/Buy")
    parser.add_argument("--rs", help="run simulated, without real trades")
 
    args = parser.parse_args()
    
    if args.tp:
        trading_pair = args.tp

    if args.bp:
        base_price = float(args.bp)

    if base_price == 0.0:
        exit("Base price not set")

    if args.bs:
        base_size = (args.bs)

    if base_size == "0.0":
        exit("Base size not set") 

    if args.rs:
        run_simulated = args.rs

    if args.sd == "Sell" or args.sd == "Buy":
        side = args.sd
    else:
        exit("Side not set")


    api_key = os.environ['BYPIT_API_KEY']
    api_secret = os.environ['BYPIT_API_SECRET']

    session = HTTP(
        testnet=False,
        api_key=api_key,
        api_secret=api_secret,
    )

    if run_simulated == 'False':

        # places a market order to sell base asset

        now = datetime.now(timezone.utc)
        order_index = int(now.day * 24 * 60 * 60 + now.second)

        try:
            order = session.place_order(
                category="spot",
                symbol=trading_pair,
                side=side,
                orderType="Market",
                qty=base_size,
                timeInForce="GTC",
                orderLinkId=str(order_index),
                isLeverage=0,
                orderFilter="Order",
            )
        except Exception as e:
            print(f"Error: ")
            print(f"{e}")
            sys.exit(0)
        
        print(">>>")
        print(order)

if __name__ == "__main__":

    main()

