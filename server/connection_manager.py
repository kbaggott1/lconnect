from fastapi import WebSocket

MAX_CONNECTIONS = 2


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.log_viewer_connections: list[WebSocket] = []

    async def connect_logview(self, websocket: WebSocket):
        await websocket.accept()
        self.log_viewer_connections.append(websocket)

    async def connect(self, websocket: WebSocket):
        if len(self.active_connections) < MAX_CONNECTIONS:
            await websocket.accept()
            self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.log_viewer_connections:
            self.log_viewer_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(f"BROADCAST: {message}")

    async def log_broadcast(self, message: str):
        for connection in self.log_viewer_connections:
            try:
                await connection.send_text(f"LOG: {message}")
            except Exception as e:
                print(f"Error sending message to log viewer: {e}")
                self.log_viewer_connections.remove(connection)
