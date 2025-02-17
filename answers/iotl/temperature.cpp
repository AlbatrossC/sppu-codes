#include <dht.h>

dht DHT;
#define DHT11_PIN A1

void setup()
{
  Serial.begin(9600);
  Serial.println("Humidity (%),\tTemperature (C)");
}

void loop()
{
  // READ DATA
  int chk = DHT.read11(DHT11_PIN);

  // DISPLAY DATA (Humidity and Temperature)
  Serial.print("Humidity: ");
  Serial.print(DHT.humidity, 1);  // Print humidity with one decimal place
  Serial.print("%\t");

  Serial.print("Temperature: ");
  Serial.println(DHT.temperature, 1);  // Print temperature with one decimal place

  delay(1000);  // Wait 1 second before reading again
}
