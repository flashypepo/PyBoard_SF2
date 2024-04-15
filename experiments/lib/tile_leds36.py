"""
class TileLED36 - controls tile LED36 mounted on WBUS_DIP68 or WBUS_DIP28

2022-0720 PP added support for different (software) I2C address), and logger
2022-0326 PP placed PyBoard on WBUS_DIP68, again
2021-0410 PP added WBUS_DIP28
    TODO: how to select WBUS_DIP68 or WBUS_DIP28 with configuration?
2020-0512 PP added WBUS_DIP68
2020-0504 PP based upon given demo
"""
from micropython import const
import time
import machine
# PYB mounted on WBUS_DIP68
from wbus_dip68 import WBUS_DIP68 as WBUS_DIP
# PYB mounted on WBUS_DIP28
#from wbus_dip28 import WBUS_DIP28 as WBUS_DIP

from logger import logger as log

LED_BROADCAST = const(1)   # broadcast I2C address
LED_ADDR = const(60)       # default individual LED36 address
# 2022-0720 I2C address must be changed when OLED SSD1306 displays are used,
# which have by-default the same address (0x3c (60))


class TileLED36(WBUS_DIP):

    def __init__(self, address):
        super().__init__()
        self._i2c = super().i2c()
        cur_addr = self._i2c.scan()[1]  # ASSUMPTION IT IS 2nd address in scan()
        log.debug(f"LED36 current I2C-address = {hex(cur_addr)} ({cur_addr})", fn=__name__)
        if address != cur_addr:
            new_addr = address
            self.set_i2caddr(cur_addr, new_addr)
            log.debug(f"LED36 new I2C-address = {hex(new_addr)} ({new_addr}) ... RESET MCU!",  fn=__name__)
            super().toggle_power()
        self._address = address
        self.init()

    # helper for set_i2caddr()
    def _save_nvram(self, addr):
        """ Save NVRAM state """
        self._i2c.writeto(addr, b'\x02fn')

    # The default I2C address of 60 can be changed using the following code
    # URL: https://pybd.io/hw/tile_led36.html
    # 2022-0720 PP added - using a different I2C address does not work (ENODEV-error)
    def set_i2caddr(self, cur_addr, new_addr):
        """ Modify I2C address and save it to NVRAM """
        ba = bytearray(b'\x02\x0eI2C ')
        ba[-1] = (new_addr * 2) & 0xfe
        self._i2c.writeto(cur_addr, ba)
        self._save_nvram(cur_addr)

    # 2020-0512 added - initialise the tile LED36
    # URL: https://pybd.io/hw/tile_led36.html
    def init(self):
        super().powerOn()
        self._i2c.writeto(LED_BROADCAST, b'\x01')  # initialise all LED36 tiles with broadcast address
        time.sleep_ms(20)  # wait for LED36 tiles to be ready

    def fill_rgb(self, r, g, b):
        """ Fill LED array using set pixel command """
        #DEBUG: print(f"fill_rgb::I2C-address = {hex(self._address)} ({self._address})")
        addr = self._address   # 2022-0720 PP added
        self._i2c.writeto(addr, b'\x02X\x00\x00')
        buf = bytearray(b'\x02A   ')
        buf[2] = r
        buf[3] = g
        buf[4] = b
        for i in range(36):
            self._i2c.writeto(addr, buf)

    def illu(self, r, g, b):
        """ Fill LED array using set illumination command """
        addr = self._address   # 2022-0720 PP added
        buf = bytearray(b'\x02i   ')
        buf[2] = r
        buf[3] = g
        buf[4] = b
        self._i2c.writeto(addr, buf)

    def fill_frame(self, r, g, b):
        """ Fill LED array using fill frame command """
        addr = self._address   # 2022-0720 PP added
        self._i2c.writeto(addr, b'\x02ml')
        buf = bytearray(b'   ')
        buf[0] = r
        buf[1] = g
        buf[2] = b
        for i in range(36):
            self._i2c.writeto(addr, buf)

    def set_dot(self, x, y, r, g, b):
        """ Set single LED color at position """
        addr = self._address   # 2022-0720 PP added
        buf = bytearray(b'\x02X  ')
        buf[2] = x
        buf[3] = y
        self._i2c.writeto(addr, buf)

        buf = bytearray(b'\x02A   ')
        buf[2] = r
        buf[3] = g
        buf[4] = b
        self._i2c.writeto(addr, buf)

    def fill_raw(self, r, g, b):
        """ Fill LED array with raw values using fill frame command """
        addr = self._address   # 2022-0720 PP added
        self._i2c.writeto(addr, b'\x02nl')
        buf = bytearray(b'   ')
        buf[0] = r
        buf[1] = g
        buf[2] = b
        for i in range(36):
            self._i2c.writeto(addr, buf)

    def led_pins(self, v):
        """ Permute LED colors (use with care) """
        addr = self._address   # 2022-0720 PP added
        buf = bytearray(b'\x02\x1c\x00')
        buf[-1] = v & 3
        self._i2c.writeto(addr, buf)

    # sample code from forum:
    # https://forum.micropython.org/viewtopic.php?f=20&t=6272
    def brightness(self, b=100):
        """ Set brightness """
        ba = bytearray(b'\x02\x16 ')
        ba[-1] = b & 0xff
        self._i2c.writeto(LED_BROADCAST, ba)

    # rb, gb, bb: background color!
    def set_text_color(self, r, g, b, rb, gb, bb):
        addr = self._address   # 2022-0720 PP added
        ba = bytearray(b'\x02c      ')
        ba[-6] = b  # front/text color blue
        ba[-5] = g  # front/text color green
        ba[-4] = r  # front/text color red
        ba[-3] = bb  # background color blue
        ba[-2] = gb  # background color green
        ba[-1] = rb  # background color red
        self._i2c.writeto(addr, ba)

    def set_rot(self, angle):
        addr = self._address   # 2022-0720 PP added
        ba = bytearray(b'\x02\x14 ')
        ba[-1] = angle
        self._i2c.writeto(addr, ba)

    def text(self, data, col_cycle=False):
        addr = self._address   # 2022-0720 PP added
        if col_cycle:
            ba = bytearray(b'\x02k ')
        else:
            ba = bytearray(b'\x02l ')
        ba[-1] = len(data) & 0xff
        self._i2c.writeto(addr, ba)
        for i in data:
           self._i2c.writeto(addr, i)

    def show(self, cycles=400, delay=50):
        count = 0
        #while True:
        while count < cycles:
            self._i2c.writeto(LED_BROADCAST, b'\x01')
            time.sleep_ms(delay)
            count += 1
    # endof sample code from forum

    # ---------------------
    # DEMO's for LED36
    # ---------------------
    def random_dots(self, dt=10):
        """ Set random colors at random positions """
        import pyb
        while True:
            rn = pyb.rng()
            r = rn & 0xff
            g = (rn >> 8) & 0xff
            b = (rn >> 16) & 0xff
            x = (rn >> 24) % 36
            y = x // 6
            x %= 6
            # print(x, y, r, g, b)  # 2020-0504 added
            self.set_dot(x, y, r, g, b, addr)  # 2020-0504 updated
            time.sleep_ms(dt)

    def cyc(self, dt=250):
        """ Set all LEDs to black, red, green, yellow, blue, magenta, cayn
            and white for dt ms. ramp up brightnes from 0 % to 100 %
        """
        while True:
            try:
                self.fill_rgb(100, 100, 100)
                for i in range(8):
                    self.fill_rgb((i & 1) * 255, ((i >> 1) & 1) * 255, ((i >> 2) & 1) * 255)
                    time.sleep_ms(dt)
                for i in range(100):
                    self.brightness(i)
                    time.sleep_ms(20)
                #break
            except:
                time.sleep_ms(100)

    def bloop(self, dt=100, maxv=100, inc=1):
        """ Cycle through brigntness ramp """
        b = 0
        while True:
            # print(b)
            self.brightness(b)
            b += inc
            b %= maxv
            time.sleep_ms(dt)

    def pump(self, cycles=5, dt=10, maxv=100):
        """ Cycle through brightness modulation """
        import math
        sinar = []
        for i in range(90):
            sinar.append(int((math.sin(i * 4 / 180 * math.pi) + 1) * maxv / 2))
        i = count = 0
        MAX_CYCLES = cycles*90
        #while True:
        while count < MAX_CYCLES:
            self.brightness(sinar[i])
            i += 1
            i %= len(sinar)
            time.sleep_ms(dt)
            count += 1


# type CTRL-C to skip through the demos
def demos(led_tile):
    try:
        # 1
        print('Cycle colors on all LEDs...')
        led_tile.cyc()
        time.sleep(1)
        # 2
        print('Fill LEDs with a color RGB...')
        led_tile.illu(0,255,0)
        time.sleep(1)
        # 3
        print('cycle through brightness modulation...')
        led_tile.pump()

    except KeyboardInterrupt:
        try:
            # 4
            print('Scrolling text...')
            # sample code from forum
            # https://forum.micropython.org/viewtopic.php?f=20&t=6272
            # led36.set_text_color(0, 150, 0)
            led_tile.set_rot(2)  # vertical-flip
            # led36.brightness(100)
            led_tile.text('Micropython is sooo cool..')
            led_tile.show()  # loop

        except KeyboardInterrupt:
            try:
                # 5
                print('random dots...')
                led_tile.random_dots()

            except KeyboardInterrupt:
                led_tile.fill_rgb(0,0,0)  # clear LEDs
                pass

# demos of class TileLED36.
# type CTRL-C to skip through the demos
if __name__ == '__main__':
    try:
        # create a tile
        led_tile = TileLED36()
        demos(led_tile)
    finally:
        print('demo done!')
