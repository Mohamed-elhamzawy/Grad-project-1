from flask import Blueprint, render_template, jsonify
from database_setup import SessionLocal, SensorData, KalmanFilterFusionData, WeightedAverageFusionData
from collections import defaultdict
import json

dashboard_bp = Blueprint('dashboard', __name__)

sensor_labels = {
    2001: "Temperature - DHT1 Internal",
    2002: "Humidity - DHT1 Internal",
    2003: "Temperature - DHT2 Internal",
    2004: "Humidity - DHT2 Internal",
    2005: "Soil Moisture - Plant 1",
    3001: "Temperature - DHT3 Internal",
    3002: "Humidity - DHT3 Internal",
    3003: "Temperature - DHT4 External",
    3004: "Humidity - DHT4 External",
    3005: "Soil Moisture - Plant 2"
}

@dashboard_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@dashboard_bp.route("/api/dashboard-data")
def dashboard_data():
    session = SessionLocal()
    try:
        # --- RAW SENSOR DATA ---
        raw_data = session.query(SensorData).order_by(SensorData.Timestamp).all()
        grouped_raw = defaultdict(list)
        for entry in raw_data:
            grouped_raw[entry.SensorID].append({
                "timestamp": entry.Timestamp.isoformat(),
                "value": entry.Value
            })

        raw_plot_data = [
            {
                "label": sensor_labels.get(sensor_id, f"Sensor {sensor_id}"),
                "sensor_id": sensor_id,
                "timestamps": [d["timestamp"] for d in data],
                "values": [d["value"] for d in data]
            }
            for sensor_id, data in grouped_raw.items()
        ]

        # --- KALMAN FILTER FUSION DATA ---
        kalman_data = session.query(KalmanFilterFusionData).order_by(KalmanFilterFusionData.Timestamp).all()
        grouped_kalman = defaultdict(list)
        for entry in kalman_data:
            grouped_kalman[entry.SensorID].append({
                "timestamp": entry.Timestamp.isoformat(),
                "value": entry.FusedValue
            })
        kalman_plot_data = [
            {
                "label": sensor_labels.get(sensor_id, f"Sensor {sensor_id}"),
                "sensor_id": sensor_id,
                "timestamps": [d["timestamp"] for d in data],
                "values": [d["value"] for d in data]
            }
            for sensor_id, data in grouped_kalman.items()
        ]

        # --- WEIGHTED AVERAGE FUSION DATA ---
        weighted_data = session.query(WeightedAverageFusionData).order_by(WeightedAverageFusionData.Timestamp).all()
        grouped_weighted = defaultdict(list)
        for entry in weighted_data:
            grouped_weighted[entry.SensorType].append({
                "timestamp": entry.Timestamp.isoformat(),
                "value": entry.FusedValue
            })
        weighted_plot_data = [
            {
                "sensor_type": sensor_type,
                "timestamps": [d["timestamp"] for d in data],
                "values": [d["value"] for d in data]
            }
            for sensor_type, data in grouped_weighted.items()
        ]

        return jsonify({
            "raw": raw_plot_data,
            "kalman": kalman_plot_data,
            "weighted": weighted_plot_data
        })

    finally:
        session.close()
