"""WebSocket connection manager for real-time dashboard broadcasting."""

import logging
from typing import Dict, List
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections grouped by motor_id."""

    def __init__(self):
        # Map of motor_id -> list of active WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, motor_id: str, websocket: WebSocket):
        """Accepts and stores an active WebSocket connection."""
        await websocket.accept()
        if motor_id not in self.active_connections:
            self.active_connections[motor_id] = []
        self.active_connections[motor_id].append(websocket)
        logger.info(f"WebSocket connected for motor {motor_id}. Active subscribers: {len(self.active_connections[motor_id])}")

    def disconnect(self, motor_id: str, websocket: WebSocket):
        """Removes a closed or disconnected WebSocket connection."""
        if motor_id in self.active_connections:
            if websocket in self.active_connections[motor_id]:
                self.active_connections[motor_id].remove(websocket)
                logger.info(f"WebSocket disconnected for motor {motor_id}. Remaining: {len(self.active_connections[motor_id])}")
            if not self.active_connections[motor_id]:
                del self.active_connections[motor_id]

    async def broadcast(self, motor_id: str, message: dict):
        """Broadcasts a JSON message payload to all connected clients for a motor."""
        if motor_id not in self.active_connections:
            return

        dead_connections = []
        for connection in self.active_connections[motor_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Error broadcasting to WebSocket subscriber on {motor_id}: {e}")
                dead_connections.append(connection)

        # Clean up stale/failed connections
        for dead in dead_connections:
            self.disconnect(motor_id, dead)


ws_manager = ConnectionManager()
