"""
simple test sensor AH10 of ATH20 temperature sensor

Source:
https://github.com/targetblank/micropython_ahtx0

2022-0326 PP new, not tested yet.

"""
import utime
from machine import Pin, I2C

import ahtx0

print("Simple test sensor AHTx0...")

# I2C for the Wemos D1 Mini with ESP8266
# i2c = I2C(scl=Pin(5), sda=Pin(4))
# I2C for the Pyboard-D
i2c = I2C(1)

# Create the sensor object using I2C
sensor = ahtx0.AHT10(i2c, 0x38)  # default I2C-address

while True:
    print("Temperature: {:0.2f} C".format(sensor.temperature), end=' ')
    print("Humidity: {:0.2f} %".format(sensor.relative_humidity))
    utime.sleep(5)
