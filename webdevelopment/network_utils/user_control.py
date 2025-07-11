from datetime import datetime
from database_setup import UserInteraction, SessionLocal, Actuator

### ⬛⬛⬛ START NEW IMPORTS ⬛⬛⬛
import os
import json

MANUAL_STATE_FILE = os.path.join(os.path.dirname(__file__), "manual_control_state.json")
DEFAULT_DEVICE_ID = 1001  # fallback if actuator.DeviceID is None

def load_manual_state():
    if not os.path.exists(MANUAL_STATE_FILE):
        return {
            "manual_mode": True,
            "ventilation_actuator_state": "off",
            "irrigation_actuator_state": "off"
        }
    with open(MANUAL_STATE_FILE, "r") as f:
        return json.load(f)
### ⬛⬛⬛ END NEW IMPORTS ⬛⬛⬛

def handle_manual_control(_=None):  # Payload ignored now
    time = datetime.utcnow()
    user_id = 7000  # Fixed for manual/web control
    manual_state = load_manual_state()

    actuator_updates = [
        {"actuator_id": 2009, "name": "ventilation_fan", "action": manual_state.get("ventilation_actuator_state", "off")},
        {"actuator_id": 3009, "name": "water_pump", "action": manual_state.get("irrigation_actuator_state", "off")}
    ]

    try:
        with SessionLocal() as session:
            for update in actuator_updates:
                actuator = session.query(Actuator).filter(Actuator.ActuatorID == update["actuator_id"]).first()

                if not actuator:
                    actuator = Actuator(
                        ActuatorID=update["actuator_id"],
                        ActuatorName=update["name"],
                        Status=update["action"],
                        UserID=user_id,
                        LastUpdated=time
                    )
                    session.add(actuator)
                else:
                    actuator.Status = update["action"]
                    actuator.UserID = user_id
                    actuator.LastUpdated = time

                device_id = actuator.DeviceID or DEFAULT_DEVICE_ID
                session.add(UserInteraction(
                    UserID=user_id,
                    DeviceID=device_id,
                    ActuatorID=update["actuator_id"],
                    Action=update["action"],
                    Timestamp=time
                ))

            session.commit()
            return {"status": "success", "message": "Manual actuator states synced from JSON."}

    except Exception as e:
        return {"status": "error", "message": str(e)}
