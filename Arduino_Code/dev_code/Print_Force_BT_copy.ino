#include <dummy.h>

#include <dummy.h>

#include "HX711.h"
#include "BluetoothSerial.h"

BluetoothSerial SerialBT;

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to enable it
#endif

#if !defined(CONFIG_BT_SPP_ENABLED)
#error Serial Bluetooth not available or not enabled. It is only available for
the ESP32 chip.
#endif

#define calibration_factor 19000 // Adjust this after re-testing
#define DOUT 5
#define CLK 4

HX711 scale;

void setup() {
  Serial.begin(115200);
  SerialBT.begin("Walking_Pole"); // Bluetooth device name
  scale.begin(DOUT, CLK); // Assume RATE pin is wired HIGH externally for 80 Hz
  scale.set_scale();
  scale.tare(); // Reset to zero
  scale.set_scale(calibration_factor); // Apply calibration factor
  scale.tare(); // Reset to zero again for accuracy
}
void loop() {
  if (scale.is_ready()) {
  float force = scale.get_units(1); // One sample for faster reading
  
  unsigned long now = millis();
  SerialBT.print(now / 1000.0, 3); // Print time in seconds with 3 decimals
  SerialBT.print(",");
  SerialBT.println(force, 2); // Print force with 2 decimal places
  }
}
