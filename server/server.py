from location import Location
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from connection_manager import ConnectionManager

watches: dict[WebSocket, Location] = {}
app = FastAPI()
manager = ConnectionManager()


@app.websocket("/logview")
async def websocket_endpoint_logview(websocket: WebSocket):
    await manager.connect_logview(websocket)
    await manager.send_personal_message("Connection Established.", websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    set_watches(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            await handle_message(data, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def handle_message(data: str, sender: WebSocket):
    if "PING" in data:
        await manager.log_broadcast(f"PING sent from {sender.client}")
        await manager.send_personal_message("BUZZ", get_other_client(sender))

    if "LOCATION_UPDATE" in data:
        cords = data.split(" ")[1:]
        watches[sender].latitude = float(cords[0])
        watches[sender].longitude = float(cords[1])

        await manager.log_broadcast(f"{data} sent from {sender.client}")

        await manager.send_personal_message(
            f"LOCATION_UPDATE {watches[sender].latitude} {watches[sender].longitude}",
            get_other_client(sender),
        )


def set_watches(websocket: WebSocket):
    MAX_WATCHES = 2
    if len(watches) == MAX_WATCHES:
        for client in watches.keys():
            for ws in manager.active_connections:
                if client is not ws:
                    watches[client] = Location(latitude=0, longitude=0)
    else:
        watches[websocket] = Location(latitude=0, longitude=0)


def get_other_client(sender: WebSocket):
    for client in manager.active_connections:
        if sender is not client:
            return client
