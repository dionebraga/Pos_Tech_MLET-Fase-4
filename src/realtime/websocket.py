import asyncio
import websockets

async def connect():

    uri = "wss://stream.binance.com:9443/ws/btcusdt@trade"

    async with websockets.connect(uri) as websocket:

        while True:

            data = await websocket.recv()

            print(data)

asyncio.run(connect())