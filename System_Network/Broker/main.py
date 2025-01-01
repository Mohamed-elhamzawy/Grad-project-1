
# import paho.mqtt.client as mqtt

# # MQTT Broker Configuration (Desktop PC IP)
# BROKER = "localhost"  # Or use 127.0.0.1 if script runs on the same PC as the broker
# PORT = 1883
# TOPICS = [("sensors/esp32/temperature", 0)]

# # Callback when connected
# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         print("Connected to MQTT Broker!")
#         for topic, qos in TOPICS:
#             client.subscribe(topic)
#             print(f"Subscribed to {topic}")
#     else:
#         print(f"Failed to connect, return code {rc}")

# # Callback when a message is received
# def on_message(client, userdata, msg):
#     print(f"Received message from {msg.topic}: {msg.payload.decode()}")

# # Initialize client
# client = mqtt.Client()
# client.on_connect = on_connect
# client.on_message = on_message

# # Connect to the local broker
# client.connect(BROKER, PORT, 60)
# client.loop_forever()

# import paho.mqtt.client as mqtt

# # MQTT Configuration
# BROKER = " 192.168.1.26"  # Replace with your Desktop PC's IP
# PORT = 1883
# TOPIC = "esp32/data"  # Topic ESP32 will publish to

# # Callback when connected
# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         print("Connected to MQTT Broker!")
#         client.subscribe(TOPIC)
#         print(f"Subscribed to {TOPIC}")
#     else:
#         print(f"Failed to connect, return code {rc}")

# # Callback when a message is received
# def on_message(client, userdata, msg):
#     print(f"Received message from {msg.topic}: {msg.payload.decode()}")

# # Initialize client
# broker_address = "192.168.1.26"  # Use the correct IP of your MQTT broker
# client = mqtt.Client()
# client.connect(broker_address, 1883)

# # client = mqtt.Client()
# # client.on_connect = on_connect
# # client.on_message = on_message

# # Connect to the broker
# try:
#     # client.connect(BROKER, PORT, 60)
#     client.connect(broker_address, 1883)
# except Exception as e:
#     print(f"Error connecting to broker: {e}")
#     exit(1)

# # Start listening for messages
# client.loop_forever()

import paho.mqtt.client as mqtt

# MQTT Configuration
BROKER = "192.168.1.26"  # Replace with your Desktop PC's IP
PORT = 1883
TOPIC = "esp32/data"  # Topic ESP32 will publish to

# Callback when connected
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(TOPIC)
        print(f"Subscribed to {TOPIC}")
    else:
        print(f"Failed to connect, return code {rc}")

# Callback when a message is received
def on_message(client, userdata, msg):
    print(f"Received message from {msg.topic}: {msg.payload.decode()}")

# Initialize MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker
try:
    print(f"Connecting to MQTT Broker at {BROKER}:{PORT}...")
    client.connect(BROKER, PORT, 60)
except Exception as e:
    print(f"Error connecting to broker: {e}")
    exit(1)

# Start listening for messages
client.loop_forever()
