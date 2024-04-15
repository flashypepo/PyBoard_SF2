"""
simple test with SGP40 library from [Agners]

The SGP40 is a Metal Oxide (MOx) based multi-pixel gas sensor
which is sensitive to almost all Volatile Organic Compunds (VOCs).
It features on-chip processing for temperature and humidity
compensation. The signal is proportional to the logarithm of
the sensing material's resistivity.

Sensirion also provides an algorithm to convert the raw signal
to a VOC index as a robust measure for indoor air quality (IAQ).


Wiring
Wire the I2C bus to the I2C bus on your MicroPython board.
This is an example using the Pyboard D:

Pyboard     SGP40
X15 (3V3)   VDD
X14 (GND)   GND
X9	        SCL
X10	        SDA

Usage
This example reads the measurements in a continous loop.

[Agners]: https://github.com/agners/micropython-sgp40
2022-0326 PP new
"""
import time
from machine import I2C
# air quality sensor
from sgp40 import SGP40
# temperature sensor
from ahtx0 import AHT10
# import/setup algorithm only on use of index
from voc_algorithm import VOCAlgorithm


# 2022-0326 PP from https://github.com/adafruit/Adafruit_CircuitPython_SGP40
# def measure_index(self, temperature=25, relative_humidity=50):
def measure_index(measure_raw, temperature=25, relative_humidity=50):
    '''
        Measure VOC index after humidity compensation
        :param float temperature: The temperature in degrees Celsius, defaults to :const:`25`
        :param float relative_humidity: The relative humidity in percentage, defaults to :const:`50`
        :note  VOC index can indicate the quality of the air directly.
        The larger the value, the worse the air quality.
        :note 0-100, no need to ventilate, purify
        :note 100-200, no need to ventilate, purify
        :note 200-400, ventilate, purify
        :note 400-500, ventilate, purify intensely
        :return int The VOC index measured, ranged from 0 to 500
        '''
    print("Raw data: {} C".format(measure_raw), end='\t')
    print("Temperature: {:0.2f} C".format(temperature), end='\t')
    print("Humidity: {:0.2f} %".format(relative_humidity))

    voc_algorithm = VOCAlgorithm()
    voc_algorithm.vocalgorithm_init()

    # 2022-0326 ???: raw = self.measure_raw(temperature, relative_humidity)
    raw = measure_raw
    if raw < 0:
        return -1
    voc_index = voc_algorithm.vocalgorithm_process(raw)
    return voc_index

def index_test(dt=1):
    '''
        read temperature & humidity
        For Compensated voc index readings

        The VOC algorithm expects a 1 hertz sampling rate.
        Run "measure index" once per second.
        It may take several minutes for the VOC index to
        start changing as it calibrates the baseline readings.
    '''
    # setup
    print("Test VOC index from sensor SGP40...")
    i2c = I2C(1)
    ahtx0 = AHT10(i2c, 0x38)  # default I2C-address
    sgp40 = SGP40(i2c, 0x59)
    #time.sleep(15)
    # loop
    while True:
        # read temperature & humidity
        temperature = ahtx0.temperature
        humidity = ahtx0.relative_humidity
        #print("Temperature: {:0.2f} C".format(temperature), end='\t')
        #print("Humidity: {:0.2f} %".format(humidity))

        measurement_raw = sgp40.measure_raw()
        #print("Raw data: {}".format(measurement_raw), end='\t\t')
        #measurement_test = sgp40.measure_test()
        #print("Measurement test: {}".format(measurement_test))

        # For Compensated voc index readings
        # The algorithm expects a 1 hertz sampling rate.
        # Run "measure index" once per second.
        # It may take several minutes for the VOC index to
        # start changing as it calibrates the baseline readings.
        voc_index = measure_index(
            measure_raw=measurement_raw,
            temperature=temperature,
            relative_humidity=humidity
        )
        print("VOC index: {}".format(voc_index))

        time.sleep(dt)

def simple_test(dt=1):
    '''
        simple_test() returns raw data from the sensor every dt secs.
        The data is meant to be processed by the Sensirion specific
        VOC Algorithm, which returns air quality reflected by an index.
    '''
    # setup
    print("Simple test sensor SGP40")
    i2c = I2C(1)
    sgp40 = SGP40(i2c, 0x59)
    #time.sleep(15)
    # loop
    while True:
        measurement_raw = sgp40.measure_raw()
        print("Raw data: {}".format(measurement_raw))
        #measurement_test = sgp40.measure_test()
        #print("Measurement test: {}".format(measurement_test))

        time.sleep(dt)



if __name__ == "__main__":
    dt = 1  # 1 sec loop
    simple_test(dt)
    index_test(dt)
