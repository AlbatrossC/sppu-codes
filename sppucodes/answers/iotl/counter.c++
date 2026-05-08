const int green_led  = 0;
const int yellow_led = 1;
const int red_led    = 2;

unsigned int counter = 0;

void setup() {
  pinMode(green_led, OUTPUT);
  pinMode(yellow_led, OUTPUT);
  pinMode(red_led, OUTPUT);
  digitalWrite(green_led, HIGH);
  digitalWrite(yellow_led, HIGH);
  digitalWrite(red_led, HIGH);
}

void loop() {
  counter++;
  delay(50);
  digitalWrite(green_led, HIGH);
  digitalWrite(yellow_led, HIGH);
  digitalWrite(red_led, HIGH);

  if (counter < 100) {
    digitalWrite(green_led, LOW);
  } 
  else if (counter >= 101 && counter <= 200) {
    digitalWrite(yellow_led, LOW);
  } 
  else if (counter > 200) {
    digitalWrite(red_led, LOW);
  }

  if (counter > 210) {
    counter = 0;
  }
}
