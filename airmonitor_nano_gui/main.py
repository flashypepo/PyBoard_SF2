"""
main.py -- execute modules on PYB-SF2, using various sensors and actuators
MCU: PYB-SF2 on Totem-Rack with various actuators, sensors and displays
Micropython: 'v1.22.1 on 2024-01-05', 'PYBD-SF2W with STM32F722IEK'
Note: mostly M5stack units
"""
# DEMO micropython nano-gui: environment values
#from asnano import run
# 2024-0413 PP: Clock on OLED, Air values on TFT
from asnano_oled_tft import run
run()  # execute
