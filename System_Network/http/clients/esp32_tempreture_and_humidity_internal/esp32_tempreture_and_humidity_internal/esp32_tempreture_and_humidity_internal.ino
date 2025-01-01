#include <WiFi.h>
#include <HTTPClient.h>
#include <base64.h>  // Ensure you have this library for Base64 encoding

const char* ssid = "WE_8ABD0C";
const char* password = "m3605330";
const char* serverUrl = "http://192.168.1.7:5000/receive";
const char* serverUsername = "esp_Temp_humid_1";
const char* serverPassword = "esp_password";

#define LED_BUILTIN 2  // ESP32 internal LED pin (usually pin 2)

// Function to simulate temperature readings
float getTemperature() {
  return random(25, 40) + 0.5;
}

// Function to simulate humidity readings
float getHumidity() {
  return random(30, 90) + 0.5;
}

// Function to blink the LED
void blinkLed() {
  for (int i = 0; i < 5; i++) {  // Blink 5 times
    digitalWrite(LED_BUILTIN, HIGH);
    delay(500);
    digitalWrite(LED_BUILTIN, LOW);
    delay(500);
  }
}

void setup() {
  Serial.begin(115200);

  // Initialize the built-in LED pin
  pinMode(LED_BUILTIN, OUTPUT);

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

    // Add Basic Authentication headers
    String authHeader = "Basic " + base64::encode(String(serverUsername) + ":" + serverPassword);
    http.addHeader("Authorization", authHeader);

    // Simulate temperature and humidity readings
    float temperature = getTemperature();
    float humidity = getHumidity();

    // Create JSON payload with the correct device_id
    String payload = String("{\"device_id\":\"") + String(serverUsername) + 
                     String("\",\"temperature\":") + temperature +
                     String(",\"humidity\":") + humidity + "}";

    Serial.println("Sending payload: " + payload);
    http.addHeader("Content-Type", "application/json");

    // Send HTTP POST request
    int httpResponseCode = http.POST(payload);
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Response from server: " + response);

      // Parse server response
      if (response.indexOf("\"device_id\":\"" + String(serverUsername) + "\"") != -1) {
        if (response.indexOf("\"action\":\"blink_led\"") != -1) {
          Serial.println("Blinking LED as per server command");
          blinkLed();
        }
      } else {
        Serial.println("Response not for this ESP");
      }
    } else {
      Serial.println("Error sending data");
    }
    http.end();
  }
  delay(5000);  // Send data every 5 seconds
}
