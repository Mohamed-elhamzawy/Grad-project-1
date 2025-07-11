from datetime import datetime
from database_setup import Actuator, UserInteraction

def log_user_action(session, device_id, action, user_id, actuator_id):
    print("[DEBUG] actuator_control.py/log_user_action loaded successfully.")
    session.add(UserInteraction(
        DeviceID=device_id,
        Action=action,
        UserID=user_id,
        ActuatorID=actuator_id,
        Timestamp=datetime.utcnow()))
    print("[DEBUG] actuator_control.py/log_user_action loaded successfully [WORKED].")

def control_actuator(session, actuator_name, status, user_id):
    print("[DEBUG] actuator_control.py/control_actuator loaded successfully.")
    actuator = session.query(Actuator).filter_by(ActuatorName=actuator_name).first()
    if not actuator:
        actuator = Actuator(ActuatorName=actuator_name, Status=status, LastUpdated=datetime.utcnow(), UserID=user_id)
        session.add(actuator)
    else:
        if actuator.Status != status:
            actuator.Status = status
            actuator.LastUpdated = datetime.utcnow()
            actuator.UserID = user_id
            log_user_action(session, actuator.ActuatorID, f"{actuator_name}_{status.lower()}", user_id, actuator.ActuatorID)
    session.commit()
    print("[DEBUG] actuator_control.py/control_actuator loaded successfully [WORKED].")
    return actuator
