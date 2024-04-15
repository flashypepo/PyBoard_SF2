"""
getweather - get weather data from OpenWeatherMap
using Lolin S2 mini microcontroller and micropython

pre-condition: device is connected to internet / Wifi

Dependencies:
urequest
max7219
micropython

Errors:
connecting to network ... ZiggoJanssen
OSError BREAK! Wifi Internal Error

2021-1025 PP added ulogging (DOE NOT YET work)
            remove print() to see if device still works
            with power-suply only 
2021-1024 PP collect data for more cities
2021-1022 PP add s2mini, class LEDMatrix
Note:
Experiment with LED signal stopped: LED is not visible!
2021-1022 PP setup
"""
import gc
import time
import machine
import json
import urequest

# TEST: logger
# https://github.com/pfalcon/pycopy-lib/tree/master/ulogging
# Import ulogging
#import _thread

import pyb as board
#from ledmatrices import LEDMatrix
from secrets import secrets

# time timer calls callback in ms
TIMER_PERIOD = 300000  # 300 secs = 5 min

# 2021-1024 PP: why is next necessary to avoid NameError?
# not_used_anymore: from boot import re_connect

# private configuration data
API_KEY = secrets['OW_key']
CITY = secrets['location']  # default city

update_weather = True # flag to indiate weather data should be updated
                      # 2021-1024 first time: True

def setup_configuration(timer_period=TIMER_PERIOD):
    print("setup configuration...")
    # create SPI bus, ledmatrix and timer
    """ TODO:
    spi = machine.SoftSPI(baudrate=10_000_000, polarity=0, phase=0,
                          sck=machine.Pin(board.SPI_CLK),
                          mosi=machine.Pin(board.SPI_MOSI),
                          miso=machine.Pin(board.SPI_MISO))
    """
    #print("\tSPI bus...", spi)  #debug
    # SoftSPI(baudrate=500000, polarity=0, phase=0, sck=7, mosi=11, miso=9)
    
    """ TODO ?
    # create LED matrix
    ledmatrix = LEDMatrix(spi=spi, cs=machine.Pin(12), n=4)
    #print("\tLEDmatrix...", ledmatrix)
    """
    
    # create timer for updating weather data
    # periodic firing every timer_period ms
    tim = machine.Timer(-1)  # -1: virtual timer
    tim.init(mode=machine.Timer.PERIODIC,
             period=timer_period,
             callback=handler_update_weather)
    #print("\tTimer...", tim)

    # builtin led for signal datar etrieval from internet
    led = board.LED(1)
    
    #return (spi, ledmatrix, tim, led)
    return (None, None, tim, led)
    
        
# callback for Timer - signal weather data must be updated
def handler_update_weather(timer):
    global update_weather
    #print("It's time to update weather data...")
    update_weather = True


def get_weather(city=CITY):
    """
    getweather() - get weather data from OpenWeatherMap and returns a dict data
        @city: name of a city
        @returns: data, a dict
    """
    # request weather data for city in JSON-format
    #r = urequest.get("http://api.openweathermap.org/data/2.5/weather"
    #                  "?q=%s&appid=%s" % (city, API_KEY)).json()
    # PYBOARD: urequest.urlopen() returns data in a socket
    sock = urequest.urlopen("http://api.openweathermap.org/data/2.5/weather"
                      "?q=%s&appid=%s" % (city, API_KEY))
    #debug: print("\nrecord: {}\n\n".format(sock))
    s = sock.readline()  # read data as byte-string from socket
    txt = s.decode("utf-8")  # convert byte-string to string
    r = json.loads(s) # convert string to json
    
    # construct data dict from JSON response
    data = {}
    data["name"] = r["name"]
    data["icon"] = r["weather"][0]["icon"]
    data["temp"] = int(r["main"]["temp"] - 273.15)
    data["feels_like"] = int(r["main"]["feels_like"] - 273.15)
    data["humidity"] = int(r["main"]["humidity"])
    data["pressure"] = int(r["main"]["pressure"])
    data["wind"] = float(r["wind"]["speed"])
    data["description"] = r["weather"][0]["description"]
    #debug: print(data)
    #print("\tgot data for {}".format(data["name"]))
    return data

# stop the timer
def timer_stop(tim):
    if not tim is None:
        tim.deinit()


def data_all_cities(cities):
    """
        data_all_cities() - collect data for all cities
        cities: list of cities
        returns: text string of all weather data
    """
    print("Getting data for {} cities...".format(len(cities)))
    # template strings
    t_str = '{0:2d}({1:2d}) Celsius'  # temperature
    h_str = ", {0:} %"                # humidity
    p_str = ", {0:} hPa"              # pressure
    w_str = ", {0:3.1f} m/s"          # wind

    # construct text of all data to be shown
    mesg = ""
    for city in cities:
        print("\tCity: {}".format(city))
        data = get_weather(city)
        # construct text for led-matrix
        mesg += data.get("name") + ":"
        mesg += t_str.format(data.get("temp"), data.get("feels_like"))
        mesg += h_str.format(data.get("humidity"))
        mesg += p_str.format(data.get("pressure"))
        mesg += w_str.format(data.get("wind"))
        mesg += ", " + data.get("description")
        mesg += "   "
        time.sleep_ms(300)  # wait, not too fast getting data
    return mesg


# main execution
def weatherstation():
    timer_period = 300000 # ms -> 5 minutes  (default TIMER_PERIOD)
    cities=["Naarden,NL", "Dubai,AE", "Antwerpen,BE"]
    print(f"Get weather data from {cities}")
    run(cities=cities, period = timer_period)

# main thread: show weather data for all cities in list,
# keep scrolling weather data until update is requested by timer
# Note: timer_period >> time to scroll all data
def run(cities, period=TIMER_PERIOD):
    global update_weather
    try:
        #print("Start weather program...")
        # setup deie configuration
        #TODO: spi, ledmatrix, tim, led = setup_configuration(
        #    timer_period=period)
        _, _, tim, led = setup_configuration(timer_period=period)
        # enter the loop...
        # keep scrolling data until update is requested by timer
        # Note: timer-period >> time to scroll all data
        update_weather = True   # get data for first time
        #print("entering the loop...", update_weather)
        while True:
            # check if new data must be collected... 
            if update_weather is True:
                led.on()
                #state = machine.disable_irq() #<- crashes device???
                mesg = data_all_cities(cities)
                update_weather = False
                #debug: mem_str = " - free memory {0:4.3f} Mb"
                #       mesg += mem_str.format(gc.mem_free() // 1024 / 1000)  #debug
                #machine.enable_irq(state)  #<- crashes device???
                led.off()
            # scroll message along the LED matrices
            print(f"{mesg}\n")
            #TODO: ledmatrix.scroll_message(mesg)
            # house-keeping
            # keep free memory as high as possible
            gc.collect()
            # wait a little time before next iteraion
            time.sleep(60)
    # not used: keep scrolling current data
    except Exception as e:
        print(e)
        timer_stop(tim)
    except NameError as ne:
        #print("NameError BREAK!", ne)
        timer_stop(tim)  #tim.deinit()
        pass
    except OSError as ose:
        #print("OSError BREAK!", ose)
        timer_stop(tim)  #tim.deinit()
        weatherstation()  # re-try main program
    except KeyboardInterrupt:
        timer_stop(tim)  #tim.deinit()
        #TODO:  ledmatrix.clear()
        print('Timer stopped and done!')
