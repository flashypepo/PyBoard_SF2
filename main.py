"""
main.py -- put your code here!

TODO: use pyRTOS or asyncio to use sensors concurrent.

2022-0525 PP WBUS-DIP68: power must be on. Test AHTx0 and SGP40
             SGP40: VOC index value is 0 al-the-time
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
import time
import gc
import uasyncio
from pyb import LED

# custom libraries ....
from tile_sensa import HDC2080, OPT3001, RGBLED
from tile_leds36 import TileLED36

# temperature sensor
from ahtx0 import AHT10
from sgp40 import SGP40
# import/setup algorithm only on use of index
#TODO: from voc_algorithm import VOCAlgorithm

# global signal color for LED36
color = (0, 255, 0)   # default color is GREEN


async def blink(led, freq=0.5):
    print("blink LED...", led)
    while True:
        led.toggle()
        await uasyncio.sleep(freq)


async def aht0x_measurement(ahtx0, freq=5):
    ''' measures AHTx0 temperature every freq seconds '''
    print(f"Simple test sensor AHTx0 every {freq} seconds...")
    while True:
        print("AHT0x: Temperature={:0.2f} C".format(ahtx0.temperature), end=' ')
        print("Humidity={:0.2f} %".format(ahtx0.relative_humidity))
        await uasyncio.sleep(freq)


async def sgp40_measurement(sgp40, ahtx0=None, freq=1):
    ''' measures SGP40 raw data every freq seconds '''
    print(f"Simple test sensor SGP40 every {freq} seconds...")
    while True:
        # read temperature & humidity from AHT0x sensor
        temperature = ahtx0.temperature
        humidity = ahtx0.relative_humidity
        measurement_raw = sgp40.measure_raw()
        #?? measurement_test = sgp40.measure_test()
        print("SGP40: Raw data={}".format(measurement_raw))
        #DEBUG: print("Raw data: {}".format(measurement_raw), end='\t\t')
        #DEBUG: print("Measurement test: {}".format(measurement_test))
        #DEBUG: print("\tTemperature: {:0.2f} C".format(temperature), end=' ')
        #DEBUG: print("\tHumidity: {:0.2f} %".format(humidity))

        # TODO: use lib.VOCAlgorithm
        # For Compensated voc index readings
        # The algorithm expects a 1 hertz sampling rate.
        # Run "measure index" once per second.
        # It may take several minutes for the VOC index to
        # start changing as it calibrates the baseline readings.

        await uasyncio.sleep(freq)

temperature_range = (20, 28)

async def tile_sensa_readings(hdc, opt, rgbled, freq=3):
    global color
    print(f"TileSensa measurements every {freq} seconds...")
    fmt = "TileSensa: Temperature={:2.2f}C, humidity={:2.2f}%, lux={:2.2f}"
    while True:
        rgbled.greenOn(False)
        rgbled.redOn()
        hdc.measure()
        opt.measure()
        while not opt.is_ready() and not hdc.is_ready():
            machine.idle()

        print(fmt.format(hdc.temperature(), hdc.humidity(), opt.lux()))
        time.sleep_ms(100) # to see red-led!
        rgbled.redOn(False)
        rgbled.greenOn()

        # 2022-0719 PP added signal color
        # default color is GREEN
        if hdc.temperature() < temperature_range[0]:
            color = (0, 0, 255)  # color BLUE
        elif hdc.temperature() > temperature_range[1]:
            color = (255, 0, 0)  # color RED

        await uasyncio.sleep(freq)


async def tile36_cycle(led36):
    """ Set all LEDs to black, red, green, yellow, blue, magenta, cayn
        and white for dt ms. ramp up brightnes from 0 % to 100 %
    """
    print("LED36: cycle...")
    #led36.cyc()
    dt = 250
    while True:
        try:
            led36.fill_rgb(100, 100, 100)
            for i in range(8):
                led36.fill_rgb((i & 1) * 255, ((i >> 1) & 1) * 255, ((i >> 2) & 1) * 255)
                await uasyncio.sleep_ms(dt)
            for i in range(100):
                led36.brightness(i)
                await uasyncio.sleep_ms(50)
        except:
            await uasyncio.sleep_ms(100)


async def tile36_pump(led36):
    global color
    print("LED36: pump brightness...")
    """ Cycle a color through brightness modulation """
    #led36.pump(cycles)
    led36.illu(color[0], color[1], color[2])
    import math
    sinar = []
    maxv = 100
    for i in range(90):
        sinar.append(int((math.sin(i * 4 / 180 * math.pi) + 1) * maxv / 2))
    i = count = 0
    cycles = 5
    dt = 10
    MAX_CYCLES = cycles*90
    while True:
        led36.brightness(sinar[i])
        i += 1
        i %= len(sinar)
        await uasyncio.sleep_ms(dt)
        count += 1
        if count >= MAX_CYCLES:
            i = count = 0


async def tile36_message(led36, msg):
    global color
    print("LED36: scrolling text...")
    #led36.set_text_color(0, 150, 0, 0, 0, 0)  # Green on black
    led36.set_text_color(color[0], color[1], color[2], 0, 0, 0)  # Color on BLACK
    led36.set_rot(2)  # vertical-flip
    led36.brightness(100)
    led36.text(msg)  # store text
    delay=50  # scrolling speed in ms
    while True:
        led36._i2c.writeto(1, b'\x01')
        await uasyncio.sleep_ms(delay)


async def tile36_randomdots(led36):
    """ Set random colors at random positions """
    print("LED36: random dots...")
    import pyb
    dt=10  # delay 10 ms
    while True:
        rn = pyb.rng()  # random number
        r = rn & 0xff   # specify RED
        g = (rn >> 8) & 0xff # specify GREEN
        b = (rn >> 16) & 0xff  # specify BLUE
        x = (rn >> 24) % 36  # specify x
        y = x // 6  # specify y
        x %= 6
        led36.set_dot(x, y, r, g, b)  # set dot at (x,y) in color (r,g,b)
        await uasyncio.sleep_ms(dt)


async def main():
    # generic configuration
    i2c = machine.I2C(1)

    # make a list of tasks
    tasks = []

    # -----------------------------
    # task: blinking LEDs
    # -----------------------------
    red, green, blue = LED(1), LED(2), LED(3)
    task = uasyncio.create_task(blink(red, 1))
    tasks.append(task)
    task = uasyncio.create_task(blink(green, 0.6))
    tasks.append(task)
    task = uasyncio.create_task(blink(blue, 0.3))
    tasks.append(task)

    # -----------------------------
    # task: AHTx0 temperature measurement
    # -----------------------------
    ahtx0 = AHT10(i2c, 0x38)  # default AHTx0 I2C-address
    freq = 5  # frequency of measurement in seconds
    task = uasyncio.create_task(aht0x_measurement(ahtx0, freq))
    tasks.append(task)

    # -----------------------------
    # task: SGP40 air quality measurements
    # -----------------------------
    sgp40 = SGP40(i2c, 0x59)
    freq = 10  # frequency of measurement in seconds
    task = uasyncio.create_task(sgp40_measurement(sgp40, ahtx0, freq))
    tasks.append(task)


    # -----------------------------
    # task: TileSensa measurements
    # -----------------------------
    rgbled = RGBLED()
    hdc = HDC2080()
    opt = OPT3001()
    freq=10   # frequency of measurement in seconds
    task = uasyncio.create_task(tile_sensa_readings(hdc, opt, rgbled, freq))
    tasks.append(task)

    # -----------------------------
    # task demo TileLED36
    # -----------------------------
    led36 = TileLED36()  # (i2c)
    led36.fill_rgb(0, 0, 0)  # clear LED36

    # select one of the following tasks...
    #task = uasyncio.create_task(tile36_cycle(led36))
    task = uasyncio.create_task(tile36_randomdots(led36))
    #task = uasyncio.create_task(tile36_message(led36, msg='Micropython is sooo cool.......'))
    #task = uasyncio.create_task(tile36_cycle(led36))
    #task = uasyncio.create_task(tile36_pump(led36))
    tasks.append(task)

    # TODO task: sensor values on OLED-display

    # TODO task: weatherstation
    #from getweather import weatherstation
    #weatherstation()

    # TODO task: neopixels animation
    #if USE_WS2812 is True:
    #    import demo_ws2812


    # collect tasks and go...
    await uasyncio.gather(*tasks)



if __name__ == '__main__':
    try:
        print('Pyboard demo...')
        uasyncio.run(main())
    except KeyboardInterrupt:
        print('User interrupted...!')
