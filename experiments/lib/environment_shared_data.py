"""
class EnvironmentData - a simple data class to hold
environment data for sharing between tasks.
Uses property decorator for data to read or write.

2022-0121 PP used with pyRTOS to share envirnmental data
2021-1130 PP new
"""

#TODO: dataclass
class EnvironmentData:
    """
        Simple data class to hold environment sensor data.
        Use property decorator for data to read or write.
    """
    def __init__(self):
        # initialise data with arbitrary data
        self._sensor = "SENSOR"  # placeholder type of sensor
        self._temperature = 0  # Sensa temp, unit: Celsius
        self._humidity = 0     # Sensa humidity, unit: %RH
        self._external_temperature = 0  # external temp, unit: Celsius
        self._external_humidity = 0     # external humidity, unit: %RH
        self._pressure = 1023  # unit: hPa
        self._altitude = 0     # unit in meters
        self._dewpoint = 0     # dewpoint
        self._gas = 0          # unit in Ohm
        self._sea_level_pressure = 1023  # sea level pressure on location
        self._eco2 = 0   # air-quality eCo2, unit in ppb
        self._voc = 0    # air quality: particles, unit in ppm
        self._ambientlight = 0   # ambient light value in lux

    @property
    def sensor(self):
        """ returns name of sensor"""
        return self._sensor

    @sensor.setter
    def sensor(self, value):
        """ set name of sensor"""
        self._sensor = value

    @property
    def dewpoint(self):
        """ returns dewpoint"""
        return self._dewpoint

    @dewpoint.setter
    def dewpoint(self, value):
        """ set dewpoint"""
        self._dewpoint = value

    @property
    def temperature(self):
        """ returns temperature in Celsius"""
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        """ set temperature in Celsius"""
        assert(value > -273.15)  # t not below absolute zero
        self._temperature = value

    @property
    def humidity(self):
        """ returns humidity in %RH"""
        return self._humidity

    @humidity.setter
    def humidity(self, value):
        """ set humidity in %RH"""
        assert(value >= 0)  # H not below zero
        self._humidity = value


    @property
    def ex_temperature(self):
        """ returns temperature in Celsius from external sensor"""
        return self._external_temperature

    @ex_temperature.setter
    def ex_temperature(self, value):
        """ set temperature in Celsius from external sesor"""
        assert(value > -273.15)  # t not below absolute zero
        self._external_temperature = value

    @property
    def ex_humidity(self):
        """ returns humidity in %RH from external sensor"""
        return self._external_humidity

    @ex_humidity.setter
    def ex_humidity(self, value):
        """ set humidity in %RH from external sensor"""
        assert(value > 0)  # H not below zero
        self._external_humidity = value

    @property
    def pressure(self):
        """ returns pressure in hPa"""
        return self._pressure

    @pressure.setter
    def pressure(self, value):
        """ set pressure in hPa"""
        assert(value > 0)  # P not below zero
        self._pressure = value

    # ----- added altitude and sea_level pressure
    @property
    def altitude(self):
        """ returns altitude in meters"""
        return self._altitude

    @altitude.setter
    def altitude(self, value):
        """ set altitude in meters"""
        self._altitude = value

    @property
    def sea_level_pressure(self):
        """ returns sea_level_pressure in hPa.
            used to calibrate for the altitude"""
        return self._sea_level_pressure

    @sea_level_pressure.setter
    def sea_level_pressure(self, value):
        """ set sea_level_pressure in hPa"""
        assert(value > 0)
        self._sea_level_pressure = value

    @property
    def gas(self):
        """ returns gas in Ohm"""
        return self._gas

    @gas.setter
    def gas(self, value):
        """ set gas in Ohm"""
        assert(value > 0)
        self._gas = value

    @property
    def eco2(self):
        """ returns eCo2 value in ppb"""
        return self._eco2

    @eco2.setter
    def eco2(self, value):
        """ set sea_level_pressure in hPa"""
        assert(value >= 400)
        self._eco2 = value

    @property
    def voc(self):
        """ returns VOC value in ppm """
        return self._voc

    @voc.setter
    def voc(self, value):
        """ sets VOC value in ppm """
        assert(value >= 0)
        self._voc = value

    # 2022-0720 PP added ambient light in lux
    @property
    def ambientlight(self):
        """ returns ambient light in lux"""
        return self._ambientlight

    @ambientlight.setter
    def ambientlight(self, value):
        """ set ambient light in lux"""
        assert(value > 0)  # ambient light not below zero
        self._ambientlight = value

