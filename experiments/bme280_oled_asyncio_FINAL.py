"""
bme280_oled_asyncio_FINAL -
Python code to measure environment data with sensor BME280,
using some LEDs for signalling and display sensor values 
on an local OLED using asyncio.

A solution for exercise: implement concurrency with asyncio

Configuratie:
1x BME680/BME280 sensor, i2c
1x OLED, ssd1306, 128*64 pixels, i2c
2x LEDs on various GPIO's

2022-0508 PP A solution for asyncio exercise (workshop 8 - concurrency)
2022-0503 PP use BME280 sensor, added LED configuration
2021-1130 PP setup, reuse code from weatherstation (workshop 5)
"""
import asyncio
import math
import logging
import os

# Adafruit libraries
import lib.blinka_pkg_check
import board
from busio import I2C
from digitalio import DigitalInOut

# configure logging
log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
#log.level = logging.WARNING  # for production
log.level = logging.INFO  # for testing and demo

# Sensor configuration
# and load appropriate libraries
USE_BME680 = False  # 2022-0503 PP modified
USE_BME280 = not USE_BME680
if USE_BME280 is True:
    from adafruit_bme280 import basic as adafruit_bme280
if USE_BME680 is True:
    import adafruit_bme680

# re-use library from weatherstation
# 2021-1130 PP small changes were made - see file ./lib/bmex80view.py
from lib.oledview import OLEDView

# shared data class for environment sensor values
from lib.environment_shared_data import EnvironmentData

# LED configuration
RED = board.D21
BLUE = board.D20
GREEN = board.D16
YELLOW = board.D12

# ------------
# define tasks
# ------------
# task to monitor the BMEx80
async def monitor_environmentdata(bmex80, env_data, pin, interval=2):
    """
        Monitor BMEx80 readings.
        Update env_data every interval seconds
        LED on pin ON when a measurement is made, else OFF
    """
    env_data.sensor = "BME280" if USE_BME280 else "BME680"
    # create a signal LED
    led = DigitalInOut(pin)
    led.switch_to_output(value=False)
    while True:
        log.debug(f"{env_data.sensor} new measurement...")  # debug
        # set LED on
        led.value = True
        t = env_data.temperature = bmex80.temperature
        # tmpF = (t * 1.8) + 32   # Fahrenheit
        h = env_data.humidity = bmex80.humidity
        env_data.pressure = bmex80.pressure
        env_data.altitude = bmex80.altitude
        # You can use the BME280 temperature and humidity
        # to calculate the dew point using the Magnus
        # formula.
        # source: https://learn.adafruit.com/adafruit-bme280-humidity-barometric-pressure-temperature-sensor-breakout/python-circuitpython-test
        # constants for dew point calculation:
        b = 17.62
        c = 243.12
        # dew point calculation using the Magnus formula
        # (https://en.wikipedia.org/wiki/Dew_point#Calculating_the_dew_point)
        gamma = (b * t / (c + t)) + math.log(h / 100.0)
        dewpoint = (c * gamma) / (b - gamma)
        env_data.dewpoint = dewpoint
        # BME680: 
        # env_data.gas=bmex80.gas
        # Let another task run.
        # set LED on
        led.value = False
        await asyncio.sleep(interval)


# task to display sensor data on OLED
async def showdata(oled, env_data, rate=10):
    """
        Show the sensor data in env_data on OLED.
        Refresh every rate second."""
    while True:
        log.debug("OLED update...")
        # display sensor data on oled
        data = {
            "Sensor": f"{env_data.sensor}",
            "Temp": f"{env_data.temperature:0.1f} \u00b0C",
            "Hum": f"{env_data.humidity:0.1f} %",
            "Pres": f"{env_data.pressure:0.2f} hPa",
            #"Alt": f"{env_data.altitude:0.2f} m",
            "Dew": f"{env_data.dewpoint:0.2f}",
        }
        #if USE_BME680 is True:
        #    data.update(Gas = "{:0.2f} Ohms".format(self._model.gas))
        # show sensor data on display...
        oled.show(data, showTopline=True)
        # Let another task run.
        await asyncio.sleep(rate)

# task to blink LED
async def blink_unending(pin, interval):
    with DigitalInOut(pin) as led:
        led.switch_to_output(value=False)
        while True:
            led.value = True
            await asyncio.sleep(interval)  # Don't forget the await!
            led.value = False
            await asyncio.sleep(interval)  # Don't forget the await!

# ------------
# Main program
# ------------

display = None  # global display object
async def main():
    global display
    # Create I2C object using our Bus I2C port
    i2c = I2C(board.SCL, board.SDA)

    # create sensor BMEx80 object
    name_sensor = "BME280" if USE_BME280 is True else "BME680"
    log.info(f"\tcreate sensor model... {name_sensor}")
    if USE_BME280 is True:
        bmex80 = adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x76)
    if USE_BME680 is True:
        bmex80 = adafruit_bme680.Adafruit_BME680_I2C(i2c, 0x77)
    # calibrate for altitude ... sealevel pressure
    # location's pressure (hPa) at sea level from:
    # https://www.weatheronline.co.uk/weather/maps/current?LANG=en&CONT=euro&REGION=0003&LAND=NL&LEVEL=4&R=310&CEL=C&ART=tabelle&TYP=druck
    # EXERCISE
    sea_level_pressure = 1020  # 2022-0503 15:00 at A'dam-Schiphol
    bmex80.sea_level_pressure = sea_level_pressure
    log.info(f"\tsea level pressure: {sea_level_pressure} hPa")

    # create OLED display object
    # 2022-0503 PP rotate display 180 degrees
    rotate = 0  # 0: default, 1:90, 2:180, 3:270 degree
    display = OLEDView(i2c, rotation=rotate)

    # create shared data object for sensor data
    env_data = EnvironmentData()
    env_data.sea_level_pressure = sea_level_pressure

    # task: monitor BMEx80 sensor
    rate = 2  # measurement interval in seconds
    log.info(f"Task sensor monitoring, refresh every {rate} second(s)... ")
    sensor_task = asyncio.create_task(
        monitor_environmentdata(bmex80, env_data,
                                pin=RED, interval=rate)
        )

    # task: display sensor data on OLED
    rate = 1   # refresh OLED every rate seconds
    log.info(f"Task OLED display, refresh every {rate} second(s) ...")
    display_task = asyncio.create_task(
        showdata(display, env_data, rate)
        )

    # task: blink a LED indicating activity
    led = GREEN
    rate = 0.5  # blink LED interval in seconds
    log.info(f"Task blinking LED{led}, every {rate} second(s)...")
    led_task = asyncio.create_task(blink_unending(led, rate))

    # This will run forever, because neither task ever exits.
    log.info("Tasks running... ")
    await asyncio.gather(sensor_task, display_task, led_task)

# execute main
if __name__ == "__main__":
    try:
        print("DEMO - show environment data on OLED display using asyncio...")
        asyncio.run(main())
    except KeyboardInterrupt:
        display.clear(refresh=True)
        log.info('Done')
