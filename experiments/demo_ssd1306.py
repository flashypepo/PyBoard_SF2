"""
demo_ssd1306.py - a demonstration of the OLED display
driver SSD1306-I2C, 128*64 pixels

2022-0720 PP code from github micropython
"""
#from machine import I2C
from wbus_dip68 import WBUS_DIP68
import ssd1306

wbus68 = WBUS_DIP68()
i2c = wbus68.i2c()
# using default address 0x3C
# i2c = I2C('X')
display = ssd1306.SSD1306_I2C(128, 64, i2c)

# display text on display
display.text('Hello, World!', 0, 0, 1)
display.show()
