from flask import Flask, render_template, request, jsonify, url_for, redirect, session
from database_setup import Base, engine
from dashboard import dashboard_bp
from network_utils.status import status_bp
from network import receive_sensor_data
from AI_model import process_images_in_directory
import os
import json

from network_utils.config_handler import load_config, save_config
from network_utils.user_control import handle_manual_control
from network_utils.auth import auth_bp

# ──────────────────────────── Flask Setup ────────────────────────────
app = Flask(__name__)
app.secret_key = "8e0b7a6e4fa24739b0a05c1e5dc889d1f6d49b91ce9b213ec2af3b110d9376b9s"

Base.metadata.create_all(bind=engine)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(status_bp)

# ──────────────────────────── Paths ────────────────────────────
INPUT_DIR = 'input'
OUTPUT_DIR = 'static/predictions'

# ──────────────────────────── Routes ────────────────────────────
@app.route('/')
def index():
    print("[DEBUG] Current session:", dict(session))
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template('index.html')


@app.route('/run', methods=['POST'])
def run_yolo():
    process_images_in_directory(INPUT_DIR, OUTPUT_DIR)
    return redirect(url_for('ai_model'))


@app.route('/results')
def ai_model():
    images = [
        f for f in os.listdir(OUTPUT_DIR)
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))
    ]
    return render_template('ai_model.html', images=images)


@app.route('/receive', methods=['POST'])
def receive_data():
    return receive_sensor_data(request)


@app.route('/get_thresholds')
def get_thresholds():
    return jsonify(load_config())


@app.route('/set_thresholds', methods=['POST'])
def set_thresholds():
    data = request.get_json()
    try:
        config = load_config()
        config["TEMP_THRESHOLD"] = int(data.get("temp_threshold", config["TEMP_THRESHOLD"]))
        config["HUM_THRESHOLD"] = int(data.get("hum_threshold", config["HUM_THRESHOLD"]))
        config["SOIL_MOISTURE_THRESHOLD"] = int(data.get("soil_moisture_threshold", config["SOIL_MOISTURE_THRESHOLD"]))
        save_config(config)
        print("[DEBUG] Thresholds updated:", config)
        return jsonify({"message": "Thresholds updated successfully."})
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 400


@app.route("/manual-control", methods=["POST"])
def manual_control():
    payload = request.get_json()
    result = handle_manual_control(payload)
    return jsonify(result), 200 if result.get("status") == "success" else 400


# ───────────── Manual Control State (JSON file) ─────────────
MANUAL_STATE_FILE = os.path.join(os.path.dirname(__file__), 'network_utils', 'manual_control_state.json')


@app.route('/get_manual_mode')
def get_manual_mode():
    try:
        with open(MANUAL_STATE_FILE, "r") as f:
            state = json.load(f)
            return jsonify({
                "manual_mode": state.get("manual_mode", False),
                "ventilation_actuator_state": state.get("ventilation_actuator_state", "off"),
                "irrigation_actuator_state": state.get("irrigation_actuator_state", "off")
            })
    except Exception as e:
        print(f"[ERROR] Failed to load manual mode: {e}")
        return jsonify({"manual_mode": False})


@app.route('/set_manual_mode', methods=["POST"])
def set_manual_mode():
    data = request.get_json()
    try:
        if os.path.exists(MANUAL_STATE_FILE):
            with open(MANUAL_STATE_FILE, "r") as f:
                state = json.load(f)
        else:
            state = {
                "manual_mode": False,
                "ventilation_actuator_state": "off",
                "irrigation_actuator_state": "off"
            }

        for key in data:
            state[key] = data[key]

        with open(MANUAL_STATE_FILE, "w") as f:
            json.dump(state, f, indent=4)

        return jsonify({"status": "success", "manual_mode": state.get("manual_mode", False)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/about')
def aboutus():
    return render_template("aboutus.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


# ───────────── NEW: Live Readings for Dashboard ─────────────
@app.route('/get_latest_readings')
def get_latest_readings():
    from database_setup import SessionLocal, WeightedAverageFusionData, KalmanFilterFusionData
    session = SessionLocal()

    def get_latest_weighted(sensor_type):
        return session.query(WeightedAverageFusionData) \
                      .filter_by(SensorType=sensor_type) \
                      .order_by(WeightedAverageFusionData.Timestamp.desc()) \
                      .first()

    def get_latest_kalman(sensor_id):
        return session.query(KalmanFilterFusionData) \
                      .filter_by(SensorID=sensor_id) \
                      .order_by(KalmanFilterFusionData.Timestamp.desc()) \
                      .first()

    # Soil moisture sensor IDs
    soil_ids = [2005, 3005]
    soil_readings = []

    for sid in soil_ids:
        result = get_latest_kalman(sid)
        if result:
            soil_readings.append(result.FusedValue)

    if soil_readings:
        soil_moisture = round(sum(soil_readings) / len(soil_readings), 2)
    else:
        soil_moisture = None

    temp = get_latest_weighted("temperature")
    hum = get_latest_weighted("humidity")

    session.close()

    return jsonify({
        "temperature": round(temp.FusedValue, 2) if temp else None,
        "humidity": round(hum.FusedValue, 2) if hum else None,
        "soil_moisture": soil_moisture
    })


# ──────────────────────────── Main ────────────────────────────
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
