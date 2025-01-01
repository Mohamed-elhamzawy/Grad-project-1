#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "WE_8ABD0C";
const char* password = "m3605330";
const char* serverUrl = "http://192.168.1.26:5000/receive";

float getTemperature() {
  // Simulate a temperature reading
  return random(20, 35) + 0.5;
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);

    float temperature = getTemperature();
    String payload = String("{\"device_id\":\"living_room\",\"temperature\":") + temperature + ",\"timestamp\":\"2024-12-05T15:30:00Z\"}";
    http.addHeader("Content-Type", "application/json");
    
    int httpResponseCode = http.POST(payload);
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Response from server: " + response);
    } else {
      Serial.println("Error sending data");
    }
    http.end();
  }
  delay(5000); // Send data every 5 seconds
}
