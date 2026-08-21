"""WebSocket route for real-time dashboard live streaming."""

import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.connection_manager import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket Real-Time Stream"])


@router.websocket("/ws/motor/{motor_id}")
async def websocket_motor_endpoint(websocket: WebSocket, motor_id: str):
    """
    WebSocket endpoint for real-time dashboard streaming.
    Whenever live ESP32 telemetry arrives for motor_id, it is pushed immediately.
    """
    await ws_manager.connect(motor_id, websocket)
    try:
        while True:
            # Keep connection open and listen for client pings or control messages
            data = await websocket.receive_text()
            # Respond to simple heartbeat/ping
            if data.strip().lower() == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(motor_id, websocket)
        logger.info(f"WebSocket client disconnected for {motor_id}")
    except Exception as e:
        logger.warning(f"WebSocket exception on {motor_id}: {e}")
        ws_manager.disconnect(motor_id, websocket)
