"""
nano-gui setup for SH1107 OLED-display, like M5Stack OLED

MCU: Pyboard-SF2

2024-0414 PP: added config and helper print_i2c_devices
2024_0413 PP: add display-dependend 'ssd' (ssd_sh1107)
              to have multiple displays in nano-gui programs
2024-0217 PP modified for Pyboard-SF2 (STM32F722)
"""
from machine import I2C
import sh1107
from sh1107 import SH1107_I2C as SSD

from helpers import print_display_I2C_configuration
from helpers import print_i2c_devices

# OLED display configutation
import config


# I2C configuration
#freq not required: i2c = I2C('X', freq=400000) # create hardware I2c object
i2c = I2C(config.DISPLAY_I2C_ID) # create hardware I2c object
print_i2c_devices(i2c)  # for debugging
# 2024-0414 PP moved to helpers
#devices = i2c.scan()
#print(f"I2C devices: {[hex(d) for d in devices]}")
#print(f"-"*10)

# create a display for SH1107 OLED-display, such M5Stack OLED-display
# Kept as ssd to maintain compatability
# For SH1107 required: framebuf2 is loaded
assert (config.DISPLAY_OLED_ADDRESS in i2c.scan()), "SH1107 OLED-display is not connected"
assert (sh1107._fb_variant == 2), "Library framebuf2 is not loaded"
ssd = SSD(config.DISPLAY_OLED_WIDTH,
          config.DISPLAY_OLED_HEIGHT,
          i2c, address=config.DISPLAY_OLED_ADDRESS,
          rotate=config.DISPLAY_OLED_ROTATE)  # display instance

# 2024-0413 PP make a separate copy
ssd_sh1107 = ssd

# display ssd configuration
display_name = "SH1107 OLED-shield 128*64"
print_display_I2C_configuration(ssd_sh1107, display_name)
