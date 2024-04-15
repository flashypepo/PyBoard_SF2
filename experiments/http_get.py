"""
http_get(url)

2021-0805 PP based upon
https://docs.micropython.org/en/latest/esp8266/tutorial/network_tcp.html#http-get-request
"""
import time
import ujson
from secrets import secrets

def http_get(url):
    import socket
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    data = buf = ''
    while True:
        data = s.recv(100)
        if data:
            buf += str(data, 'utf8')
        else:
            break
    s.close()
    return buf

def get_data_for(city="Bussum", country_code="NL"):
    api_url = "http://api.openweathermap.org/data/2.5/weather"
    api_key = secrets["OPENWEATHER_API_KEY"]
    #country_code = "NL"
    #city = "Bussum"
    url = "{0}?q={1},{2}&APPID={3}".format(api_url, city, country_code, api_key)

    # remove whitespaces '\r\n' and remove header to get JSON-string
    recv = http_get(url)
    ccc = recv.replace("\r\n", "")  # remove "\r'n"
    aaa = ccc.split("POST")   # split HTML-header from JSON
    json_str = aaa[1]  # get the JSON string
    # parse to JSON
    # https://docs.micropython.org/en/latest/library/ujson.html
    #print ("JSON string:", json_str)
    #js = ujson.loads(json_str)
    #print("\nJSON object is type:", type(js))
    #return js
    return ujson.loads(json_str)

# getters
def name(js):
    return js["name"]

def temperature(js):
    return js["main"]["temp"]

def humidity(js):
    return js["main"]["humidity"]

def description(js):
    return js["weather"][0]["description"]

def demo(city="Bussum", country_code="NL"):
    print("Ophalen weergegevens voor {},{} ...".format(city, country_code), end='')
    js = get_data_for(city, country_code)
    print('\n')
    # print(js)
    # specific weather data
    print ("Temperature : {} Kelvin".format(temperature(js)))
    print ("Humidity    : {} %".format(humidity(js)))
    print ("Description : {}".format(description(js)))
    

if __name__ == "_main_":
    demo("Naarden", "NL")
