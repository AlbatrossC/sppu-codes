int red_light_pin = 5;
int green_light_pin = 6;
int blue_light_pin = 3;

unsigned int red, green, blue;

void setup() {
  pinMode(red_light_pin, OUTPUT);
  pinMode(green_light_pin, OUTPUT);
  pinMode(blue_light_pin, OUTPUT);
}

void loop() {
  red = analogRead(A0);
  red = (red / 4);
  green = analogRead(A2);
  green = (green / 4);
  blue = analogRead(A3);
  blue = (blue / 4);  

  RGB_color(255 - red, 255 - green, 255 - blue); // Red

  /*
    Change LED color by uncommenting desired RGB_color() line and commenting others.
    RGB_color(0, 255, 255); // Cyan
    RGB_color(255, 0, 255); // Magenta
    RGB_color(255, 255, 0); // Yellow
    RGB_color(0, 0, 125); // Raspberry
    RGB_color(255, 0, 0); // Red
    RGB_color(0, 255, 0); // Green
    RGB_color(0, 0, 255); // Blue
    RGB_color(0, 0, 0); // White
  */
}

void RGB_color(int red_light_value, int green_light_value, int blue_light_value) {
  analogWrite(red_light_pin, red_light_value);
  analogWrite(green_light_pin, green_light_value);
  analogWrite(blue_light_pin, blue_light_value);
}
