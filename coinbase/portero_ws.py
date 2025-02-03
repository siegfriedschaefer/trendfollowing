import asyncio
import websockets
import json
import time
import hmac
import hashlib
import os
import sys
import signal

import jwt
import hashlib
import os
import threading
from datetime import datetime, UTC
from dotenv import load_dotenv

WS_URL_MARKET_DATA='wss://advanced-trade-ws.coinbase.com'
WS_URL_USER_ORDER_DATA='wss://advanced-trade-ws-user.coinbase.com'

ALGORITHM = "ES256"

CHANNEL_NAMES = {
    "level2": "level2",
    "user": "user",
    "tickers": "ticker",
    "ticker_batch": "ticker_batch",
    "status": "status",
    "market_trades": "market_trades",
    "candles": "candles",
}

def sign_with_jwt(private_key, api_key, message):
    payload = {
        "iss": "coinbase-cloud",
        "nbf": int(time.time()),
        "exp": int(time.time()) + 120,
        "sub": api_key,
    }
    headers = {
        "kid": api_key,
        "nonce": hashlib.sha256(os.urandom(16)).hexdigest()
    }

    token = jwt.encode(payload, private_key, algorithm=ALGORITHM, headers=headers)
    message['jwt'] = token
    return message


def signal_handler(sig, frame):
    print("You pressed Ctrl+C! Exiting...")
    sys.exit(0)

async def subscibe_to_candles(private_key, api_key, ws, products):
    message = {
        "type": "subscribe",
        "product_ids": products,
        "channel": "candles"
    }
    signed_message = sign_with_jwt(private_key=private_key, api_key=api_key, message=message)
    await ws.send(json.dumps(signed_message))


async def subscribe_to_products(private_key, api_key, ws, products, channel_name):
    message = {
        "type": "subscribe",
        "channel": channel_name,
        "product_ids": products
    }
    signed_message = sign_with_jwt(private_key=private_key, api_key=api_key, message=message)
    await ws.send(json.dumps(signed_message))

async def unsubscribe_to_products(websocket, products, channel_name):
    message = {
        "type": "unsubscribe",
        "channel": channel_name,
        "product_ids": products
    }
    signed_message = sign_with_jwt(message, channel_name, products)

    await websocket.send(json.dumps(signed_message))

# Function to handle the market client
async def start_market(private_key, api_key):
    products = ["OP-USD","ETH-USD"]

    state = {
        "subscribed": False
    }

    async with websockets.connect(WS_URL_MARKET_DATA, max_size=None) as websocket:
        while True:

            if not state["subscribed"]:
                await subscibe_to_candles(private_key, api_key, websocket, products)
                # await subscribe_to_products(private_key, api_key, websocket, products, CHANNEL_NAMES["level2"])
                state["subscribed"] = True

            message = await websocket.recv()
            data = json.loads(message)

            events = data.get("events", [])
            for event in events:
                if "type" in event and event["type"] == "update":
                    print(f"Update: {event['candles']}")

#                with open("Output1.txt", "a") as f:
#                    f.write(json.dumps(data) + "\n")

def main():

    load_dotenv()
    signal.signal(signal.SIGINT, signal_handler)

    api_key = os.environ['COINBASE_WS_001_API_KEY']
    private_key = os.environ['COINBASE_WS_001_PRIVATE_KEY']

    # this is critical to handle different shell environments and how they handle newlines.
    # the private key is a multi-line string, and the newlines are escaped with '\n'.
    # so we need to replace them with actual newlines.
    private_key = private_key.replace("\\n", "\n")

    if not api_key or not private_key:
        raise ValueError("Missing mandatory environment variable(s)")
    
    asyncio.run(start_market(private_key=private_key, api_key=api_key))

    sent_unsub = False
    start_time = datetime.now(UTC)

    try:
        while True:
            if (datetime.now(UTC) - start_time).total_seconds() > 5 and not sent_unsub:
                print(f"Unsubscribing from channel")
                # Unsubscribe after 5 seconds
#                ws = websocket.create_connection(WS_URL_MARKET_DATA)
#                unsubscribe_to_products(ws, ["BTC-USD"], CHANNEL_NAMES["level2"])
#                ws.close()
                sent_unsub = True
            time.sleep(1)
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    main()
