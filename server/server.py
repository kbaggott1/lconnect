from location import Location
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from connection_manager import ConnectionManager

NUMBER_OF_WATCHES = 2

watches: dict[WebSocket, Location] = {}
app = FastAPI()
manager = ConnectionManager()


@app.websocket("/logview")
async def websocket_endpoint_logview(websocket: WebSocket):
    await manager.connect_logview(websocket)
    await manager.send_personal_message("Connection Established.", websocket)

    # TODO Ensure number of connections gets updated when device connnects and disconnects from server
    await manager.send_personal_message(
        f"No. Connections: {len(manager.active_connections)}", websocket
    )

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
    # TODO Messages sent back to other device like UPDATE_LOCATION and LOCATION need better names
    if "PING" in data:
        await manager.log_broadcast(f"PING sent from {sender.client}")

        if len(manager.active_connections) == NUMBER_OF_WATCHES:
            await manager.send_personal_message("BUZZ", get_other_client(sender))

    if "UPDATE_LOCATION" in data:
        cords = data.split(" ")[1:]
        if len(cords) != 2:
            return
        try:
            watches[sender].latitude = float(cords[0])
            watches[sender].longitude = float(cords[1])

            await manager.log_broadcast(f"{data} sent from {sender.client}")

            if len(manager.active_connections) == NUMBER_OF_WATCHES:
                await manager.send_personal_message(
                    f"UPDATE_LOCATION {watches[sender].latitude} {watches[sender].longitude}",
                    get_other_client(sender),
                )

        except ValueError as e:
            print(f"Could not update location: {e}")

    if "GET_LOCATION" in data:
        if len(manager.active_connections) == NUMBER_OF_WATCHES:
            await manager.send_personal_message(
                f"LOCATION {watches[get_other_client(sender)].latitude} {watches[get_other_client(sender)].longitude}",
                sender,
            )


def set_watches(websocket: WebSocket):
    MAX_WATCHES = 2
    old_client = get_other_client(websocket)

    if len(watches) == MAX_WATCHES:
        client_to_delete: WebSocket

        for client in watches.keys():
            if client is not old_client:
                client_to_delete = client
                break
        del watches[client_to_delete]

    watches[websocket] = Location(latitude=0, longitude=0)


def get_other_client(sender: WebSocket):
    for client in manager.active_connections:
        if sender is not client:
            return client
