"""
color_setup for 1.8" TFT-LCD display from WeActStudio
SPI, 128*160 pixels, ST7735

Nano-GUI driver: st7735r.st7735r144,
             or, st7735r.st7735r144_4bit

Connection schema
TFT-LCD  Pico-Grove Shield  Pyboard  DIP68
==================================================
GND      GND				  GND
VCC      3V3				  3V3
SCL      GPIO2 - SPI0-SCK	 'Y6'  	 W49 - SPI(2)
SDA      GPIO3 - SPI0-MOSI	 'Y8'    W57 - SPI(2)
RST      GPIO15				 'Y3'    W50
DC       GPIO14				 'Y1'    W54
CS       GPIO5				 'Y2'    W52
BL       GPIO17 - LOW		 'Y4'    W46

Note: SPI0 socket on Grove Shield could be used as an alternative.

2024_0413 PP: add display-dependend 'ssd' (ssd_st7735)
              to have multiple displays in nano-gui programs
2024-0220 PP: modified backligth pin for TFT-LCD power management
2024-0217 PP setup for Pyboard-SF2 on DIP68
2024-0217 PP setup for Raspberry PICO using nano-gui driver
             => colors are wrong (BLUE->RED, ..)
2024-0217 PP setup for Raspberry PICO using alistairhm-driver

"""
from micropython import const
from machine import Pin, SPI
import gc
from helpers import print_display_SPI_configuration

# TFT-display configuration
import config

# *** Choose your color display driver here ***

# distorted: from drivers.st7735r.st7735r import ST7735R as SSD
# OK, except colors:
from drivers.st7735r.st7735r144 import ST7735R as SSD
# OK, except colors: from drivers.st7735r.st7735r144_4bit import ST7735R as SSD
# distorted: from drivers.st7735r.st7735r_4bit import ST7735R as SSD


# SPI, pins - from Peter Hinch - 'setup_st7735r_pyb.py'
pdc  = Pin(config.DISPLAY_DC_PIN, Pin.OUT_PP, value=0)
pcs  = Pin(config.DISPLAY_CS_PIN, Pin.OUT_PP, value=1)
prst = Pin(config.DISPLAY_RESET_PIN, Pin.OUT_PP, value=1)
pbl  = Pin(config.DISPLAY_BL_PIN, Pin.OUT_PP, value=1) # BL is managed in driver
# Note: pbl LOW (pbl(0)) will turn TFT-display in WHITE screen.

spi = SPI(config.DISPLAY_SPI_ID, baudrate=config.DISPLAY_BAUDRATE)

gc.collect()  # Precaution before instantiating framebuf

# Create a display instance
# 2024-0220 PP: add backligth pin for TFT-LCD power management
ssd = SSD(spi,
          cs=pcs, dc=pdc, rst=prst, bl=pbl, 
          width=config.DISPLAY_TFT_WIDTH,
          height=config.DISPLAY_TFT_HEIGHT,  # landscape
          #width=config.DISPLAY_TFT_HEIGHT,
          #height=config.DISPLAY_TFT_WIDTH,  # portrait
          )

# 2024-0413 PP make a separate copy
ssd_st7735 = ssd

landscape = ssd.width > ssd.height
display_name = "1.8 TFT-LCD SPI, 128*160"
print_display_SPI_configuration(ssd, display_name, landscape=landscape)