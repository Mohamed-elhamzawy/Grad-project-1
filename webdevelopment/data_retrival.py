from sqlalchemy.orm import sessionmaker
from database_setup import engine, Actuator, UserInteraction
import pandas as pd

# Create session
Session = sessionmaker(bind=engine)
session = Session()

# === Fetch last row from Actuator table ===
last_actuator = (
    session.query(Actuator)
    .order_by(Actuator.LastUpdated.desc())
    .first()
)

# Convert to dict
actuator_data = {
    "ActuatorID": last_actuator.ActuatorID,
    "ActuatorName": last_actuator.ActuatorName,
    "Status": last_actuator.Status,
    "LastUpdated": last_actuator.LastUpdated,
    "UserID": last_actuator.UserID,
    "DeviceID": last_actuator.DeviceID
} if last_actuator else {}

# === Fetch last row from UserInteraction table ===
last_interaction = (
    session.query(UserInteraction)
    .order_by(UserInteraction.Timestamp.desc())
    .first()
)

# Convert to dict
interaction_data = {
    "InteractionID": last_interaction.InteractionID,
    "UserID": last_interaction.UserID,
    "DeviceID": last_interaction.DeviceID,
    "ActuatorID": last_interaction.ActuatorID,
    "Action": last_interaction.Action,
    "Timestamp": last_interaction.Timestamp
} if last_interaction else {}

# Close session
session.close()

# Print output
print("\n=== Last Actuator Entry ===")
print(pd.DataFrame([actuator_data]))

print("\n=== Last UserInteraction Entry ===")
print(pd.DataFrame([interaction_data]))
