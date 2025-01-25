const int green_led = 0;
const int yellow_led = 1;
const int red_led = 2;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
}

char key = 0;

void loop() {
  Serial.begin(9600);

  while (1) {
    key = Serial.read();
    if ((key == 'b') || (key == 'B')) break;
    if ((key == 'g') || (key == 'G')) break;
    if ((key == 'r') || (key == 'R')) break;
    if ((key == 'y') || (key == 'Y')) break;
    delay(100);
  }

  Serial.end();
  delay(200);

  // Set LED pins as outputs
  pinMode(green_led, OUTPUT);
  pinMode(red_led, OUTPUT);
  pinMode(yellow_led, OUTPUT);

  if ((key == 'b') || (key == 'B')) {
    digitalWrite(yellow_led, HIGH);
    digitalWrite(red_led, HIGH);

    for (int i = 0; i < 10; i++) {
      digitalWrite(green_led, LOW);
      delay(500);

      digitalWrite(green_led, HIGH);
      delay(500);
    }
    key = 0;
  }

  if ((key == 'g') || (key == 'G')) {
    digitalWrite(yellow_led, HIGH);
    digitalWrite(green_led, LOW);
    digitalWrite(red_led, HIGH);
    delay(5000);

    digitalWrite(yellow_led, HIGH);
    digitalWrite(green_led, HIGH);
    digitalWrite(red_led, HIGH);
    key = 0;

  } else if ((key == 'y') || (key == 'Y')) {
    digitalWrite(yellow_led, LOW);
    digitalWrite(green_led, HIGH);
    digitalWrite(red_led, HIGH);
    delay(5000);

    digitalWrite(yellow_led, HIGH);
    digitalWrite(green_led, HIGH);
    digitalWrite(red_led, HIGH);
    key = 0;

  } else if ((key == 'r') || (key == 'R')) {
    digitalWrite(yellow_led, HIGH);
    digitalWrite(green_led, HIGH);
    digitalWrite(red_led, LOW);
    delay(5000);

    digitalWrite(yellow_led, HIGH);
    digitalWrite(green_led, HIGH);
    digitalWrite(red_led, HIGH);
    key = 0;
    
  }
}
