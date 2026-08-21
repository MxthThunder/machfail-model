/**
 * Real-Time ESP32 Motor Telemetry & AI Backend API Client
 * Connects Frontend Web Dashboard to FastAPI Backend Server at http://127.0.0.1:8000
 */

export interface MotorTelemetryData {
  motor_id: string;
  status: string;
  temperature: number;
  humidity: number;
  ir: number;
  ir_pulses: number;
  rpm: number;
  acs_adc: number;
  current: number;
  mpu_x: number;
  mpu_y: number;
  mpu_z: number;
  total_acceleration: number;
  vibration: number;
  vibration_level: 'LOW' | 'MEDIUM' | 'HIGH';
  motor_pwm: number;
  voltage?: number | null;
  esp32_ip?: string | null;
  received_at?: string;
  timestamp?: string;
}

export interface MotorStatusData {
  motor_id: string;
  status: string;
  online: boolean;
  last_seen: string | null;
  runtime_seconds: number;
}

export interface MotorHistoryData {
  motor_id: string;
  count: number;
  records: MotorTelemetryData[];
}

export interface ConditionParameter {
  value: number;
  unit: string;
  condition: 'NORMAL' | 'MEDIUM' | 'HIGH';
  score: number;
}

export interface MotorConditionAnalysis {
  motor_id: string;
  temperature: ConditionParameter;
  rpm: ConditionParameter;
  current: ConditionParameter;
  vibration: ConditionParameter;
  overall_condition: 'NORMAL' | 'MEDIUM' | 'HIGH';
  condition_score: number;
  maximum_score: number;
  failure_risk: 'LOW' | 'MEDIUM' | 'HIGH';
  risk_type: string;
  stages: {
    sensor_data_analysis: string;
    motor_condition_prediction: string;
    failure_risk_analysis: string;
  };
  message: string;
  timestamp: string;
}

export interface SensorReading {
  rpm: number;
  temperature: number;
  humidity: number;
  current: number;
  vibration: number;
}

export interface PredictionResponse {
  status: 'NORMAL' | 'WARNING' | 'FAULT';
  health_score: number;
  confidence: number;
  prediction: string;
  contributing_factors: string[];
}

export interface ModelInfoResponse {
  model_type: string;
  version: string;
  train_date: string;
  training_samples: number;
  test_accuracy: number;
  cv_macro_f1_mean: number;
  classes: string[];
  features: string[];
}

export interface HealthCheckResponse {
  status: string;
  service?: string;
  timestamp: string;
}

const API_BASE_URL = 'http://127.0.0.1:8000';
const WS_BASE_URL = 'ws://127.0.0.1:8000';

/**
 * Fetches latest real telemetry data for a motor from backend.
 */
export async function fetchLatestMotorTelemetry(motorId: string = 'M001'): Promise<MotorTelemetryData | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/motor/latest?motor_id=${encodeURIComponent(motorId)}`);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

/**
 * Fetches real motor online/offline status and runtime.
 */
export async function fetchMotorStatus(motorId: string = 'M001'): Promise<MotorStatusData | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/motor/status?motor_id=${encodeURIComponent(motorId)}`);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

/**
 * Fetches historical sensor readings from SQLite database.
 */
export async function fetchMotorHistory(motorId: string = 'M001', limit: number = 50): Promise<MotorHistoryData | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/motor/history/${encodeURIComponent(motorId)}?limit=${limit}`);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

/**
 * Fetches real-time condition analysis for the latest ESP32 telemetry.
 */
export async function fetchMotorCondition(motorId: string = 'M001'): Promise<MotorConditionAnalysis | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/motor/condition/${encodeURIComponent(motorId)}`);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

/**
 * Manually analyzes provided telemetry parameters.
 */
export async function analyzeMotorCondition(params: {
  motor_id?: string;
  temperature: number;
  rpm: number;
  current: number;
  vibration: number;
}): Promise<MotorConditionAnalysis> {
  const res = await fetch(`${API_BASE_URL}/api/motor/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      motor_id: params.motor_id || 'M001',
      temperature: params.temperature,
      rpm: params.rpm,
      current: params.current,
      vibration: params.vibration,
    }),
  });
  if (!res.ok) {
    throw new Error(`Condition analysis failed: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Queues a motor control command (ON/OFF).
 */
export async function sendMotorControl(motorId: string, command: 'ON' | 'OFF') {
  const res = await fetch(`${API_BASE_URL}/api/motor/control`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ motor_id: motorId, command }),
  });
  if (!res.ok) {
    throw new Error(`Control command failed: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Creates a real-time WebSocket connection to receive live ESP32 pushes.
 */
export function connectMotorWebSocket(
  motorId: string = 'M001',
  onMessage: (payload: { type: string; data: MotorTelemetryData; condition?: MotorConditionAnalysis; online: boolean; runtime_seconds: number }) => void,
  onError?: (err: Event) => void
): WebSocket {
  const socket = new WebSocket(`${WS_BASE_URL}/ws/motor/${encodeURIComponent(motorId)}`);
  
  socket.onmessage = (event) => {
    try {
      const parsed = JSON.parse(event.data);
      onMessage(parsed);
    } catch {
      // ignore non-json messages like pong
    }
  };

  if (onError) socket.onerror = onError;
  return socket;
}

/**
 * AI Prediction Endpoint (if ML server running)
 */
export async function fetchPrediction(reading: SensorReading): Promise<PredictionResponse> {
  const response = await fetch(`${API_BASE_URL}/predict`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(reading),
  });

  if (!response.ok) {
    throw new Error(`Inference API error: ${response.statusText}`);
  }

  return response.json();
}

export async function fetchModelInfo(): Promise<ModelInfoResponse | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/model-info`);
    if (!response.ok) return null;
    return response.json();
  } catch {
    return null;
  }
}

export async function fetchSystemHealth(): Promise<HealthCheckResponse | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    if (!response.ok) return null;
    return response.json();
  } catch {
    return null;
  }
}