#include <WiFi.h>
#include <PubSubClient.h>

// Wi-Fi Configuration
const char* ssid = "WE_8ABD0C";       // Replace with your Wi-Fi SSID
const char* password = "m3605330"; // Replace with your Wi-Fi password
const char* mqtt_user = "green";
const char* mqtt_password = "2457";
// MQTT Broker Configuration
const char* mqtt_server = "192.168.1.26"; // Replace with the broker's IP
const int mqtt_port = 1883;               // Default MQTT port

const char* topic = "esp32/data";         // MQTT topic to publish to

WiFiClient espClient;
PubSubClient client(espClient);

// Connect to Wi-Fi
void setup_wifi() {
  delay(10);
  Serial.println("Connecting to Wi-Fi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi connected!");
}

// MQTT Callback (optional, for subscribing)
void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.println(topic);
}

// Reconnect to MQTT Broker if disconnected
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32_Client")) { // Client ID
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  // if (!client.connected()) {
  //   reconnect();
  // }
  // client.loop();

  // // Send data
  // String data = "Temperature: 25.3"; // Replace with actual sensor data
  // Serial.println("Publishing data: " + data);
  // client.publish(topic, data.c_str());
  
  // delay(5000); // Publish every 5 seconds
  // Modify the connection part
  while (!client.connected()) {
  if (client.connect("ESP32_Client", mqtt_user, mqtt_password)) {
    Serial.println("Connected to MQTT Broker");
  } else {
    Serial.print("Failed with state ");
    Serial.println(client.state());
    delay(2000);
  }
}
}

