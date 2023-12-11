#include "HX711.h"
#include "BluetoothSerial.h"

BluetoothSerial SerialBT;

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

#if !defined(CONFIG_BT_SPP_ENABLED)
#error Serial Bluetooth not available or not enabled. It is only available for the ESP32 chip.
#endif

#define calibration_factor 22000 //This value is obtained using the SparkFun_HX711_Calibration sketch
#define DOUT  5
#define CLK  4

HX711 scale;

void setup() {
  Serial.begin(115200);
  SerialBT.begin("Walking_Pole"); //bluetooth device name
  scale.begin(DOUT, CLK);
  scale.set_scale();
  scale.tare(); //Reset the scale to 0
  scale.set_scale(calibration_factor); //Adjust to this calibration factor
  scale.tare(); //Reset the scale to 0
}

void loop() {
  SerialBT.print(millis() / 1000.00);
  SerialBT.print(",");
  SerialBT.println(scale.get_units(), 1);
}
