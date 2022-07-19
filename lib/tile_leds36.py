"""
class TileLED36 - controls tile LED36 mounted on WBUS_DIP68 or WBUS_DIP28

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


LED_BROADCAST = const(1)   # broadcast I2C address
LED_ADDR = const(60)       # default individual LED36 address


class TileLED36(WBUS_DIP):
    def __init__(self, address=LED_ADDR):
        super().__init__()
        self._i2c = super().i2c()
        self._address = address
        self.init()

    # 2020-0512 added - initialise the tile LED36
    def init(self):
        super().powerOn()
        self._i2c.writeto(LED_BROADCAST, b'\x01')     # initialise all LED36 tiles with broadcast address
        time.sleep_ms(20)           # wait for LED36 tiles to be ready

    def cyc(self, dt=250, addr=LED_ADDR):
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

    def brightness(self, b=100, addr=LED_ADDR):
        """ Set brightness """
        ba = bytearray(b'\x02\x16 ')
        ba[-1] = b & 0xff
        self._i2c.writeto(addr, ba)

    def bloop(self, dt=100, maxv=100, inc=1, addr=LED_ADDR):
        """ Cycle through brigntness ramp """
        b = 0
        while True:
            # print(b)
            self.brightness(b)
            b += inc
            b %= maxv
            time.sleep_ms(dt)

    def pump(self, cycles=5, dt=10, maxv=100, addr=LED_ADDR):
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

    def fill_rgb(self, r, g, b, addr=LED_ADDR):
        """ Fill LED array using set pixel command """
        self._i2c.writeto(addr, b'\x02X\x00\x00')
        buf = bytearray(b'\x02A   ')
        buf[2] = r
        buf[3] = g
        buf[4] = b
        for i in range(36):
            self._i2c.writeto(addr, buf)

    def illu(self, r, g, b, addr=LED_ADDR):
        """ Fill LED array using set illumination command """
        buf = bytearray(b'\x02i   ')
        buf[2] = r
        buf[3] = g
        buf[4] = b
        self._i2c.writeto(addr, buf)

    def fill_frame(self, r, g, b, addr=LED_ADDR):
        """ Fill LED array using fill frame command """
        self._i2c.writeto(addr, b'\x02ml')
        buf = bytearray(b'   ')
        buf[0] = r
        buf[1] = g
        buf[2] = b
        for i in range(36):
            self._i2c.writeto(addr, buf)

    def set_dot(self, x, y, r, g, b, addr=LED_ADDR):
        """ Set single LED color at position """
        buf = bytearray(b'\x02X  ')
        buf[2] = x
        buf[3] = y
        self._i2c.writeto(addr, buf)

        buf = bytearray(b'\x02A   ')
        buf[2] = r
        buf[3] = g
        buf[4] = b
        self._i2c.writeto(addr, buf)

    def fill_raw(self, r, g, b, addr=LED_ADDR):
        """ Fill LED array with raw values using fill frame command """
        self._i2c.writeto(addr, b'\x02nl')
        buf = bytearray(b'   ')
        buf[0] = r
        buf[1] = g
        buf[2] = b
        for i in range(36):
            self._i2c.writeto(addr, buf)

    def led_pins(self, v, addr=LED_ADDR):
        """ Permute LED colors (use with care) """
        buf = bytearray(b'\x02\x1c\x00')
        buf[-1] = v & 3
        self._i2c.writeto(addr, buf)


    def random_dots(self, dt=10, addr=LED_ADDR):
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

    # sample code from forum:
    # https://forum.micropython.org/viewtopic.php?f=20&t=6272
    # rb, gb, bb: background color!
    def set_text_color(self, r, g, b, rb, gb, bb, addr=LED_ADDR):
        ba = bytearray(b'\x02c      ')
        ba[-6] = b  # front/text color color blue
        ba[-5] = g  # front/text color color green
        ba[-4] = r  # front/text color color red
        ba[-3] = bb  # background color blue
        ba[-2] = gb  # background color green
        ba[-1] = rb  # background color red
        self._i2c.writeto(addr, ba)

    def set_rot(self, angle, addr=LED_ADDR):
        ba = bytearray(b'\x02\x14 ')
        ba[-1] = angle
        self._i2c.writeto(addr, ba)

    def text(self, data, col_cycle=False, addr=LED_ADDR):
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
            self._i2c.writeto(1, b'\x01')
            time.sleep_ms(delay)
            count += 1

    def brightness(self, b=100, addr=LED_BROADCAST):
        ba = bytearray(b'\x02\x16 ')
        ba[-1] = b & 0xff
        self._i2c.writeto(addr, ba)
    # endof sample code from forum

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
