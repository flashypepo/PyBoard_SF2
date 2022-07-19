"""
secrets - stored credentials

!! File must not be placed in public places, like GitHub !!

OpenWeatherMap API: https://openweathermap.org/appid/
Adafruit IO credentials: xxxxxxxxx

2021-1025 PP cleanup, only secrets
2021-0805 PP all keys in dictionary 'secrets'; only one Wifi network
2020-11xx PP added Adafruit IO credentials
2020-1102 PP aded API-key's OpenWeatherMap
2020-0802 PP: new, known_nets for Wifi

TODO: collection of known wifi networks
Specify for each ssid (wifi netwerk):
1. passwrd
2. for STATIC IP: provide values for 'wlan_config'
3. for DYNAMIC IP, such as your home Wifi: remove 'wlan_config' values.
Format known_nets (Python dictionary):
known_nets = {
  'ssid_name': {'pwd': 'passwrd',
                'wlan_config': (ip, subnet_mask, gateway, DNS_server),
                },
     .....
}
"""
secrets = {
    "ssid": 'ZiggoJanssen',
    "password": 'rRwp83vKeamp',
    "OW_key": "0268b4521291f0506c640014e469579e",    
    'aio_username' : "your-aio-username-here",
    'aio_key' : 'your-aio-key-here',
    'OW_key'   :  "e27cc670236e2eed2b68918a4989612e",  # 2020-1003 updated
    'location' : 'Naarden,NL',
    'timezone' : "Europe/Amsterdam", # http://worldtimeapi.org/timezones
}
print("secrets loaded...")
