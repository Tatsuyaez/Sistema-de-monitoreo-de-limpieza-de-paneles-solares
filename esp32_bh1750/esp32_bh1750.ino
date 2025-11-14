

#include <Wire.h>
#include <BH1750.h>

BH1750 lightMeter;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  if (lightMeter.begin()) {
    Serial.println("BH1750 iniciado");
  } else {
    Serial.println("Error iniciando BH1750");
  }
}

void loop() {
  float lux = lightMeter.readLightLevel();
  if (isnan(lux)) {
    // lectura inválida
    Serial.println("LUX:0");
  } else {
    Serial.print("LUX:");
    Serial.println(lux);
  }
  delay(1000); // enviar cada 1 segundo
}
