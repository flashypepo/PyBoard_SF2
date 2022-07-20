"""
main.py -- put your code here!

TODO: use pyRTOS or asyncio to use sensors concurrent.

2022-0719-20 PP experiments to add tile LED36, Logging, OLED-display (SSD1306, SH1107)
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
from tile_sensa import HDC2080_ADDRESS, OPT3001_ADDRESS
from tile_leds36 import TileLED36, LED_ADDR

# temperature sensor
from ahtx0 import AHT10
from sgp40 import SGP40
#TODO: import/setup algorithm only on use of index
#TODO: from voc_algorithm import VOCAlgorithm


# 2022-0720 PP added simple logger
# URL: https://github.com/Youkii-Chen/micropython-ulogger
from logger import logger as log

# OLED drivers SSD1306 or SH1107 (M5Stack)
# URL SH1107: https://github.com/nemart69/sh1107-micropython
#from ssd1306 import SSD1306_I2C
from sh1107 import SH1107_I2C

# shared data class for environment sensor values
from environment_shared_data import EnvironmentData


# ------------------------------------
#  OLED display to show sensor values
# ------------------------------------
async def show_sensordata(display, ip, env_data, freq=1):
    count = 0
    dx, dy = 5, 12
    # to spare OLED-display: toggle display OFF and ON
    # 0..300 (5min) -> display on
    # 300..900 (15min) -> display off
    # >900: display on and reset count
    limits = (0, 60, 120)  # 1 min display on, then off and after 2 min on again
    #limits = (0, 10, 20)  # test

    while True:
        # 2022-0720 Tile Sensa is taken as environment sensor values
        temp = env_data.temperature
        hum = env_data.humidity
        eco2 = env_data.eco2

        # show the differences in temperature and humidity of sensors
        ex_temp = env_data.ex_temperature
        ex_hum = env_data.ex_humidity
        log.debug(f"T(sensa)-T(external)={(temp - ex_temp):.1f} C, H(sensa)-H(external)={(hum - ex_hum):.1f}%RH", fn=__name__)

        if count in range(limits[0], limits[1]):
            display.fill(0)  # clear display
            display.text(ip, 0, 0, 1)
            display.text(f"Temp:{temp:.1f} C", dx, dy, 1)
            display.text(f"Hum :{hum:.1f} %RH", dx, 2*dy, 1)
            display.text(f"eCO2: {eco2}", dx, 3*dy, 1)
            #DEBUG: display.text(f"count: {count}", dx, 4*dy, 1)
            # show differences in sensorvalues
            display.text(f"DT={(temp-ex_temp):.1f} DH={(hum-ex_hum):.1f}", dx, 4*dy, 1)
            display.show()
        elif count in range(limits[1], limits[2]):
            display.poweroff()
            log.info("OLED-display is off...", fn=__name__)
        elif count > limits[2]:
            display.poweron()
            count = 0
        count += 1
        await uasyncio.sleep(freq)


async def show_header(display):
    from time import sleep
    display.fill(0)
    display.text('================', 0,  0, 1)
    display.text('  Pyboard demo  ', 0, 11, 1)
    display.text(f'{ip(wl)}', 0, 22, 1)
    display.text('================', 0, 33, 1)
    display.show()
    sleep(3)


# global signal color for LED36
color = (0, 255, 0)   # default color is GREEN

# -------------------------
#  PyBoard LEDs animations
# -------------------------
async def blink(led, freq=0.5):
    '''
        blink() - blink a Pyboard LED
        @param led - a particlur pytboard-led
        @param freq - blink frequency
    '''
    log.debug(f"blink {led}...", fn=__name__)
    while True:
        led.toggle()
        await uasyncio.sleep(freq)

# ----------------------------------
#  Air Quality SGP40 sensor readings
# ----------------------------------
async def sgp40_measurement(sgp40, env_data, env_sensor=None, freq=1):
    ''' measures SGP40 raw data every freq seconds '''
    log.debug(f"Sensor SGP40 measures every {freq} seconds...", fn=__name__)
    while True:
        # get temperature and humidiy if an env_sensor is connected
        # 2022-0720 PP not used yet.
        temperature = 0 if env_sensor is not None else env_sensor.temperature
        humidity = 0 if env_sensor is not None else env_sensor.relative_humidity

        measurement_raw = sgp40.measure_raw()
        #?? measurement_test = sgp40.measure_test()

        # store in shared data
        env_data.eco2 = measurement_raw

        # print values - debugging
        #print("SGP40: Raw data={}".format(measurement_raw))
        log.info(f"SGP40: raw data={measurement_raw}", fn=__name__)
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

# -----------------------------------------------------------
#  Environment sensor readings
# 2022-0720: values are to be overridden by TileSensa sensors
# -----------------------------------------------------------
async def aht0x_measurement(ahtx0, env_data, freq=5):
    ''' measures AHTx0 temperature every freq seconds '''
    log.debug(f"Sensor AHTx0 measures every {freq} seconds...", fn=__name__)
    fmt = "AHTx0: Temperature={:2.2f} C, humidity={:2.2f} %RH"

    while True:
        # get sensor values
        t = ahtx0.temperature
        h = ahtx0.relative_humidity

        # store in env_data
        env_data.ex_temperature = t
        env_data.ex_humidity = h

        # debugging
        log.info(fmt.format(t, h), fn=__name__)

        await uasyncio.sleep(freq)


# ----------------------
#  Tile SENSA measurements
# ----------------------
TEMPERATURE_RANGE = (20, 28)
async def tile_sensa_readings(hdc, opt, rgbled, env_data, freq=3):
    global color
    log.debug(f"TileSensa measurements every {freq} seconds...", fn=__name__)
    fmt = "TileSensa: Temperature={:2.2f}C, humidity={:2.2f}%, lux={:2.2f}"
    while True:
        # start measurement signal
        rgbled.greenOn(False)
        rgbled.redOn()

        # start sensor measurements
        hdc.measure()
        opt.measure()
        while not opt.is_ready() and not hdc.is_ready():
            machine.idle()

        # get sensor values
        hdc_temp = hdc.temperature()
        hdc_hum = hdc.humidity()
        ambient = opt.lux()
        # print sensor values in console ... debugging
        log.info(fmt.format(hdc_temp, hdc_hum, ambient), fn=__name__)

        # store sensor values
        # 2022-0720 PP Tile Sensa must be used -> overrides AHTx0 sensor values
        env_data.temperature = hdc_temp
        env_data.humidity = hdc_hum
        env_data.ambientlight = ambient

        time.sleep_ms(100) # to see red-led!
        # stop measurement signal
        rgbled.redOn(False)
        rgbled.greenOn()

        # 2022-0719 PP added signal color
        #              only used in some animations of LED36
        # default color is GREEN
        if hdc_temp < TEMPERATURE_RANGE[0]:
            color = (0, 0, 255)  # color BLUE
        elif hdc_temp > TEMPERATURE_RANGE[1]:
            color = (255, 0, 0)  # color RED

        await uasyncio.sleep(freq)

# ----------------------
#  Tile LED36 animations
# ----------------------
async def tile36_cycle(led36):
    """ Set all LEDs to black, red, green, yellow, blue, magenta, cayn
        and white for dt ms. ramp up brightnes from 0 % to 100 %
    """
    log.info("LED36: cycle...", fn=__name__)
    #print("LED36: cycle...")
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
    log.info("LED36: pump brightness ...", fn=__name__)
    #print("LED36: pump brightness...")
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
    #print("LED36: scrolling text...")
    log.info("LED36: scrolling text ...", fn=__name__)

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
    #print("LED36: random dots...")
    log.info("LED36: random dots ...", fn=__name__)

    #import pyb
    from pyb import rng
    dt=10  # delay 10 ms
    while True:
        rn = rng()  #pyb.rng()  # random number
        r = rn & 0xff   # specify RED
        g = (rn >> 8) & 0xff # specify GREEN
        b = (rn >> 16) & 0xff  # specify BLUE
        x = (rn >> 24) % 36  # specify x
        y = x // 6  # specify y
        x %= 6
        led36.set_dot(x, y, r, g, b)  # set dot at (x,y) in color (r,g,b)
        await uasyncio.sleep_ms(dt)


"""
# 2022-0720 using neopixels with asynio does not work!
# will try with pyrtos in-future

from demo_ws2812 import stick, solidColors, randomLevel, randomColors, clear
from pyb import rng
async def run(freq=1000):
    level = stick.led_count
    log.debug(f"Neopixel demo...{level} neopixels", fn=__name__)

    mask = 0x3
    while True:
        demo = (rng() & mask)  # random demo
        if demo == 0:
            print(f"Demo.. {demo}")
            data = solidColors()  # solid colors
        elif demo == 1:
            print(f"Demo.. {demo}")
            data = randomColors(stick.led_count) # random colors
        elif demo == 2:
            print(f"Demo.. {demo}")
            data = randomLevel()  # random level and random colors
        else:
            data = randomColors(stick.led_count) # random colors

        # DEBUG: print('data:', data)
        stick.show(data)
        await uasyncio.sleep_ms(freq)
        #pyb.delay(wait)
        #clear()
        #pyb.delay(wait // 4)
"""


async def main(i2c, display, led36):
    # generate a shared data object for environment data
    env_data = EnvironmentData()

    # make a list of tasks
    tasks = []

    # -----------------------------
    # task: blinking Pyboard-LEDs
    # -----------------------------
    log.info("task: blinking Pyboard-LEDS ...", fn=__name__)
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
    freq = 5  # frequency of measurement in seconds
    AHT10_ADDRESS = const(0x38)
    log.info(f"task: AHTx0-sensor, I2C-address={hex(AHT10_ADDRESS)}({AHT10_ADDRESS}), every {freq} secs", fn=__name__)
    ahtx0 = AHT10(i2c, AHT10_ADDRESS)  # use default AHTx0 I2C-address
    task = uasyncio.create_task(aht0x_measurement(ahtx0, env_data, freq))
    tasks.append(task)

    # -----------------------------
    # task: SGP40 air quality measurements
    # -----------------------------
    freq = 10  # frequency of measurement in seconds
    SGP40_ADDRESS = const(0x59)
    log.info(f"task: SGP40-sensor, I2C-address={hex(SGP40_ADDRESS)}({SGP40_ADDRESS}), every {freq} secs", fn=__name__)
    sgp40 = SGP40(i2c, SGP40_ADDRESS)
    task = uasyncio.create_task(sgp40_measurement(sgp40, env_data, ahtx0, freq))
    tasks.append(task)


    # -----------------------------
    # task: TileSensa measurements
    # -----------------------------
    freq=10   # frequency of measurement in seconds
    log.info(f"task: HDC2080 sensor, I2C-address={hex(HDC2080_ADDRESS)}({HDC2080_ADDRESS}), every {freq} secs", fn=__name__)
    log.info(f"task: OPT3001 sensor, I2C-address={hex(OPT3001_ADDRESS)}({OPT3001_ADDRESS}), every {freq} secs", fn=__name__)
    rgbled = RGBLED()
    hdc = HDC2080()
    opt = OPT3001()
    task = uasyncio.create_task(tile_sensa_readings(hdc, opt, rgbled, env_data, freq))
    tasks.append(task)

    # -----------------------------
    # task demo TileLED36
    # -----------------------------
    led36.fill_rgb(0, 0, 0)  # clear LED36

    # select one of the following tasks...
    #task = uasyncio.create_task(tile36_cycle(led36))
    task = uasyncio.create_task(tile36_randomdots(led36))
    #task = uasyncio.create_task(tile36_message(led36, msg='Micropython is sooo cool.......'))
    #task = uasyncio.create_task(tile36_cycle(led36))
    #task = uasyncio.create_task(tile36_pump(led36))
    tasks.append(task)

    # TODO task: sensor values on OLED-display
    # 2022-0720 PP tile LEDS36 has another i2c-address, so OLED should work

    # TODO task: weatherstation
    #from getweather import weatherstation
    #weatherstation()

    # -----------------------------
    # task: Neopixel animations
    # -----------------------------
    # 2022-0720 using neopixels with asynio seems not work!
    #           I''ll try with pyrtos in-future
    """
    freq=2000   # frequency of measurement in seconds
    log.info(f"task: Neostick, SPI, every {freq/1000} secs", fn=__name__)
    task = uasyncio.create_task(run(freq))
    tasks.append(task)
    """

    # -----------------------------
    # task: Title on OLED
    # -----------------------------
    task = uasyncio.create_task(show_header(display))
    tasks.append(task)


    # -----------------------------------
    # task: sensor values on OLED-display
    # -----------------------------------
    SSD1306_ADDRESS = 0x3c
    freq= 1
    log.info(f"task: OLED display, I2C-address {SSD1306_ADDRESS}, refresh every {freq} second", fn=__name__)
    task = uasyncio.create_task(show_sensordata(display, ip(wl), env_data, freq))
    tasks.append(task)

    # collect tasks and go...
    await uasyncio.gather(*tasks)

# main: create i2c, display and led36, so I can clean them up in exception
# 2022-0720 try...except does not work in main() itself
if __name__ == '__main__':
    try:
        print('====================')
        print('  Pyboard-SF2 demo  ')
        print('====================')
        # generic configuration
        i2c = machine.I2C(1)
        #or: i2c = machine.I2C('X')
        log.info(f"I2C scan: {i2c.scan()}", fn=__name__)

        # create a display from OLED-display SSD1306
        #SSD1306: display = SSD1306_I2C(128, 64, i2c)
        #SSD1306: display.rotate(180)  # SH1107: not implemented yet
        display = SH1107_I2C(128, 64, i2c)   # works!

        LED36_ADDRESS = const(61)   # hex: 0x3D
        log.info(f"task: LED36 bling-bling, I2C-address={hex(LED36_ADDRESS)}({LED36_ADDRESS})", fn=__name__)
        #led36 = TileLED36(address=LED_ADDR)  # default I2C address
        led36 = TileLED36(address=LED36_ADDRESS)  # provide new I2C address
        # 2022-0720 PP changing I2C-address to 0x3D (61) requires reset of the pyboard
        #              which was done after a first test. Current I2C-address is LED36_ADDRESS!
        # NOT DONE: change LED_ADDRESS in tile_leds36.py into new address - requires sourcecode change!
        # NOT TESTED: toggle power line Pin("EN_3V3") should also help - see tile_leds36.py

        # go...
        uasyncio.run(main(i2c, display, led36))

    except KeyboardInterrupt:
        print('User interrupted...!', end=' ')
        led36.fill_rgb(0,0,0)  # clear LED36
        display.fill(0)  # clear OLED
        display.show()
        print('Done!')
