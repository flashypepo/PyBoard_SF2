"""
WBUS_DIP68 - baseclass for tiles on the WBUS-DIP68

2020-1101 PP added poweron in init() and now program in main works!
2020-0512 PP new, https://pybd.io/hw/wbus_dip68.html
"""
import machine
from time import sleep

class WBUS_DIP68:

    def __init__(self):
        self._i2c = machine.I2C('X')
        self._spi = machine.SPI('X')
        # 2020-1101 added poweron - a must apparently!
        self.powerOn()
        #DEBUG: print(self._i2c.scan())  # 2020-1101 not empty after poweron
        # no enable power by-default. Let tile decide.


    def powerOn(self):
        machine.Pin.board.EN_3V3.value(1) # 2020-1101 added - works!
        # 2020-1101 NOT WORKING: machine.Pin('EN_3V3').on()
        sleep(0.2)  # 2020-1101 added- some delay

    def powerOff(self):
        machine.Pin.board.EN_3V3.value(0) # 2020-1101 added - ?works
        # 2020-1101 removed: machine.Pin('EN_3V3').off()  # disable power on Tile-bus
        sleep(0.2)  # 2020-11-1 added

    # 2020-0512: no property -> errors in calling i2c-methods !?
    #@property
    def i2c(self):
        return self._i2c
    
    # @property
    def spi(self):
        return self._spi
