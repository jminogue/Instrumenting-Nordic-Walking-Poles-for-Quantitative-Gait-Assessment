/*
notes

*/

#include "HX711.h"

#define DOUT  5
#define CLK  4

HX711 scale;

float calibration_factor = 10000;

void setup() {
  Serial.begin(115200);
  scale.begin(DOUT, CLK);
  scale.set_scale();
  scale.tare(); //Reset the scale to 0
  scale.set_scale(calibration_factor); //Adjust to this calibration factor
}

void loop() {

  Serial.print(millis()/1000.00);
  Serial.print("\t");
  Serial.print(scale.get_units() * 0.453592, 1); // converting from lbs to kg
  Serial.print(" kg");
  Serial.println();


}
