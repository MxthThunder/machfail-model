"""Motor business logic, telemetry processing, runtime tracking, and state management."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional, List, Any

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.config import settings
from app.models import MotorReading, MotorCommand, utc_now
from app.schemas import (
    MotorSensorDataIn,
    MotorLatestDataResponse,
    MotorStatusResponse,
    MotorHistoryRecord,
    MotorHistoryResponse,
    MotorControlResponse,
    PendingCommandResponse,
    CommandAckResponse,
)
from app.services.connection_manager import ws_manager
from app.services.condition_service import condition_service

logger = logging.getLogger(__name__)


class MotorService:
    """Service handling state tracking, runtime calculation, database operations, and commands."""

    def __init__(self):
        # In-memory latest states for fast O(1) access
        self.latest_readings: Dict[str, dict] = {}
        self.last_seen_times: Dict[str, datetime] = {}
        self.last_statuses: Dict[str, str] = {}
        self.accumulated_runtimes: Dict[str, float] = {}  # in seconds
        self.pending_commands: Dict[str, dict] = {}

    def _update_runtime(self, motor_id: str, current_status: str, now: datetime):
        """
        Calculates accumulated runtime based on real motor status changes and timestamps.
        Only accumulates time when status is 'ON' and updates are actively received.
        """
        if motor_id not in self.accumulated_runtimes:
            self.accumulated_runtimes[motor_id] = 0.0

        last_seen = self.last_seen_times.get(motor_id)
        last_status = self.last_statuses.get(motor_id, "OFF")

        if last_seen is not None and last_status.upper() == "ON":
            delta_seconds = (now - last_seen).total_seconds()
            # If the time delta is reasonable (e.g. less than 2x the timeout threshold), accumulate it
            if 0 < delta_seconds <= (settings.MOTOR_ONLINE_TIMEOUT_SECONDS * 2):
                self.accumulated_runtimes[motor_id] += delta_seconds

    async def ingest_telemetry(self, data: MotorSensorDataIn, db: Session) -> str:
        """
        Processes real incoming ESP32 sensor telemetry:
        1. Persists data to SQLite.
        2. Calculates motor runtime.
        3. Updates in-memory latest status and last_seen.
        4. Broadcasts update to connected WebSocket clients.
        """
        now = utc_now()
        timestamp_str = now.isoformat()

        # Update runtime calculation
        self._update_runtime(data.motor_id, data.status, now)
        self.last_seen_times[data.motor_id] = now
        self.last_statuses[data.motor_id] = data.status.upper()

        # 1. Store in SQLite Database
        db_reading = MotorReading(
            motor_id=data.motor_id,
            timestamp=now,
            status=data.status.upper(),
            temperature=data.temperature,
            humidity=data.humidity,
            ir=data.ir,
            ir_pulses=data.ir_pulses if data.ir_pulses is not None else 0,
            rpm=data.rpm if data.rpm is not None else 0.0,
            acs_adc=data.acs_adc,
            current=data.current,
            mpu_x=data.mpu_x,
            mpu_y=data.mpu_y,
            mpu_z=data.mpu_z,
            total_acceleration=data.total_acceleration,
            vibration=data.vibration,
            vibration_level=data.vibration_level.upper(),
            motor_pwm=data.motor_pwm if data.motor_pwm is not None else 0,
            voltage=data.voltage,
            esp32_ip=data.esp32_ip,
        )
        db.add(db_reading)
        db.commit()
        db.refresh(db_reading)

        # 2. Update in-memory latest reading cache
        latest_dict = {
            "motor_id": data.motor_id,
            "status": data.status.upper(),
            "temperature": data.temperature,
            "humidity": data.humidity,
            "ir": data.ir,
            "ir_pulses": data.ir_pulses if data.ir_pulses is not None else 0,
            "rpm": data.rpm if data.rpm is not None else 0.0,
            "acs_adc": data.acs_adc,
            "current": data.current,
            "mpu_x": data.mpu_x,
            "mpu_y": data.mpu_y,
            "mpu_z": data.mpu_z,
            "total_acceleration": data.total_acceleration,
            "vibration": data.vibration,
            "vibration_level": data.vibration_level.upper(),
            "motor_pwm": data.motor_pwm if data.motor_pwm is not None else 0,
            "voltage": data.voltage,
            "esp32_ip": data.esp32_ip,
            "received_at": timestamp_str,
        }
        self.latest_readings[data.motor_id] = latest_dict

        logger.info(
            f"ESP32 Telemetry stored for {data.motor_id}: "
            f"Status={data.status} Temp={data.temperature}°C RPM={data.rpm} Current={data.current}A Vib={data.vibration_level}"
        )

        # 3. Evaluate real-time condition analysis
        condition_eval = condition_service.evaluate_condition(
            motor_id=data.motor_id,
            temperature=data.temperature,
            rpm=data.rpm if data.rpm is not None else 0.0,
            current=data.current,
            vibration=data.vibration,
            timestamp=timestamp_str
        )

        # 4. Broadcast real-time update to WebSocket subscribers
        ws_payload = {
            "type": "telemetry",
            "data": latest_dict,
            "condition": condition_eval,
            "runtime_seconds": round(self.accumulated_runtimes.get(data.motor_id, 0.0), 2),
            "online": True
        }
        await ws_manager.broadcast(data.motor_id, ws_payload)

        return timestamp_str

    def get_latest_data(self, motor_id: str, db: Session) -> Optional[MotorLatestDataResponse]:
        """Returns the most recently received telemetry for a motor."""
        # Check cache first
        if motor_id in self.latest_readings:
            return MotorLatestDataResponse(**self.latest_readings[motor_id])

        # Fallback to Database query
        db_reading = (
            db.query(MotorReading)
            .filter(MotorReading.motor_id == motor_id)
            .order_by(desc(MotorReading.timestamp))
            .first()
        )
        if not db_reading:
            return None

        reading_dict = {
            "motor_id": db_reading.motor_id,
            "status": db_reading.status,
            "temperature": db_reading.temperature,
            "humidity": db_reading.humidity,
            "ir": db_reading.ir,
            "ir_pulses": db_reading.ir_pulses if db_reading.ir_pulses is not None else 0,
            "rpm": db_reading.rpm if db_reading.rpm is not None else 0.0,
            "acs_adc": db_reading.acs_adc,
            "current": db_reading.current,
            "mpu_x": db_reading.mpu_x,
            "mpu_y": db_reading.mpu_y,
            "mpu_z": db_reading.mpu_z,
            "total_acceleration": db_reading.total_acceleration,
            "vibration": db_reading.vibration,
            "vibration_level": db_reading.vibration_level,
            "motor_pwm": db_reading.motor_pwm if db_reading.motor_pwm is not None else 0,
            "voltage": db_reading.voltage,
            "esp32_ip": db_reading.esp32_ip,
            "received_at": db_reading.timestamp.isoformat() if db_reading.timestamp else utc_now().isoformat(),
        }
        self.latest_readings[motor_id] = reading_dict
        return MotorLatestDataResponse(**reading_dict)

    def get_motor_status(self, motor_id: str, db: Session) -> MotorStatusResponse:
        """
        Determines motor online/offline state dynamically based on timeout threshold
        and returns accumulated runtime.
        """
        now = utc_now()
        last_seen = self.last_seen_times.get(motor_id)
        current_status = self.last_statuses.get(motor_id)

        # If not in cache, check database
        if last_seen is None:
            latest_db = (
                db.query(MotorReading)
                .filter(MotorReading.motor_id == motor_id)
                .order_by(desc(MotorReading.timestamp))
                .first()
            )
            if latest_db:
                last_seen = latest_db.timestamp
                current_status = latest_db.status
                self.last_seen_times[motor_id] = last_seen
                self.last_statuses[motor_id] = current_status

        if last_seen is None:
            return MotorStatusResponse(
                motor_id=motor_id,
                status="OFF",
                online=False,
                last_seen=None,
                runtime_seconds=0.0
            )

        # Ensure timezone consistency
        if last_seen.tzinfo is None:
            last_seen = last_seen.replace(tzinfo=timezone.utc)

        time_since_last_seen = (now - last_seen).total_seconds()
        is_online = time_since_last_seen <= settings.MOTOR_ONLINE_TIMEOUT_SECONDS

        return MotorStatusResponse(
            motor_id=motor_id,
            status=current_status if current_status else "OFF",
            online=is_online,
            last_seen=last_seen.isoformat(),
            runtime_seconds=round(self.accumulated_runtimes.get(motor_id, 0.0), 2)
        )

    def get_history(self, motor_id: str, limit: int, db: Session) -> MotorHistoryResponse:
        """Queries historical telemetry records for a motor ordered chronologically or reverse."""
        readings = (
            db.query(MotorReading)
            .filter(MotorReading.motor_id == motor_id)
            .order_by(desc(MotorReading.timestamp))
            .limit(limit)
            .all()
        )

        records = [
            MotorHistoryRecord(
                id=r.id,
                motor_id=r.motor_id,
                status=r.status,
                temperature=r.temperature,
                humidity=r.humidity,
                ir=r.ir,
                ir_pulses=r.ir_pulses if r.ir_pulses is not None else 0,
                rpm=r.rpm if r.rpm is not None else 0.0,
                acs_adc=r.acs_adc,
                current=r.current,
                mpu_x=r.mpu_x,
                mpu_y=r.mpu_y,
                mpu_z=r.mpu_z,
                total_acceleration=r.total_acceleration,
                vibration=r.vibration,
                vibration_level=r.vibration_level,
                motor_pwm=r.motor_pwm if r.motor_pwm is not None else 0,
                voltage=r.voltage,
                esp32_ip=r.esp32_ip,
                timestamp=r.timestamp.isoformat() if r.timestamp else utc_now().isoformat()
            )
            for r in readings
        ]

        return MotorHistoryResponse(
            motor_id=motor_id,
            count=len(records),
            records=records
        )

    def queue_command(self, motor_id: str, command: str, db: Session) -> MotorControlResponse:
        """
        Queues a motor control command without falsely asserting physical state.
        Separates requested_command from actual_status.
        """
        command_upper = command.upper()
        command_id = f"cmd_{uuid.uuid4().hex[:12]}"
        now = utc_now()

        # Current actual status from in-memory tracking
        actual_status = self.last_statuses.get(motor_id, "OFF")

        # Save to database
        db_cmd = MotorCommand(
            command_id=command_id,
            motor_id=motor_id,
            command=command_upper,
            status="PENDING",
            created_at=now
        )
        db.add(db_cmd)
        db.commit()

        # Cache as active pending command
        self.pending_commands[motor_id] = {
            "command_id": command_id,
            "command": command_upper,
            "created_at": now.isoformat()
        }

        logger.info(f"Queued control command {command_id} for {motor_id}: {command_upper}")

        return MotorControlResponse(
            motor_id=motor_id,
            requested_command=command_upper,
            actual_status=actual_status,
            command_status="PENDING",
            command_id=command_id
        )

    def get_pending_command(self, motor_id: str, db: Session) -> PendingCommandResponse:
        """Retrieves the current pending command for the ESP32 to execute."""
        # Check in-memory pending queue first
        if motor_id in self.pending_commands:
            cmd = self.pending_commands[motor_id]
            return PendingCommandResponse(
                motor_id=motor_id,
                command=cmd["command"],
                command_id=cmd["command_id"],
                has_pending_command=True,
                created_at=cmd["created_at"]
            )

        # Fallback to database
        db_cmd = (
            db.query(MotorCommand)
            .filter(MotorCommand.motor_id == motor_id, MotorCommand.status == "PENDING")
            .order_by(desc(MotorCommand.created_at))
            .first()
        )
        if db_cmd:
            return PendingCommandResponse(
                motor_id=motor_id,
                command=db_cmd.command,
                command_id=db_cmd.command_id,
                has_pending_command=True,
                created_at=db_cmd.created_at.isoformat() if db_cmd.created_at else None
            )

        return PendingCommandResponse(
            motor_id=motor_id,
            command=None,
            command_id=None,
            has_pending_command=False,
            created_at=None
        )

    def acknowledge_command(self, motor_id: str, command_id: str, status: str, db: Session) -> CommandAckResponse:
        """Acknowledges command execution by the ESP32."""
        now = utc_now()
        status_upper = status.upper()

        db_cmd = (
            db.query(MotorCommand)
            .filter(MotorCommand.command_id == command_id, MotorCommand.motor_id == motor_id)
            .first()
        )
        if db_cmd:
            db_cmd.status = status_upper
            db_cmd.executed_at = now
            db.commit()

        # Remove from in-memory pending if matched
        if motor_id in self.pending_commands and self.pending_commands[motor_id].get("command_id") == command_id:
            del self.pending_commands[motor_id]

        logger.info(f"Command {command_id} for {motor_id} acknowledged with status: {status_upper}")

        return CommandAckResponse(
            success=True,
            message=f"Command {command_id} acknowledged as {status_upper}",
            motor_id=motor_id,
            command_id=command_id,
            acknowledged_at=now.isoformat()
        )


motor_service = MotorService()
