int ledPin = 13;

void setup() {
  pinMode(ledPin, OUTPUT);
}

void loop() {
  digitalWrite(ledPin, HIGH);
  delay(1000);

    // 1000 milliseconds = 1 seconds

  digitalWrite(ledPin, LOW);
  delay(1000);
}
