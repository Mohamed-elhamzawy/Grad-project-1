from sqlalchemy.orm import Session
from datetime import timedelta
import pandas as pd
from database_setup import SessionLocal, KalmanFilterFusionData

# Start DB session
session: Session = SessionLocal()

# Step 1: Get latest timestamp
latest_entry = session.query(KalmanFilterFusionData).order_by(
    KalmanFilterFusionData.Timestamp.desc()
).first()

if latest_entry:
    latest_timestamp = latest_entry.Timestamp
    start_timestamp = latest_timestamp - timedelta(minutes=20)

    # Step 2: Query data within the latest 20-minute window
    results = session.query(KalmanFilterFusionData).filter(
        KalmanFilterFusionData.Timestamp.between(start_timestamp, latest_timestamp)
    ).order_by(KalmanFilterFusionData.Timestamp.asc()).all()

    # Step 3: Convert to DataFrame
    df = pd.DataFrame([{
        "Timestamp": r.Timestamp,
        f"{r.SensorID}": r.FusedValue
    } for r in results])

    # Step 4: Pivot based on SensorID (aggregated on Timestamp)
    df_pivoted = df.pivot_table(
        index="Timestamp",
        aggfunc="first"  # If multiple values exist per sensor & timestamp, take the first
    )

    # Optional: sort columns by SensorID
    df_pivoted = df_pivoted[sorted(df_pivoted.columns, key=int)]

    # Step 5: Save to CSV
    df_pivoted.to_csv("kalman_latest_20min_pivoted.csv")
    print("✅ Pivoted CSV 'kalman_latest_20min_pivoted.csv' saved.")
else:
    print("⚠️ No data found in KalmanFilterFusionData.")

# Step 6: Close DB session
session.close()
