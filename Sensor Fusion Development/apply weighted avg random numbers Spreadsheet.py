import pandas as pd


# Function for weighted average fusion
def weighted_average_fusion(sensor_data, weights):
    n = len(sensor_data)
    fused_value = []
    subreading = [0,0,0]
    subweight = [0,0,0]
    for i in range(int(n/3)):
        for j in range(3):
            subreading[j] = sensor_data[3*i+j]
            subweight[j] =weights[3*i+j]
        result = subreading[0]*subweight[0]+subreading[1]*subweight[1]+subreading[2]*subweight[2]
        fused_value.append(result)
    return fused_value



# Read data from Excel file
file_path = "fusiondata.csv"
# Replace with your sheet name

# Load the Excel sheet
data = pd.read_csv(file_path)

# Extract values from "Temp 1 (C)", "Temp 2 (C)", and "Temp 3 (C)" columns
temp_1 = data["Temp  1 (C)"]
temp_2 = data["Temp 2 (C)"]
temp_3 = data["Temp 3 (C)"]


# Combine the values in the specified order
sr1 = list(temp_1)
sr2 = list(temp_2)
sr3 = list(temp_3)
sensor_readings = []

for i in range(len(sr1)):
    sensor_readings.append(sr1[i])
    sensor_readings.append(sr2[i])
    sensor_readings.append(sr3[i])


# Filter out readings outside the range of 10-30
filtered_readings = [reading for reading in sensor_readings if 10 <= reading <= 30]

# Assign weights (ensure they sum to 1)
weights = data.loc[0, ["W1", "W2", "W3"]].tolist()  # First row weights

sensor_weights = weights * (len(filtered_readings) // len(weights))  # Adjust for size
print(len(sensor_readings))
print(filtered_readings)
if len(filtered_readings) != len(sensor_weights):
    print("Error: Number of valid readings does not match the number of weights.")
else:
    # Apply weighted average fusion
    fused_reading = weighted_average_fusion(filtered_readings, sensor_weights)
    print("Fused sensor reading:", fused_reading)