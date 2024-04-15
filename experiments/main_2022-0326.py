"""
main.py -- put your code here!

2020-1224 PP mind the order of execution: added Sensa-tile after neopixels
             - that works
    Note: Running Neopixels after Sensa-tile without a hard-reset
          does not work correctly!! Bright white LED(s).
    TODO: SPI problem? Maybe use SPI2 - DIN = Pin('Y8')?
2020-1222 PP added WS2812 - neopixel demo, added USE-flags
TODO: when Sensa-Tile is used, neopixels behave odd (no colors/bright white color)
2020-0512 PP added demo from tile_sensa
2020-0504 PP new. collected some demos
"""
import gc

USE_AHTx0 = False   # 2022-0326 PP added
USE_SGP40 = False  # 2022-0326 PP added
USE_LED = False
USE_TILE_LEDS36 = True   # 2022-0326 / 2021-0525 PP modified
USE_TILE_SENSA = False
USE_WS2812 = False
USE_WEATHERSTATION = False  # 2022-0326 / 2021-1025 PP added

# 2022-0326 PP added
if USE_AHTx0 is True:
    from test_ahtx0 import simple_test
    simple_test(dt=1)

# 2022-0326 PP added
if USE_SGP40 is True:
    from test_sgp40 import simple_test, index_test
    #simple_test(dt=1)
    index_test(dt=1)


if USE_LED is True:
    from pyb import Timer, LED

    # blinking LED from https://forum.micropython.org/viewtopic.php?f=20&t=6943
    # LED(2).intensity(0)  #0=off, 1=on
    timer = Timer(14, callback=lambda x: LED(2).toggle(), freq=0.5)
    #timer = Timer(14, callback=lambda x: LED(2).toggle(), freq=10)


if USE_TILE_LEDS36 is True:
    from tile_leds36 import TileLED36

    led36 = TileLED36()  # (i2c)

    def demoTile():
        # Tile-LED example
        print('LED36 tile...')
        try:
            print("\tcycle...")
            led36.cyc()
            c= 10
            print("\tpump...{} cycles".format(c))
            led36.pump(cycles=5)
            print("\tscrolling text...")
            led36.set_text_color(0, 150, 0, 0, 0, 0)  # Green on black
            led36.set_rot(2)  # vertical-flip
            led36.brightness(100)
            led36.text('Micropython is sooo cool..')
            led36.show()  # loop fixed number
            print("\trandom dots...")
            led36.random_dots()
        except KeyboardInterrupt:
            print('LED36-tile interrupted!')
            # led36.fill_rgb(0, 50, 0)  # green
            led36.fill_rgb(0, 0, 0)  # blank leds
            pass


if USE_TILE_SENSA is True:
    from tile_sensa import demo

    def demoSensaTile():
        # Tile-Sensa example
        print('Sensa tile...')
        try:
            demo(delay=10)
        except KeyboardInterrupt:
            print('Sensa-tile interrupted!')
            pass


if USE_WS2812 is True:
    import demo_ws2812


if USE_WEATHERSTATION is True:
    from getweather import weatherstation
    weatherstation()


if __name__ == '__main__':
    try:
        print('LEDS36 demo...', USE_TILE_LEDS36)
        if USE_TILE_LEDS36 is True:
            demoTile()

        print('WS2812 demo...', USE_WS2812)
        if USE_WS2812 is True:
            demo_ws2812.run(100)

        # 2020-1224 Sensa after neopixels, else no colors/bright white lights
        print('TILE_SENSA demo...', USE_TILE_SENSA)
        if USE_TILE_SENSA is True:
            demoSensaTile()

    except KeyboardInterrupt:
        print('Demo interrupted!')

