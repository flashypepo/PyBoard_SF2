# -*- coding: utf-8 -*-
"""
 demo_ws2812 - simple demo of an 8-stick Neopixel

 Configuration:
 DIN = SPI(1) - MOSI (X8)  - WBUS128: W14
 Vcc = 5V
 GND = GND

 Usage:
     from demo_ws2812 import run
    run()

 2020-1222 PP adopted from demo_simple.py.
 TODO: Pixels behave sometime odd, and seems not to be combined with main

"""
try:
    import pyb
except ImportError:
    import machine as pyb

from ws2812 import WS2812

NEOPIXELS = 8  # 8-stick Neopixels
#NEOPIXELS = 16  # 2nd 8-stick connected - test DOUT
INTENSITY = 0.2  # brightness level

# create neopixel-object
stick = WS2812(spi_bus=1, led_count=NEOPIXELS, intensity=INTENSITY)


# returns some fixed solid colors
def solidColors():
    return [
        (24, 0, 0),     # red
        (0, 24, 0),     # green
        (0, 0, 24),     # blue
        (12, 12, 0),    # yellow
        (0, 12, 12),    # blueish
        (12, 0, 12),    # purple
        (24, 0, 0),     # red
        (21, 21, 21),   # white
    ]


# random colors
def randomColors(level):
    # fill data up to level with random numbers
    mask = 0xff
    data = [( (pyb.rng() & mask),
              ((pyb.rng() >> 8) & mask),
              ((pyb.rng() >> 16) & mask)
            ) for i in range(level)]
    return data

# fill data until random level with random color
# simulation of a VU-meter or similar...
def randomLevel():
    level = ((pyb.rng() >> 8) & 0x07) + 1
    # DEBUG: print('level:', level)
    return randomColors(level)


def clear():
    data = [(0, 0, 0) for i in range(stick.led_count)]
    stick.show(data)


# main program
def run(wait=1000):
    try:
        print("Neopixel demo...", stick.led_count, "neopixels")
        mask = 0x3
        while True:
            i = (pyb.rng() & mask)  # random demo
            if i == 0:
                print(f"Demo.. {i}")
                data = solidColors()  # solid colors
            elif i == 1:
                print(f"Demo.. {i}")
                data = randomColors(stick.led_count) # random colors
            elif i == 2:
                print(f"Demo.. {i}")
                data = randomLevel()  # random level and random colors
            else:
                data = randomColors(stick.led_count) # random colors

            # DEBUG: print('data:', data)
            stick.show(data)
            pyb.delay(wait)
            #clear()
            #pyb.delay(wait // 4)
    #except Exception as ex:
    #    print(ex)
    #    pass
    except KeyboardInterrupt:
        clear()
        print('Interrupted!')
        pass

def demo_solidcolors(wait=1000):
    try:
        print(f"Demo solid colors for {stick.led_count} neopixels...")
        while True:
            data = solidColors()  # solid colors

            stick.show(data)

            pyb.delay(wait)
            clear()
            pyb.delay(wait // 4)

    except KeyboardInterrupt:
        clear()
        print('Interrupted!')
        pass


def demo_randomcolors(wait=1000):
    try:
        print(f"Demo random colors for {stick.led_count} neopixels...")
        while True:
            data = randomColors(stick.led_count) # random colors
            stick.show(data)
            pyb.delay(wait)
            clear()
            pyb.delay(wait // 4)
    except KeyboardInterrupt:
        clear()
        print('Interrupted!')
        pass

def demo_randomlevelcolors(wait=1000):
    try:
        print(f"Demo random colors for random number of neopixels...")
        while True:
            data = randomLevel()  # random level and random colors
            stick.show(data)

            pyb.delay(wait)
            clear()
            pyb.delay(wait // 4)

    except KeyboardInterrupt:
        clear()
        print('Interrupted!')
        pass


if __name__ == "__main__":
    print("Demo started...")
    run()
    print('Demo done!')
