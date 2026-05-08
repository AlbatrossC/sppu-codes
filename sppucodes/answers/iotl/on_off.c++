// a) On / OFF LED 

#include <stdio.h>
#include <stdlib.h>

const int button = 8;    // GPIO 8 for the button
const int led = 7;       // GPIO 7 for the LED

int ledFlag = 0;         // LED status flag

void setup() {
    pinMode(button, INPUT);     // Define button as input
    pinMode(led, OUTPUT);       // Define LED as output
    digitalWrite(led, LOW);     // Ensure LED is off at startup
}

void loop() {
    if (digitalRead(button) == HIGH) {  // If button is pressed
        if (ledFlag == 0) {
            ledFlag = 1;                // Set flag
            digitalWrite(led, HIGH);    // Turn LED on
        } else {
            ledFlag = 0;                // Reset flag
            digitalWrite(led, LOW);     // Turn LED off
        }
        delay(1000);                    // Debounce delay
    }
}
