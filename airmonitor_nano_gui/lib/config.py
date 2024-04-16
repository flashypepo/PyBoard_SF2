"""
config.py - configuration parameters

2024-0414 PP adopted for Pyboard-SF2 on Totem-Rack
2024-0412 PP added DISPLAY_ROTATE,
             change DISPLAY_ADDRESS for Lolin OLED-display,
             add Oled poweron times
             add STOP_BUTTON, LED
2024-0409 PP added DISPLAY_BAUDRATE
2024-0407 PP modifed for Waveshare RP2040-Tiny
2024-0321 PP adopted from Grinberg
Github: https://github.com/miguelgrinberg/micropython-pico-code/blob/main/chapter5/config.py.example
"""
from micropython import const
# import board specifics
import pyb as board

# Wifi credentials - see secrets.py

# Pyboard SF2
LED_RED   = board.LED(1)   # red LED for warnings and errors
LED_GREEN = board.LED(2)   # green LED for status
LED_BLUE  = board.LED(3)   # blue LED for status

# Tiles, if present
TILE_LED36_ADDR = const(0x3d)  #(61)  # Tile 36 leds

#TODO: Tile Sensa with lux sensor (OPT3001) and temp/humidity sensor (HDC2080)
# URL: https://pybd.io/hw/tile_sensa.html
TILE_SENSA_RGB_RED_PIN   = 'X2'
TILE_SENSA_RGB_GREEN_PIN = 'X3'
TILE_SENSA_RGB_BLUE_PIN  = 'X4'

# webhooks
WEBHOOK_URL   = None  # TODO: see source Grinberg

# display dimensions
DISPLAY_OLED_WIDTH   = const(128)
DISPLAY_OLED_HEIGHT  = const(64)
DISPLAY_OLED_ROTATE  = const(180)   # rotation of screen in degrees
#DISPLAY_ROTATE  = const(2)   # OLED-display on yellow standaard
DISPLAY_OLED_CONTRAST  = const(128) #(255)   # constrast screen 0..255

# OLED-display and sensors - I2C
DISPLAY_I2C_ID  = 'X'   # I2C id
DISPLAY_SDA_PIN = 'B9'
DISPLAY_SCL_PIN = 'B8'

# I2C addresses
DISPLAY_OLED_ADDRESS       = const(0x3C)  # OLED SSD1306
SENSOR_CO2_ADDRESS         = const(0x58)  # CO2 sensor SGP30
SENSOR_TEMPERATURE_ADDRESS = const(0x38)  # temperature sensor AHT10
TILE_SENSA_HDC2080_ADDRESS = const(0x40)  #(64)  # temperature/humidity sensor
TILE_SENSA_OPT3001_ADDRESS = const(0x44)  #(69)  # lux lightsensor

# TFT-display - SPI
DISPLAY_SPI_ID = 2  
DISPLAY_BAUDRATE = 12_000_000  # TFT display - 12 MHz
#DISPLAY_BAUDRATE = 20_000_000
#DISPLAY_MOSI_PIN = board.SPI0_MOSI  # MOSI
#DISPLAY_MISO_PIN = board.SPI0_MISO  # MISO
#DISPLAY_SCK_PIN  = board.SPI0_SCK   # SCK

# SPI display control pins
DISPLAY_DC_PIN    = 'Y1'
DISPLAY_CS_PIN    = 'Y2'
DISPLAY_RESET_PIN = 'Y3'
DISPLAY_BL_PIN    = 'Y4'  # backlight

# WeAct Studio TFT - ST7735
DISPLAY_TFT_WIDTH   = const(160)
DISPLAY_TFT_HEIGHT  = const(128)

# Power management
DISPLAY_ON_PERIODS   = [7, 12, 13, 16, 18, 22] # displays ON: 7-12, 13-16, 18-22

# SENSOR MEASUREMENT
FREQ_CO2_MEASUREMENT  = 1000   # delay in ms between airquality measurements
FREQ_TEMP_MEASUREMENT = 2000   # delay in ms between temperature measurements
