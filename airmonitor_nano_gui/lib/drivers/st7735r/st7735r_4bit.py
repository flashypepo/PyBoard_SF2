# st7735r.py Driver for 1.8" 128*160 ST7735R LCD displays for nano-gui

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2018-2020 Peter Hinch

# Supported display
# Adfruit 1.8' Color TFT LCD display with MicroSD Card Breakout:
# https://www.adafruit.com/product/358

# Based on
# https://github.com/adafruit/Adafruit_CircuitPython_ST7735R/blob/master/adafruit_st7735r.py
# https://github.com/GuyCarver/MicroPython/blob/master/lib/ST7735.py
# https://github.com/boochow/MicroPython-ST7735

# https://learn.adafruit.com/adafruit-1-44-color-tft-with-micro-sd-socket/python-usage
# disp = st7735.ST7735R(spi, rotation=90,                           # 1.8" ST7735R
# disp = st7735.ST7735R(spi, rotation=270, height=128, x_offset=2, y_offset=3,   # 1.44" ST7735R

from time import sleep_ms
import framebuf
import gc
import micropython
from drivers.boolpalette import BoolPalette

# Datasheet para 8.4 scl write cycle 66ns == 15MHz


@micropython.viper
def _lcopy(dest:ptr8, source:ptr8, lut:ptr8, length:int):
    n = 0
    for x in range(length):
        c = source[x]
        d = (c & 0xf0) >> 3  # 2* LUT indices (LUT is 16 bit color)
        e = (c & 0x0f) << 1
        dest[n] = lut[d]
        n += 1
        dest[n] = lut[d + 1]
        n += 1
        dest[n] = lut[e]
        n += 1
        dest[n] = lut[e + 1]
        n += 1

class ST7735R(framebuf.FrameBuffer):

    lut = bytearray(32)

    # Convert r, g, b in range 0-255 to a 16 bit colour value
    # LS byte goes into LUT offset 0, MS byte into offset 1
    # Same mapping in linebuf so LS byte is shifted out 1st
    @staticmethod
    def rgb(r, g, b):
        return (b & 0xf8) << 5 | (g & 0x1c) << 11 | (g & 0xe0) >> 5 | (r & 0xf8)

    # rst and cs are active low, SPI is mode 0
    def __init__(self, spi, cs, dc, rst, height=128, width=160, usd=False, init_spi=False):
        self._spi = spi
        self._rst = rst  # Pins
        self._dc = dc
        self._cs = cs
        self.height = height  # Required by Writer class
        self.width = width
        self._spi_init = init_spi
        mode = framebuf.GS4_HMSB  # Use 4bit greyscale.
        self.palette = BoolPalette(mode)
        gc.collect()
        buf = bytearray(height * width // 2)
        self._mvb = memoryview(buf)
        super().__init__(buf, width, height, mode)
        self._linebuf = bytearray(self.width * 2)  # 16 bit color out
        self._init(usd)
        self.show()

    # Hardware reset
    def _hwreset(self):
        self._dc(0)
        self._rst(1)
        sleep_ms(1)
        self._rst(0)
        sleep_ms(1)
        self._rst(1)
        sleep_ms(1)

    # Write a command, a bytes instance (in practice 1 byte).
    def _wcmd(self, buf):
        self._dc(0)
        self._cs(0)
        self._spi.write(buf)
        self._cs(1)

    # Write a command followed by a data arg.
    def _wcd(self, c, d):
        self._dc(0)
        self._cs(0)
        self._spi.write(c)
        self._cs(1)
        self._dc(1)
        self._cs(0)
        self._spi.write(d)
        self._cs(1)

    # Initialise the hardware. Blocks 500ms.
    def _init(self, usd):
        self._hwreset()  # Hardware reset. Blocks 3ms
        if self._spi_init:  # A callback was passed
            self._spi_init(self._spi)  # Bus may be shared
        cmd = self._wcmd
        wcd = self._wcd
        cmd(b'\x01')  # SW reset datasheet specifies > 120ms
        sleep_ms(150)
        cmd(b'\x11')  # SLPOUT
        sleep_ms(256)  # Adafruit delay (datsheet 120ms)
        wcd(b'\xb1', b'\x01\x2C\x2D')  # FRMCTRL1
        wcd(b'\xb2', b'\x01\x2C\x2D')  # FRMCTRL2
        wcd(b'\xb3', b'\x01\x2C\x2D\x01\x2C\x2D')  # FRMCTRL3
        wcd(b'\xb4', b'\x07')  # INVCTR line inversion

        wcd(b'\xc0', b'\xa2\x02\x84')  # PWCTR1 GVDD = 4.7V, 1.0uA
        wcd(b'\xc1', b'\xc5')  # PWCTR2 VGH=14.7V, VGL=-7.35V
        wcd(b'\xc2', b'\x0a\x00')  # PWCTR3 Opamp current small, Boost frequency
        wcd(b'\xc3', b'\x8a\x2a')  # PWCTR4
        wcd(b'\xc4', b'\x8a\xee')  # PWCTR5 
        wcd(b'\xc5', b'\x0e')  # VMCTR1 VCOMH = 4V, VOML = -1.1V  NOTE I make VCOM == -0.775V

        cmd(b'\x20') # INVOFF
        # d7..d5 of MADCTL determine rotation/orientation
        if self.height > self.width:
            wcd(b'\x36', b'\x80' if usd else b'\x40')  # MADCTL: RGB portrait mode
        else:
            wcd(b'\x36', b'\xe0' if usd else b'\x20')  # MADCTL: RGB landscape mode
        wcd(b'\x3a', b'\x05')  # COLMOD 16 bit
        wcd(b'\xe0', b'\x02\x1c\x07\x12\x37\x32\x29\x2d\x29\x25\x2B\x39\x00\x01\x03\x10')  # GMCTRP1 Gamma
        wcd(b'\xe1', b'\x03\x1d\x07\x06\x2E\x2C\x29\x2D\x2E\x2E\x37\x3F\x00\x00\x02\x10')  # GMCTRN1

        wcd(b'\x2a', int.to_bytes(self.width, 4, 'big'))  # CASET column address 0 start, 160 end
        wcd(b'\x2b', int.to_bytes(self.height, 4, 'big'))  # RASET

        cmd(b'\x13')  # NORON
        sleep_ms(10)
        cmd(b'\x29')  # DISPON
        sleep_ms(100)

    def show(self):  # Blocks 36ms on Pyboard D at stock frequency (160*128)
        clut = ST7735R.lut
        wd = self.width // 2
        ht = self.height
        lb = self._linebuf
        buf = self._mvb
        self._dc(0)
        self._cs(0)
        if self._spi_init:  # A callback was passed
            self._spi_init(self._spi)  # Bus may be shared
        self._spi.write(b'\x2c')  # RAMWR
        self._dc(1)
        for start in range(wd * (ht - 1), -1, - wd):  # For each line
            _lcopy(lb, buf[start :], clut, wd)  # Copy and map colors
            self._spi.write(lb)
        self._cs(1)
