# color_setup.py Customise for your hardware config

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2020 Peter Hinch

# Demo of initialisation procedure designed to minimise risk of memory fail
# when instantiating the frame buffer. The aim is to do this as early as
# possible before importing other modules.

# 2024-0217 PP changed name 'setup_tft_st7735' to 'color_setup_st7735'
# 2023-0825 PP adopted for micropython-nano-gui
#           Tested on PYB-SF2 (i2c) and M5Stack SH1107 OLED-display

import gc


# ====================================================
# Display configuration (I've tested)
#TODO: USE_OLED_SSD1306   = False  # OLED-displays from Lolin 128*64
USE_OLED_SH1107    = True  # M5Stack OLED-display - 128*64
#TODO: USE_TFT_ILI93xx    = False  #TODO: setup TFT-RGB ili9341
#TODO: USE_EPAPER_SSD1680 = False  #TODO: ePaper WeActStudio 2.9"
USE_TFT_ST7735     = True   # 1.8" TFT-Display WeAct Studio

# *** Choose your color display driver here ***
# Kept as SSD to maintain compatability
# Precaution before instantiating framebuf
gc.collect()

# =========================================================
# SETUP for M5Stack, OLED-display. SH1107
# =========================================================
if USE_OLED_SH1107 is True:
    from color_setup_sh1107 import *
    
# =========================================================
#TODO: SETUP for 2.8" TFT-RGB, 240x320, ILI93**
# =========================================================
#if USE_TFT_ILI93xx is True:
#    from color_setup_ili93xx import *


# =========================================================
# SETUP for 1.8" TFT-LCD from WeAct Studio, ST7735, 128x160 - SPI
# =========================================================
if USE_TFT_ST7735 is True:
    from color_setup_st7735 import *

# ====================================================


# execute if main
if __name__ == "__main__":
    from time import sleep
    print("Quick demo display...")
    
    # local function
    def demo(dt=1):
        print("Demo display...")
        ssd.text("Demo display...", 0, 0, 2)
        ssd.show()
        time.sleep(dt*2)
        print("\twhite display...")
        ssd.fill(1)
        ssd.show()
        sleep(dt)
        print("\tdark display...")
        ssd.fill(0)
        ssd.show()
    # run quick demo
    demo(dt=2)
