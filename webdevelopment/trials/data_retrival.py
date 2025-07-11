from sqlalchemy.orm import sessionmaker
from database_setup import engine, SensorData,UserInteraction
import pandas as pd

# this could also be used for sensor fusion

#  Create session
Session = sessionmaker(bind=engine)
session = Session()

#  Fetch all readings as a list of dictionaries
data = session.query(UserInteraction).all()

# Convert SQLAlchemy objects to dictionaries
result_list = [
    {"DeviceID": d.DeviceID, "UserID": d.UserID, "Action": d.Action, "Timestamp": d.Timestamp}
    for d in data
]

#  Close session
session.close()

print("\n Retrieved Sensor Readings List:")
print(result_list)
# data=result_list
# # Convert to Pandas DataFrame
# df = pd.DataFrame(data)

# # Convert 'Timestamp' column to datetime format (if needed)
# df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# # Convert Timestamp to datetime
# df["Timestamp"] = pd.to_datetime(df["Timestamp"])

# # Pivot the table to restructure data
# df_pivot = df.pivot_table(index=["Timestamp", "DeviceID"], columns="SensorType", values="Value", aggfunc="first")

# # Rename columns explicitly to match the required output
# df_pivot.columns = df_pivot.columns.rename(None)  # Remove MultiIndex column names
# df_pivot.rename(columns={
#     "temperature": "temperature",
#     "humidity": "humidity",
#     "soil_moisture": "soil_moisture"
# }, inplace=True)

# # Reset index to bring columns back
# df_pivot.reset_index(inplace=True)

# # Rename Timestamp to time
# df_pivot.rename(columns={"Timestamp": "time"}, inplace=True)

# # Display result
# print(df_pivot)