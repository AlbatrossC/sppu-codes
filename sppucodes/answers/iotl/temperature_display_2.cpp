//this Code includes printing of min and max
//however this code is not TESTED

#include <dht.h>

dht DHT;

#define DHT11_PIN A1
float min_f, max_f;

void setup()
{
  Serial.begin(9600);
  Serial.println("Humidity (%),\tTemp (C),\tTemp (F),\tMin Temp (F),\tMax Temp (F)");

  min_f = 9999;
  max_f = -9999;
}

void loop()
{
  int chk = DHT.read11(DHT11_PIN);

  float currentF = DHT.temperature * 1.8 + 32;

  // Update min/max
  if (currentF < min_f) min_f = currentF;
  if (currentF > max_f) max_f = currentF;

  // Display all values
  Serial.print(DHT.humidity, 1);
  Serial.print("\t\t");
  Serial.print(DHT.temperature, 1);
  Serial.print("\t\t");
  Serial.print(currentF, 1);
  Serial.print("\t\t");
  Serial.print(min_f, 1);
  Serial.print("\t\t");
  Serial.println(max_f, 1);

  delay(1000);
}
