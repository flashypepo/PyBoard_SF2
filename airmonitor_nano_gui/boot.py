"""
boot.py -- run on boot-up
can run arbitrary Python, but best to keep it minimal

2024-0218 PP mount and use eMMC instead of CDCard
2021-1025 PP modified: use antenna and f-string (mp v1.17+)
2020-1224 PP rmeoved unnessary comments and code - see boot_archief.py
2020-1101 PP removed not used modules
2020-0512 PP added Wifi(raw!), emergency buffer, add comment 2020-0512
2020-0504 P modified: NL
"""
import micropython
# for emergency exception buffer
# Buffer for interrupt error messages
micropython.alloc_emergency_exception_buf(100)

import machine
import pyb
import time
from secrets import secrets

# 2022-0525 PP added for power-control
USE_WBUS_DIP68 = True
USE_WBUS_DIP28 = not USE_WBUS_DIP68

# 2024-0218 PP added eMMC instead of CDCard
USE_EMMC = True
USE_CDCard = not USE_EMMC   # both cannot be used normally.

# usage of Wifi and external antenna
USE_WIFI = True  #True - 2020-0512 added
USE_ANTENNA = 1   # 2021-1025 modified to 1, antenna (1) or not (0)

pyb.country('NL') # ISO 3166-1 Alpha-2 code, eg US, GB, DE, AU
#pyb.usb_mode('VCP+MSC')  # act as a serial and a storage device
#pyb.usb_mode('VCP+HID') # act as a serial device and a mouse


# 2023-0509 power on asap.
#     Maybe it helps to get OLED-display works from the start.
# 2022-0525 PP added power control
def power_on():
    machine.Pin('EN_3V3').value(1)
    time.sleep_ms(50)  # tial-and-error

def power_off():
    machine.Pin('EN_3V3').value(0)

# 2024-0210 added blink a led in freq
def blink(led, freq=0.5):
    from pyb import Timer
    tim = Timer(1, freq=freq)
    #tim.freq(freq) # 0.5 Hz
    tim.callback(lambda t: led.toggle())
    
    
if USE_WBUS_DIP68 is True:
    power_on()


# 2023-0826 PP removed...
# 2023-0509 added USER-button to perform hard_reset
#sw = pyb.Switch()
#sw.callback(lambda: machine.soft_reset())
#sw.callback(lambda: machine.reset())


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
        # NOT USED: mac = wl.config('mac')   # get the MAC address
        # wl.config(txpower=value)  # In dbm
        # wl.config(trace=value) # value can be a bit-wise or of 1=async-events, 2=eth-tx, 4=eth-rx.
        # So:
        #   wl.config(trace=7)  # To see everything.
        #   wl.config(trace=0)  # To stop
        # NOT USED: networks = wl.scan()     # scan for access points, returning a list
        print(f"Connecting to Wifi '{mySSID}'...")
        wl.connect(mySSID, myPASSWORD)
        while not wl.isconnected():
            print(" ", end=".")
            #TEST: machine.idle()
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
    def ip(network=wl):
        return network.ifconfig()[0]

    def mac(network=wl):
        return network.config('mac')   # return the MAC address


# 2024-0218 PP add eMMC storage and expand sys.path
# URL: https://pybd.io/hw/wbus_emmc.html
if USE_EMMC is True:
    import sys, os
    os.mount(pyb.MMCard(), '/mmc')
    #pyb.usb_mode('VCP+MSC', msc=(pyb.MMCard(),)) # expose it over USB mass storage
    pyb.usb_mode('VCP+MSC', msc=(pyb.MMCard(),pyb.Flash())) # expose it also over USB mass storage
    # add eMMC folders to sys.path
    sys.path.append('/mmc')
    sys.path.append('/mmc/lib')
    # power on MMC and make it suitable for sleep
    pyb.MMCard().power(1)
    print(f"eMMC added: sys.path={sys.path}")


# 2020-1224 PP add SDCard if microSD is present
if USE_CDCard is True and pyb.SDCard().present() is True:
    import sys, os
    os.mount(pyb.SDCard(), '/sd')
    # add SDCard folders to sys.path
    sys.path.append('/sd')
    sys.path.append('/sd/lib')
    print(f"SD card added: sys.path={sys.path}")


# 2023-0509 used comprehension
# 2022-0720 PP added scan(i2c)
# print I2C-bus devices in hex-value en decimal-value
def print_i2cscan(i2c):
    """
    print_i2cscan: print the address attached to the I2C bus (hex and decimal values)
    @param i2c - i2c-bus
    """
    print(f"I2C devices: {[hex(d) for d in i2c.scan()]}")
    #devices = i2c.scan()
    #for device in devices:
    #    print(f"device: {hex(device)}({device})")


# 2024-0210 specify LEDs
#TODO: should be in a board specification file
red = pyb.LED(1)
green = pyb.LED(2)
blue = pyb.LED(3)

import time
red.toggle()
time.sleep(0.5)
red.toggle()
print("boot process is done")
