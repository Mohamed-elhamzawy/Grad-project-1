from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database_setup import KalmanFilterFusionData, WeightedAverageFusionData, SessionLocal


def weighted_average_fusion(values, weights):
    """Perform weighted average of given values with weights."""
    if len(values) != len(weights):
        raise ValueError("Length of values and weights must match.")
    return sum(v * w for v, w in zip(values, weights))


def fetch_recent_sensor_data(session, sensor_ids, window_seconds):
    """Fetch the most recent Kalman-filtered readings for given sensor_ids within time window."""
    now = datetime.utcnow()
    window_start = now - timedelta(seconds=window_seconds)
    latest_data = {}

    for sensor_id in sensor_ids:
        entry = session.query(KalmanFilterFusionData)\
            .filter(KalmanFilterFusionData.SensorID == sensor_id)\
            .filter(KalmanFilterFusionData.Timestamp >= window_start)\
            .order_by(KalmanFilterFusionData.Timestamp.desc())\
            .first()
        if entry:
            latest_data[sensor_id] = entry.FusedValue

    return latest_data


def process_weighted_fusion(sensor_ids, weights, sensor_type, fusion_window_seconds=60):
    """
    Run weighted average fusion on a given set of sensor IDs and weights.
    
    Args:
        sensor_ids (list): List of sensor IDs.
        weights (list): Corresponding weights (same length as sensor_ids).
        sensor_type (str): Sensor type label (e.g., "Temperature", "Humidity").
        fusion_window_seconds (int): Time window in seconds to consider valid readings.
    """
    session: Session = SessionLocal()
    try:
        sensor_data = fetch_recent_sensor_data(session, sensor_ids, fusion_window_seconds)

        if not sensor_data:
            print(f"[{sensor_type.upper()}] No recent readings available.")
            return

        available_ids = list(sensor_data.keys())
        available_values = [sensor_data[sid] for sid in available_ids]

        # Adjust weights to match available sensors
        weight_map = {sid: w for sid, w in zip(sensor_ids, weights)}
        available_weights = [weight_map[sid] for sid in available_ids]


        # Normalize weights
        total_weight = sum(available_weights)
        normalized_weights = [w / total_weight for w in available_weights]

        fused_value = weighted_average_fusion(available_values, normalized_weights)

        session.add(WeightedAverageFusionData(
            SensorType=sensor_type,
            Timestamp=datetime.utcnow(),
            FusedValue=fused_value
        ))
        session.commit()
        print(f"[{sensor_type.upper()}] Fused value: {fused_value:.2f} from {len(available_values)} sensors.")
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Fusion failed for {sensor_type}: {e}")
    finally:
        session.close()
