#include "DHT.h"
#include <Servo.h>

#define DHTPIN 2     // Digital pin connected to the DHT sensor
#define DHTTYPE DHT11   // DHT 11

DHT dht(DHTPIN, DHTTYPE);

// Soil Moisture Sensor Module
#define sensorPin A0
const int SENSOR_MIN = 0;   // Minimum sensor value (no water)
const int SENSOR_MAX = 1023;  // Maximum sensor value (fully wet)
// Function to map the raw sensor value to a percentage
int waterPercentage;
int mapToPercentage(int sensorValue) {
  // Map the sensor value from the range SENSOR_MIN to SENSOR_MAX to the range 0 to 100
return map(sensorValue, SENSOR_MIN, SENSOR_MAX,100,0);
}

// Light Sensor Module
const int ldr_pin = A1;

// Traffic Light Module
const int PIN_RED = 12;
const int PIN_YELLOW = 10;
const int PIN_GREEN = 7;

// Servo
Servo myServo;
const int SERVO_PIN = 13;

// Flags to track serial control
bool serialControlLED = false;
bool serialControlServo = false;
String serialLEDStatus = "None";
int serialServoAngle = 0;

void setup() {
    pinMode(ldr_pin, INPUT);
    pinMode(PIN_RED, OUTPUT);
    pinMode(PIN_YELLOW, OUTPUT);
    pinMode(PIN_GREEN, OUTPUT);
    pinMode(SERVO_PIN, OUTPUT);
    myServo.attach(SERVO_PIN);
    Serial.begin(9600);
    dht.begin();
}

void loop() {
 

    // DHT Sensor Module
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    // Soil Moisture Sensor Module
    int moisture = analogRead(sensorPin);
    waterPercentage = mapToPercentage(moisture);

    // Light Sensor Module
    int lightReading = analogRead(ldr_pin);


    // Print readings
    Serial.print(humidity);
    Serial.print(",");
    Serial.print(temperature);
    Serial.print(",");
    Serial.print(lightReading);
    Serial.print(",");
    Serial.print(waterPercentage);
    Serial.print("\n");

    if (Serial.available() > 0) {
        String data = Serial.readStringUntil('\n');

        if (data.startsWith("Led: ")) {
            serialLEDStatus = data.substring(5, data.indexOf("\n"));
            serialControlLED = true;
        }

        if (data.startsWith("Servo Angle: ")) {
            serialServoAngle = data.substring(13).toInt();
            serialControlServo = true;
        }
    }

    // Override functions with serial control if applicable
    if (serialControlLED) {
        if (serialLEDStatus == "Green") {
            digitalWrite(PIN_GREEN, HIGH);
            digitalWrite(PIN_YELLOW, LOW);
            digitalWrite(PIN_RED, LOW);
        } else if (serialLEDStatus == "Yellow") {
            digitalWrite(PIN_GREEN, LOW);
            digitalWrite(PIN_YELLOW, HIGH);
            digitalWrite(PIN_RED, LOW);
        } else if (serialLEDStatus == "Red") {
            digitalWrite(PIN_GREEN, LOW);
            digitalWrite(PIN_YELLOW, LOW);
            digitalWrite(PIN_RED, HIGH);
        } else {
            // Turn off all LEDs if status is unknown
            digitalWrite(PIN_GREEN, LOW);
            digitalWrite(PIN_YELLOW, LOW);
            digitalWrite(PIN_RED, LOW);
        }
    }

    if (serialControlServo) {
        myServo.write(serialServoAngle);
    }

    delay(3000);
}
