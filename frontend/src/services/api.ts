/**
 * AI Predictive Maintenance Microservice Client
 * Connects to the FastAPI backend at http://127.0.0.1:8000
 */

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

const API_BASE_URL = 'http://127.0.0.1:8000';

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
