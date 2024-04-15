"""
boot.py -- run on boot-up
can run arbitrary Python, but best to keep it minimal

2021-1025 PP modified: use antenna and f-string (mp v1.17+)
2020-1224 PP rmeoved unnessary comments and code - see boot_archief.py
2020-1101 PP removed not used modules
2020-0512 PP added Wifi(raw!), emergency buffer, add comment 2020-0512
2020-0504 P modified: NL
"""
# for emergency exception buffer
import micropython
import machine
import pyb
#import time
from secrets import secrets

# Buffer for interrupt error messages
micropython.alloc_emergency_exception_buf(100)

# 2022-0525 PP added for power-control
USE_WBUS_DIP68 = True
USE_WBUS_DIP28 = not USE_WBUS_DIP68


pyb.country('NL') # ISO 3166-1 Alpha-2 code, eg US, GB, DE, AU
#pyb.usb_mode('VCP+MSC')  # act as a serial and a storage device
#pyb.usb_mode('VCP+HID') # act as a serial device and a mouse

USE_WIFI = True  # 2020-0512 added
USE_ANTENNA = 1   # 2021-1025 modified to 1, 2021-0805 antenna (1) or not (0)

# Wifi
# Source: https://github.com/peterhinch/micropython-samples/tree/master/pyboard_d#bootloader-and-boot-options
print(f"Wifi is enabled: {USE_WIFI}, external antenna: {USE_ANTENNA}")
#print("Wifi is enabled: {0}, external antenna: {1}".format(USE_WIFI, USE_ANTENNA))
if USE_WIFI is True:
    # bare bone STA-connection
    import network
    wl = network.WLAN()
    # 2021-0805 check if device is not connected to Wifi...
    if wl.isconnected() is False:
        # connect device to Wifi, use secrets
        mySSID = secrets["ssid"]
        myPASSWORD = secrets["password"]
        wl.active(1)             # activate network
        # config parameters:
        wl.config(antenna=USE_ANTENNA)  # 2021-1025 modified: 0 internal 1 external
        mac = wl.config('mac')   # get the MAC address
        # wl.config(txpower=value)  # In dbm
        # wl.config(trace=value) # value can be a bit-wise or of 1=async-events, 2=eth-tx, 4=eth-rx.
        # So:
        #   wl.config(trace=7)  # To see everything.
        #   wl.config(trace=0)  # To stop
        networks = wl.scan()     # scan for access points, returning a list
        print(f"Connecting to Wifi '{mySSID}'")
        wl.connect(mySSID, myPASSWORD)
    # print network status
    print("IP = {}".format(wl.ifconfig()[0]))  # 2022-0326 PP configuration data
    #print(f"IP = {wl.ifconfig()[0]})"   # 2022-0326 PP configuration data

    """
    from wifimanager import WifiManager
    wifi = WifiManager(secrets["ssid"], secrets["password"])
    wifi.connect()
    while wifi._wifi.isconnected is False:
        machine.idle()
    print("Wifi connected:", wifi._wifi.isconnected())
    print(wifi._wifi.ifconfig())
    """
    # 2022-0720 PP added helper for IP address
    # Note: returns IP in text
    def ip(wl):
        return wl.ifconfig()[0]


# 2020-1224 PP added SD-card
if pyb.SDCard().present():
    import sys, os
    os.mount(pyb.SDCard(), '/sd')
    sys.path[1:1] = ['/sd', '/sd/lib']
    print("SD card added")

# 2022-0720 PP added scan(i2c)
# print I2C-bus devices in hex-value en decimal-value
def print_i2cscan(i2c):
    """
    print_i2cscan: print the address attached to the I2C bus (hex and decimal values)
    @param i2c - i2c-bus
    """
    devices = i2c.scan()
    for device in devices:
        print(f"device: {hex(device)}({device})")


# 2022-0525 PP added power control
def power_on():
    machine.Pin('EN_3V3').value(1)

def power_off():
    machine.Pin('EN_3V3').value(0)

if USE_WBUS_DIP68 is True:
    power_on()
