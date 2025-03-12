import asyncio
from websockets.asyncio.client import connect
from datetime import datetime
from websockets.exceptions import ConnectionClosed

HOST_ADDRESS = "ws://localhost:8000"


async def handler(websocket):
    consumer_task = asyncio.create_task(consumer_handler(websocket))
    producer_task = asyncio.create_task(producer_handler(websocket))
    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()


async def consumer_handler(websocket):
    async for message in websocket:
        await consume(message)


async def producer_handler(websocket):
    while True:
        try:
            message = await produce()
            await websocket.send(message)
        except ConnectionClosed:
            break


async def produce():
    await asyncio.sleep(1)
    return await asyncio.to_thread(input, "Send to server: ")


async def consume(message: str):
    print(f"Server: {message}")


async def main():
    print(f"Connecting to {HOST_ADDRESS}...")
    async with connect(HOST_ADDRESS) as websocket:
        await handler(websocket)


if __name__ == "__main__":
    asyncio.run(main())
