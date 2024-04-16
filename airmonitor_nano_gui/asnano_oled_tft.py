"""
asnano.py: demo program for use of nanogui with uasyncio

#TODO: add config to abstract configuration parameters
#TODO: add standby/micropwer (Peter Hinch) instead of display OFF
#TODO: correct colors (RED->RED etc.) Requires GRB instead of RGB, but how?

2024-0415 PP: add class DateCal for date string, renamed uos -> os (micropython v1.20+)
2024_0414 PP: modified display_awake for *all* displays, remove display_oled_awake
2024-0413 PP: add Clock on M5Stack OLED-display (SH1107), add 'display' to widgets
2024-0221 PP: adopt meters and colors for TFT-display WeActStudio (ST7735)
2024-0220 PP: modified display_off(): ST7735 driver include poweroff and poweron
2024-0218 PP: adopted partially 1.8" WeActStudio TFT-LCD (ST7735)
2023-0826 PP: adopted for PYB-D SF2 and M5Stack OLED-display (SH1107)

Copyright (c) 2020 Peter Hinch
Released under the MIT License (MIT) - see LICENSE file
"""
# Initialise hardware and framebuf before importing modules.
from color_setup import ssd_sh1107  # Create an OLED display instance
from color_setup import ssd_st7735  # Create a TFT display instance
from gui.core.nanogui import refresh

import time
import uasyncio as asyncio
import pyb
import os
from machine import I2C

# Sensors and actuator drivers (nano-gui compabtible)
from adafruit_sgp30 import Adafruit_SGP30
import ahtx0
from tile_leds36 import TileLED36

# Airquality widgets
from gui.core.writer import CWriter
from gui.widgets.led import LED
from gui.widgets.meter import Meter

# Clock widgets
from gui.widgets.label import Label
from gui.widgets.dial import Dial, Pointer

# Fonts and colors
import gui.fonts.arial10 as arial10
import gui.fonts.font10 as font10
import gui.fonts.freesans20 as freesans20
from gui.core.colors import *

# Now import other modules
import cmath
# customization parameters
import config
# 2024-0415 use class DateCal from nano-gui for date string
from gui.extra.date import DateCal


# helper: built-in LEDs OFF
def leds_off():
    #print("leds_off() entered...")
    [pyb.LED(i).off() for i in range(1, 4)]

# 2024-0413 PP: initialise global 'ssd'
ssd = ssd_st7735       # Airquality screen
ssd_oled = ssd_sh1107  # Clock screen
# Initialise and clear displays
refresh(ssd_st7735)
refresh(ssd_sh1107) #, True)

i2c = None  # placeholder 2024-0216 added to clear Led36 tile

color = lambda v : RED if v > 0.7 else YELLOW if v > 0.5 else GREEN
txt = lambda v : 'ovr' if v > 0.7 else 'high' if v > 0.5 else 'ok'

mode = 0


# ===============
# Tasks
# ===============
async def aclock(display):
    print(f"Task: Clock on display: {display}")    
    uv = lambda phi : cmath.rect(1, phi)  # Return a unit vector of phase phi
    pi = cmath.pi
    days = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday',
            'Sunday')
    months = ('Jan', 'Feb', 'March', 'April', 'May', 'June', 'July',
              'Aug', 'Sept', 'Oct', 'Nov', 'Dec')
    # Instantiate CWriter
    CWriter.set_textpos(display, 0, 0)  # In case previous tests have altered it
    #PP modified: wri = CWriter(display, arial10, GREEN, BLACK)  # Report on fast mode. Or use verbose=False
    wri_dial = CWriter(display, arial10, GREEN, BLACK)  # Report on fast mode. Or use verbose=False
    wri_time = CWriter(display, font10, GREEN, BLACK)  # Report on fast mode. Or use verbose=False
    wri_dial.set_clip(True, True, False)
    wri_time.set_clip(True, True, False)

    # Instantiate displayable objects
    #PP: dial = Dial(wri, 2, 2, height = 75, ticks = 12, bdcolor=None, label=120, pip=False)  # Border in fg color
    #dial = Dial(wri, 2, 2, height = 48, ticks = 12,  # 128*64 display
    # 2024-0218 PP: relate height to width of display (experimental)
    h = display.width // 2 - 15
    dial = Dial(wri_dial, 2, 0, height=h, ticks=12,
                bdcolor=False, label=2, pip=False)  # no Border
    lbltim = Label(wri_time, 5, h+2, 35, fgcolor=YELLOW)
    hrs = Pointer(dial)
    mins = Pointer(dial)
    secs = Pointer(dial)

    hstart =  0 + 0.7j  # Pointer lengths and position at top
    mstart = 0 + 0.92j
    sstart = 0 + 0.92j
    
    while True:
        t = time.localtime()
        hrs.value(hstart * uv(-t[3]*pi/6 - t[4]*pi/360), YELLOW)
        mins.value(mstart * uv(-t[4] * pi/30), YELLOW)
        secs.value(sstart * uv(-t[5] * pi/30), RED)
        lbltim.value('{:02d}.{:02d}.{:02d}'.format(t[3], t[4], t[5]))
        # DEPRECATED: dial.text('{} {} {} {}'.format(days[t[6]], t[2], months[t[1] - 1], t[0]))
        cal = DateCal(t)
        dial.text(f"{cal.day_str} {cal.mday} {cal.month_str} {cal.year}")
        
        refresh(display)
        await asyncio.sleep(1)


# TASK: blink led only when display is ON
async def blink_on(led, freq=0.5):
    print(f"Task: when display is ON, blink {led} with frequence {freq} sec...")
    while True:
        if ssd.is_awake is True:
            led.toggle()
        else:
            led.off()
        await asyncio.sleep(freq)

# TASK: blink led only when display is OFF
async def blink_off(led, freq=0.5):
    print(f"Task: when display is OFF, blink {led} with frequence {freq} sec...")
    while True:
        # blink only when display is OFF
        if ssd.is_awake is False:
            led.toggle()
        else:
            led.off()
        await asyncio.sleep(freq)

# Task: setup a Meter, optional values from a sensor
# TODO: separate meter-tasks in task 'airquality' and task 'temperature/humidiy'
async def meter(display, n, x, text, t, sensor=None):
    """
    meter(display, n, x, text, t, sensor=None) - a template for a Meter to
    show sensor, or random values (if sensor is None)
    Parameters:
        @display: specifies display for a Meter
        @n     : [int], specifies values for a Meter, range 0..3
        @x     : [int] specifies column position of a Meter
        @text  : [String] specifies text of a Meter
        @t     : [number] specifies the cycle in seconds for updating values of a Meter
        @sensor: None | sensor-class: specifies an air quality sensor, can be None
    """
    global mode
    print(f"{display}: Meter {n} '{text}', refresh every {t//1000} secs.")
    #assert (n>0 and sensor is not None), "sensor must be present"
    #refresh(display) #, True)
    
    # 2023-0826 PP: some reference values:
    # TODO: put values in config.py
    # https://forum.smartcitizen.me/t/eco2-and-tvoc-reference-values/1200/6
    if n == 0: # random meter
        legend = ('0.0', '0.5', '1.0')
        oldMin, oldMax = 0, 1  # random minimum and maximum value
    elif n == 1: # eCO2
        legend = ('400', '800', '1200')
        oldMin, oldMax = 400, 1200  # eCO2 minimum and maximum value
    elif n == 2: # TVOC
        legend = ('0', '250', '500')
        oldMin, oldMax = 0, 500  # TVOC minimum and maximum value
    elif n == 3: # Temperature
        legend = ('10', '20', '30')
        oldMin, oldMax = 10, 30  # Temperature minimum and maximum value
    else:
        raise ValueError(f"Illegal value 'n':{n}")

    # define a writer for Meter widget
    CWriter.set_textpos(display, 0, 0)  # In case previous tests have altered it
    wri = CWriter(display, arial10, GREEN, BLACK, verbose=False)
    wri.set_clip(True, True, False)

    row = display.height  - 16 - wri.height  # row for LED
    hm = row - 10  # height for Meter
    m = Meter(wri, 5, x, height=hm,
              divisions=4, ptcolor=YELLOW,
              label=text, style=Meter.BAR, legends=legend)
    l = LED(wri, row, x, bdcolor=YELLOW, label='over')
    
    newMin, newMax = 0, 1  # level=panel range
    oldRange = (oldMax - oldMin)
    newRange = (newMax - newMin)
    
    while True:
        if sensor is not None:
            if n == 1:  # eCO2
                val, _ = sensor.iaq_measure()
                #if display.is_awake is False:
                #    print(f"eCO2: {val} ppm")
            elif n == 2:  # TVOC
                _, val = sensor.iaq_measure()
                #if display.is_awake is False:
                #    print(f"TVOC: {val} ppb")
            elif n == 3: # temperature
                val = sensor.temperature
                #if display.is_awake is False:
                #    print(f"Temperature: {val} Celsius")
            # map sensor value to level-range
            v = (((val - oldMin) * newRange) / oldRange) + newMin

        else:  # no sensor -> random values
            v = int.from_bytes(os.urandom(3),'little')/16777216
        
        # v exists and has a valid value [0..1]
        m.value(v, color(v))
        #l.color(color(v))
        l.text(txt(v), fgcolor=color(v))        
        refresh(display)
        await asyncio.sleep_ms(t)


# Task: flash RGBLeds
async def flash(n, t):
    rgbled = {1:"red", 2:"green", 3:"blue"}
    print(f"LED '{rgbled[n]}', toggle every {t/1000:0.1f} secs.")
    led = pyb.LED(n)
    while True:
        led.toggle()
        await asyncio.sleep_ms(t)


# Task: kill all tasks when USR-button is pressed
# regular mode to stop program, not Ctrl-C.
async def killer(tasks, displays):
    sw = pyb.Switch()
    while not sw():
        await asyncio.sleep_ms(100)
    print("USR button pressed", end="...")  # PP added
    for task in tasks:
        task.cancel()
    # PP added: clear screens
    for display in displays:
        display.fill(0)  # clear screen
        display.show()
    # PP added: clear LED36 tile
    fill_rgb(i2c, addr=61, r=0, g=0, b=0)
    print("Done!")  # PP added


# Task: display management: periodic display ON, otherwise display OFF
# usage: display_awake([ssd, ssd_oled], periods=[7, 12, 13, 17, 18, 22]))
async def display_awake(displays, periods, verbose=False):
    """
        displays are alternerend ON or OFF in list of periods
        Example:
        periods = [7, 12, 13, 17, 18, 22] (exact 6 numbers of hours!)
        means a display is: ON between 7-12, 13-17, 18-22 and OFF otherwise.
    """
    print(f"displays '{displays}' are ON between hours"
          + f" {periods[0]}-{periods[1]},"
          + f" {periods[2]}-{periods[3]}"
          + f" and {periods[4]}-{periods[5]}"
          + " and OFF otherwise...")
    assert len(periods) == 6, "Number of periods must be exactly 6"
    # assume display is ON
    on = True  # 2024-0413 modified: display.is_awake  # get current awake-state from display
    while True:
        ch = time.localtime()[3]  # get current hour
        if ch in range(periods[0], periods[1]):
            if verbose is True:
                print(f"period: {periods[0]}-{periods[1]}...")
            mustOn = True
        elif ch in range(periods[2], periods[3]):
            if verbose is True:
                print(f"period: {periods[2]}-{periods[3]}...")
            mustOn = True
        elif ch in range(periods[4], periods[5]):
            if verbose is True:
                print(f"period: {periods[4]}-{periods[5]}...")
            mustOn = True
        else:
            mustOn = False
        #print(f"mustOn: {mustOn}")
        if mustOn is True and on is False:
            # display must be ON, only when display is OFF
            for d in displays:
                d.poweron()  # power display ON
            on = True      # save state
            if verbose is True:
                print("display is ON")
        elif mustOn is False and on is True:
            # display must be OFF, only when display is ON
            for d in displays:
                d.poweroff()  # power display OFF
            on = False  # save state
            if verbose is True:
                print("display is OFF")
        else:  # do nothing
            pass
        # wait some secs for next check
        await asyncio.sleep(10)


# 2024-0211 helper for LED36 light patterns
# async def fill_rgb(addr, r, g, b):
# fill Led36 with color r, g, b
def fill_rgb(i2c, addr, r, g, b):
    """ Fill LED array using set pixel command """
    i2c.writeto(addr, b'\x02X\x00\x00')
    buf = bytearray(b'\x02A   ')
    buf[2] = r
    buf[3] = g
    buf[4] = b
    for i in range(36):
        i2c.writeto(addr, buf)

#Task: randsom dots on LED36 tile
async def random_dots(addr, i2c, b= 100, dt=10):
    """ Set random colors at random positions
        addr: tile i2c-address
        i2c : i2c bus
        b   : brigthness 0..100(?)
        dt  : delay in ms
    """
    import pyb
    
    # local helpers
    def brightness(addr, b=100):
        """ Set brigntness """
        ba = bytearray(b'\x02\x16 ')
        ba[-1] = b & 0xff
        i2c.writeto(addr, ba)

    def set_dot(addr, x, y, r, g, b):
        """ Set single LED color (r,g,b) at position (x, y)"""
        buf = bytearray(b'\x02X  ')
        buf[2] = x
        buf[3] = y
        i2c.writeto(addr, buf)

        buf = bytearray(b'\x02A   ')
        buf[2] = r
        buf[3] = g
        buf[4] = b
        i2c.writeto(addr, buf)

    brightness(addr, b)  # set brightness to b
    
    while True:
        # when display is OFF: clear LEDs
        if ssd.is_awake is False:
            fill_rgb(i2c, addr, 0, 0, 0)
        else:
            # display is ON - show pattern
            rn = pyb.rng()
            r = rn & 0xff
            g = (rn >> 8) & 0xff
            b = (rn >> 16) & 0xff
            x = (rn >> 24) % 36
            y = x // 6
            x %= 6
            set_dot(addr, x, y, r, g, b)
        #time.sleep_ms(dt)
        await asyncio.sleep_ms(dt)


# main entrey point
async def main():
    global i2c
    
    #2024-0221 PP: moved to helper: [pyb.LED(i).off() for i in range(1, 4)]  # all LEDs off
    leds_off()
    #i2c = I2C('X', freq=400000)     # create hardware I2c object
    i2c = I2C('X')     # create hardware I2c object
    aht10 = ahtx0.AHT10(i2c, 0x38)  # Temperature sensor
    sgp30 = Adafruit_SGP30(i2c)     # eCO2 - sensor
    print("SGP30 serial #", [hex(i) for i in sgp30.serial])
    # Initialize SGP-30 internal drift compensation algorithm.
    sgp30.iaq_init()
    # Wait 15 seconds for the SGP30 to properly initialize
    print("Waiting 15 seconds for SGP30 initialization.")
    ssd.text("Waiting for SGP30", 0, 0, 2)
    ssd.show()
    pyb.LED(1).on()  # RED led on
    time.sleep(15)   # 15 secs according to datasheet
    pyb.LED(1).off()  # RED led off
    ssd.fill(0)
    ssd.show()

    # TODO: asyncio version of Tile36 must be made first!!
    # 2024-0211 add class Tile36
    led36_addr = 61  # 60: default individual LED36 address
    # 2024-0211 PP: LED_ADDR modified
    #   LED36 default address conflicts with
    #   OLED-displays at 0x3c (60).
    #   Address was modified to 61 (0x3d).
    #led_tile = TileLED36(addr)
    #led_tile.brightness(10)  # low brightness
    """
    # initialozation of a tile pattern
    # Scrolling text...'
    # sample code from forum
    # https://forum.micropython.org/viewtopic.php?f=20&t=6272
    #TODO: led_tile.set_text_color(0, 150, 0)
    led_tile.set_rot(1)  # 2024-0211: Totem rack rotation
    led_tile.text('Micropython is sooo cool..')
    """

    # add tasks to be executed asynchronious!
    tasks = []
    # task: clock on OLED-display
    ssd_sh1107.contrast(config.DISPLAY_OLED_CONTRAST)  #PP: set OLED brightness
    tasks.append(asyncio.create_task(aclock(ssd_sh1107)))
    
    # task: display sensor values...
    tasks.append(asyncio.create_task(meter(ssd, 1, 2, 'eco2', 1000, sgp30)))
    tasks.append(asyncio.create_task(meter(ssd, 2, 50, 'voc', 1000, sgp30)))
    #tasks.append(asyncio.create_task(meter(ssd, 0, 98, 'bass', 1500, None)))
    tasks.append(asyncio.create_task(meter(ssd, 3, 98, 'temp', 2000, aht10)))
    
    # RGB leds tasks
    # 2024-0221 PP: blink(red) when display is OFF
    #				blink(green) when display is ON
    #tasks.append(asyncio.create_task(flash(1, 200)))  # RED led
    #tasks.append(asyncio.create_task(flash(2, 500)))  # GREEN led
    #tasks.append(asyncio.create_task(flash(3, 200)))  # BLUE led
    # select a built-in LED of Pyboard
    #led = pyb.LED(1)  # red
    #led = pyb.LED(2)  # green
    #led = pyb.LED(3)  # blue
    # Task: blink green LED when display is ON
    led = pyb.LED(2)
    tasks.append(asyncio.create_task(blink_on(led=led, freq=1)))

    # Task: blink red LED when display is OFF
    led = pyb.LED(1)
    tasks.append(asyncio.create_task(blink_off(led=led, freq=2)))
    
    # task: tile LED36 blinks in random pattern, just for fun!
    tasks.append(asyncio.create_task(random_dots(addr=led36_addr, i2c=i2c, b=10, dt=2)))
    #TODO requires asyncio Tile36
    #tasks.append(asyncio.create_task(led_tile.random_dots(dt=2)))
    # scrolling text - check initialization!
    #tasks.append(asyncio.create_task(led_tile.show()))
    
    # task: power management all displays
    periods = config.DISPLAY_ON_PERIODS #[7, 12, 13, 16, 18, 22] # ON: 7-12, 13-16, 18-22
    displays = [ssd, ssd_sh1107]
    tasks.append(asyncio.create_task(display_awake(displays, periods, verbose=False)))
    
    await killer(tasks, displays)

# 2024-0211 added main entry to execute...
def run():
    print("Press Pyboard's USR button to stop.")
    try:
        asyncio.run(main())
    finally:  # Reset uasyncio case of KeyboardInterrupt
        asyncio.new_event_loop()
        print('Run done!')
        #manual in REPL:
        # power_off()
        # blink(green, 0.5)


if __name__ == "__main__":
    run()