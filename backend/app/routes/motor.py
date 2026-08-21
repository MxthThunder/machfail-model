"""Motor data ingestion, query, and control API endpoints."""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    MotorSensorDataIn,
    MotorDataIngestResponse,
    MotorLatestDataResponse,
    MotorStatusResponse,
    MotorHistoryResponse,
    MotorControlRequest,
    MotorControlResponse,
    PendingCommandResponse,
    CommandAckRequest,
    CommandAckResponse,
    MotorConditionAnalysisRequest,
    MotorConditionAnalysisResponse,
)
from app.services.motor_service import motor_service
from app.services.condition_service import condition_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/motor", tags=["Motor Operations"])


@router.post(
    "/data",
    response_model=MotorDataIngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest live ESP32 motor telemetry"
)
async def ingest_motor_data(
    payload: MotorSensorDataIn,
    db: Session = Depends(get_db)
):
    """
    Ingests live telemetry packet from ESP32.
    - Stores sensor reading in SQLite
    - Updates in-memory latest status and runtime tracker
    - Broadcasts packet via WebSocket to connected dashboards
    """
    try:
        timestamp_str = await motor_service.ingest_telemetry(payload, db)
        return MotorDataIngestResponse(
            success=True,
            message="Motor data received",
            motor_id=payload.motor_id,
            timestamp=timestamp_str
        )
    except Exception as e:
        logger.error(f"Error ingesting motor telemetry: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist motor telemetry"
        )


@router.get(
    "/latest",
    response_model=MotorLatestDataResponse,
    summary="Get latest received ESP32 sensor data"
)
def get_latest_motor_data(
    motor_id: str = Query("M001", description="Motor identifier"),
    db: Session = Depends(get_db)
):
    """Retrieves the most recent real sensor reading received from the ESP32."""
    latest = motor_service.get_latest_data(motor_id, db)
    if not latest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No telemetry records found for motor ID: {motor_id}"
        )
    return latest


@router.get(
    "/status",
    response_model=MotorStatusResponse,
    summary="Get motor online status & runtime"
)
def get_motor_status(
    motor_id: str = Query("M001", description="Motor identifier"),
    db: Session = Depends(get_db)
):
    """
    Evaluates motor online/offline state dynamically:
    - If last reading was received within timeout threshold (e.g. 10s), online = True.
    - If elapsed time exceeds threshold, online = False.
    - Also returns total accumulated operational runtime in seconds.
    """
    return motor_service.get_motor_status(motor_id, db)


@router.get(
    "/history/{motor_id}",
    response_model=MotorHistoryResponse,
    summary="Get historical motor sensor readings"
)
def get_motor_history(
    motor_id: str,
    limit: int = Query(50, ge=1, le=1000, description="Max number of historical records to return"),
    db: Session = Depends(get_db)
):
    """Retrieves historical sensor time-series records from SQLite."""
    return motor_service.get_history(motor_id, limit, db)


@router.post(
    "/control",
    response_model=MotorControlResponse,
    summary="Queue motor control command"
)
def control_motor(
    payload: MotorControlRequest,
    db: Session = Depends(get_db)
):
    """
    Queues a motor control command (e.g. ON / OFF) for ESP32 retrieval.
    Does NOT falsely state that physical motor changed state until ESP32 acknowledges.
    """
    cmd = payload.command.upper()
    if cmd not in ["ON", "OFF"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Command must be either 'ON' or 'OFF'"
        )

    return motor_service.queue_command(payload.motor_id, cmd, db)


@router.get(
    "/command/{motor_id}",
    response_model=PendingCommandResponse,
    summary="Poll pending motor control command for ESP32"
)
def poll_pending_command(
    motor_id: str,
    db: Session = Depends(get_db)
):
    """Endpoint for ESP32 to poll pending control commands."""
    return motor_service.get_pending_command(motor_id, db)


@router.post(
    "/command/ack",
    response_model=CommandAckResponse,
    summary="Acknowledge executed command from ESP32"
)
def acknowledge_command(
    payload: CommandAckRequest,
    db: Session = Depends(get_db)
):
    """Endpoint for ESP32 to confirm physical command execution."""
    return motor_service.acknowledge_command(
        payload.motor_id,
        payload.command_id,
        payload.status,
        db
    )


@router.post(
    "/analyze",
    response_model=MotorConditionAnalysisResponse,
    summary="Analyze motor condition from provided sensor parameters"
)
def analyze_motor_condition(
    payload: MotorConditionAnalysisRequest
):
    """
    Evaluates Temperature, RPM, Current, and Vibration parameters against
    standard thresholds, calculates condition score (0-8), failure risk (LOW/MEDIUM/HIGH),
    and generates clear explanatory messages.
    """
    return condition_service.evaluate_condition(
        motor_id=payload.motor_id,
        temperature=payload.temperature,
        rpm=payload.rpm,
        current=payload.current,
        vibration=payload.vibration
    )


@router.get(
    "/condition/{motor_id}",
    response_model=MotorConditionAnalysisResponse,
    summary="Get condition analysis for latest real ESP32 motor telemetry"
)
def get_motor_condition_analysis(
    motor_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves the most recent real ESP32 telemetry reading from database/cache
    and performs full rule-based condition & failure risk analysis.
    """
    latest = motor_service.get_latest_data(motor_id, db)
    if not latest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No telemetry records found for motor ID: {motor_id}"
        )

    return condition_service.evaluate_condition(
        motor_id=latest.motor_id,
        temperature=latest.temperature,
        rpm=latest.rpm if latest.rpm is not None else 0.0,
        current=latest.current,
        vibration=latest.vibration,
        timestamp=latest.received_at
    )
