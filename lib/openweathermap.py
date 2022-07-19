"""
class OpenWeatherMap
get weather data from the OpenWeaterMap service

Dependencies:
Python library requests
secrets.py contains API-KEY

OpenWeatherMap API:
https://openweathermap.org/appid/

Pricing and limits Free account:
https://openweathermap.org/price

Kelvin to Celsius: 
https://www.rapidtables.com/convert/temperature/kelvin-to-celsius.html

Source based upon [Santos] Raspberry Pi Project Handboek

2020-1102 PP new, refactored source code to OOP-class
"""
#2021-0805 import requests
import urequest as requests
from secrets import OPENWEATHER_API_KEY

class OpenWeatherMap():
    def __init__(self, city_name, country_code):
        """ get weather data for city_name and country_code,
            store weather data in JSON-format."""
        self._api_url = "http://api.openweathermap.org/data/2.5/weather"
        self._api_key = OPENWEATHER_API_KEY
        city = city_name
        # check for space in name, convert to url-encoded space
        if " " in city_name:
            city = city_name.replace(" ", "%20")
        # 2021-0805 micropython doesnot know f-string:
        # url = f"{self._api_url}?q={city},{country_code}&APPID={self._api_key}"
        url = "{0}?q={1},{2}&APPID={3}".format(self._api_url, city, country_code, self._api_key)
        # DEBUG: print(url)  # debug
        # get the weather data
        data = requests.get(url)
        self._weather_data_json = data.json()

    def max_temp_celsius(self):
        """ return max. temperature in Celcius 
            from weather data """
        # get max.temperature
        temp_max = self._weather_data_json.get('main').get('temp_max')
        return (temp_max - 273.15)

    def windspeed(self):
        return self._weather_data_json.get('wind').get('speed')

    def description(self):
        return self._weather_data_json.get('weather')[0].get('description')

    # more methods which returns a specifc weather data

    # kind of private method, returns weather_data in JSON
    def _data_json(self):
        return self._weather_data_json

# test method
if __name__ == "__main__":
    city_name = "Almere Stad"
    country_code = "NL"
    #2021-0805 print(f"Weersrapport voor {city_name} in {country_code}:")
    print("Weersrapport voor {0} in {1}:".format(city_name, country_code))
    service = OpenWeaterMap(city_name, country_code)
    temp_max = service.max_temp_celsius()
    print ("Max.temperatuur: {:4.2f}\u00b0C".format(temp_max))
    print("JSON:\n{}".format(service._data_json()))
