"""
demo openweather API-request
weather data on OLED-display

Configuration:
* OLED, i2c, 128*64 pixels
* class OpenWeatherMap
* Python3

OpenWeatherMap API:
https://openweathermap.org/appid/

2020-1102 PP new - OLED versie
bron: Raspberry Pi Project Handboek

"""
from openweathermap import OpenWeaterMap

if __name__ == "__main__":
    #city_name = "Almere Stad"
    city_name = "Bussum"

    country_code = "NL"
    print(f"Weersrapport voor {city_name} in {country_code}:")

    service = OpenWeaterMap(city_name, country_code)

    # haal op de weersgegeven voor city_name
    temp_max = service.max_temp_celsius()
    wind_speed = service.windspeed()
    description = service.description()

    # toon de weersgegevesn in console
    print("Beschrijving: {}".format(description))
    print ("Max.temperatuur: {:4.2f}\u00b0C".format(temp_max))
    print ("Wind snelheid: {:4.2f} m/s".format(wind_speed))
