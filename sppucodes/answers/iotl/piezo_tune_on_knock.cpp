const int buzzer = A1;             // LED connected to digital pin 13
const int knockSensor = A1;        // the piezo is connected to analog pin 0
const int threshold = 400;         // threshold value to decide when the detected sound is a knock or not

// these variables will change:
int sensorReading = 0;             // variable to store the value read from the sensor pin

void setup() {
    pinMode(buzzer, INPUT);
}

void loop() {
    // read the sensor and store it in the variable sensorReading:
    sensorReading = analogRead(knockSensor);

    // if the sensor reading is greater than the threshold:
    if (sensorReading >= threshold) {
        pinMode(buzzer, OUTPUT);
        tone(buzzer, 261);  // Sounds the buzzer at the frequency relative to the note C in Hz
        delay(200);         // Waits some time to turn off
        noTone(buzzer);     // Turns the buzzer off

        tone(buzzer, 293);  // Sounds the buzzer at the frequency relative to the note D in Hz
        delay(200);
        noTone(buzzer);     // Turns the buzzer off

        tone(buzzer, 329);  // Sounds the buzzer at the frequency relative to the note E in Hz
        delay(200);
        noTone(buzzer);     // Turns the buzzer off

        tone(buzzer, 349);  // Sounds the buzzer at the frequency relative to the note F in Hz
        delay(200);
        noTone(buzzer);     // Turns the buzzer off

        tone(buzzer, 392);  // Sounds the buzzer at the frequency relative to the note G in Hz
        delay(200);
        noTone(buzzer);     // Turns the buzzer off
    }

    delay(100);  // delay to avoid overloading the serial port buffer
}
