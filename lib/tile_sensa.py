"""
TILE-Sensa clases and functions
# https://pybd.io/hw/tile_sensa.html

2022-0720 PP added logger as reminder - not used
2020-0512 PP added RGBLED and baseclass WBUS_DIP68
202-0504 PP new
"""
import machine
import time
from wbus_dip68 import WBUS_DIP68

# 2022-0720 PP MAYBE IN FUTURE:
#from logger import logger as log


HDC2080_ADDRESS = 64
OPT3001_ADDRESS = 69

class RGBLED(WBUS_DIP68):

    def __init__(self):
        super().__init__()
        self._led_r = machine.Signal('X2', machine.Pin.OUT, value=0, invert=True)
        self._led_g = machine.Signal('X3', machine.Pin.OUT, value=0, invert=True)
        self._led_b = machine.Signal('X4', machine.Pin.OUT, value=0, invert=True)
        self._leds = [0,0,0]  # led-array containing 0 (OFF) or 1 (ON)

    def _led_on(self):
        self._led_r.on() if self._leds[0] == 1 else self._led_r.off()
        self._led_g.on() if self._leds[1] == 1 else self._led_g.off()
        self._led_b.on() if self._leds[2] == 1 else self._led_b.off()


    def redOn(self, isOnOff=True):
        self._leds[0] = 1 if isOnOff is True else 0
        self._led_on()

    def greenOn(self, isOnOff=True):
        self._leds[1] = 1 if isOnOff is True else 0
        self._led_on()

    def blueOn(self, isOnOff=True):
        self._leds[2] = 1 if isOnOff is True else 0
        self._led_on()

    def off(self):
        self._leds = [0, 0, 0]
        self._led_on()

    def on(self):
        self._leds = [1, 1, 1]
        self._led_on()



class HDC2080(WBUS_DIP68):
    def __init__(self, addr=HDC2080_ADDRESS):
        super().__init__()
        self.i2c = super().i2c()
        self.addr = addr
        super().powerOn()

    def is_ready(self):
        return self.i2c.readfrom_mem(self.addr, 0x0f, 1)[0] & 1 == 0

    def measure(self):
        self.i2c.writeto_mem(self.addr, 0x0f, b'\x01')

    def temperature(self):
        data = self.i2c.readfrom_mem(self.addr, 0x00, 2)
        data = data[0] | data[1] << 8
        return data / 0x10000 * 165 - 40

    def humidity(self):
        data = self.i2c.readfrom_mem(self.addr, 0x02, 2)
        data = data[0] | data[1] << 8
        return data / 0x10000 * 100



class OPT3001(WBUS_DIP68):
    def __init__(self, addr=HDC2080_ADDRESS):
        super().__init__()
        self.i2c = super().i2c()
        # self.i2c = i2c
        self.addr = addr
        # super().__init__()

    def is_ready(self):
        return bool(self.i2c.readfrom_mem(self.addr, 0x01, 2)[1] & 0x80)

    def measure(self):
        self.i2c.writeto_mem(self.addr, 0x01, b'\xca\x10')

    def lux(self):
        data = self.i2c.readfrom_mem(self.addr, 0, 2)
        return 0.01 * 2 ** (data[0] >> 4) * ((data[0] & 0x0f) << 8 | data[1])


if __name__ == '__main__':
    # import _thread  # doesnot exists in micropython v1.11 installed version

    # 2020-0512 no RGBLED, it might influence the measurements?
    # helper function: demo()
    def demo(delay=5):
        import machine
        # from tile_sensa import RGBLED, HDC2080, OPT3001
        from tile_sensa import HDC2080, OPT3001

        # rgbled = RGBLED()
        hdc = HDC2080()
        opt = OPT3001()
        fmt = "Temperature: {:2.2f}C, humidity: {:2.2f}%, lux: {:2.2f}"

        while True:
            hdc.measure()
            opt.measure()
            # rgbled.redOn()
            while not opt.is_ready() and not hdc.is_ready():
                machine.idle()

            print(fmt.format(hdc.temperature(), hdc.humidity(), opt.lux()))
            # time.sleep_ms(200)  # to see red-led!
            # rgbled.redOn(False)
            # rgbled.greenOn()
            time.sleep(delay)
            # rgbled.greenOn(False)


    demo(delay=5)
    # th_temp = _thread.start_new_thread(demo_temp, (2,))
    # th_lux = _thread.start_new_thread(demo_lux, (3,))

