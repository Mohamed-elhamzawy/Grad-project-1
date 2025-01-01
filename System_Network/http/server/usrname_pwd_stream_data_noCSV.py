from flask import Flask, request, jsonify

app = Flask(__name__)

# Define valid credentials
credentials = {
    "esp_Temp_humid_1": "esp_password",
    "esp_Soil_moisture_1" : "esp_password"
}

USERNAME = "esp_user"
PASSWORD = "esp_password"

def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

@app.route('/receive', methods=['POST'])
def receive_data():
    # Get Authorization header
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return jsonify({"error": "Unauthorized"}), 401  # Unauthorized

    try:
        data = request.json
        if not data:
            return jsonify({"error": "Invalid or missing JSON payload"}), 400

        device_id = data.get('device_id')
        temperature = data.get('temperature')

        if device_id is None or temperature is None:
            return jsonify({"error": "Missing 'device_id' or 'temperature' in payload"}), 400

        print(f"Received from {device_id}: {temperature}°C")

        # Check for temperature threshold
        if device_id == "kitchen" and temperature > 30:  # Kitchen-specific threshold
            action = "blink_led"
        else:
            action = "no_action"

        # Respond with action
        response = {
            "action": action
        }
        return jsonify(response)

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)