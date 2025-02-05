void setup() {
  Serial.begin(9600);
  Serial.println("Input a number:");
}

void loop() {
  if (Serial.available() > 0) {
    int input = Serial.parseInt();
    if (input != 0) {
      int inputSquared = square(input);
      Serial.print("Squared: ");
      Serial.println(inputSquared);
    } else {
      Serial.println("Please enter a valid number.");
    }
  }
  delay(500);
}

int square(int num) {
  return num * num;
}
