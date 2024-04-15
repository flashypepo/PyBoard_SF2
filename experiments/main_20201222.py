"""
main.py -- put your code here!

2002-0512 PP added demo from tile_sensa
2020-0504 PP new. collected some demos
"""
import gc

from pyb import Timer, LED

from tile_leds36 import TileLED36
from tile_sensa import demo


# blinking LED from https://forum.micropython.org/viewtopic.php?f=20&t=6943
# LED(2).intensity(0)  #0=off, 1=on
timer = Timer(14, callback=lambda x: LED(2).toggle(), freq=0.5)

led36 = TileLED36()  # (i2c)


def demoTile():
    # Tile-LED example
    print('LED matrix...')
    #led36 = TileLED36()  # (i2c)
    try:
        led36.random_dots()     
    except KeyboardInterrupt:
        led36.fill_rgb(0, 50, 0)  # green
        pass


def demoSensaTile():
    # Tile-Sensa example
    print('Sensa tile...')
    demo(delay=10)


if __name__ == '__main__':
    try:
        demoTile()
        demoSensaTile()

    except KeyboardInterrupt:
        led36.fill_rgb(0, 0, 0)  # blank leds
        pass

    finally:
        print('Demo done!')
        gc.collect()
        print("Memory available: {} kB".format(gc.mem_free() // 1024))
