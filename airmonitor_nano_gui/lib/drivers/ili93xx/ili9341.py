# ILI9341 nano-gui driver for ili9341 displays
# As with all nano-gui displays, touch is not supported.

# Copyright (c) Peter Hinch 2020
# Released under the MIT license see LICENSE

# This work is based on the following sources.
# https://github.com/rdagger/micropython-ili9341
# Also this forum thread with ideas from @minyiky:
# https://forum.micropython.org/viewtopic.php?f=18&t=9368

# 2023-1007 PP: added some methodes from rdagger. Some are work-in-progress

from time import sleep_ms
import gc
import framebuf
import uasyncio as asyncio
from drivers.boolpalette import BoolPalette

@micropython.viper
def _lcopy(dest:ptr16, source:ptr8, lut:ptr16, length:int):
    # rgb565 - 16bit/pixel
    n = 0
    for x in range(length):
        c = source[x]
        dest[n] = lut[c >> 4]  # current pixel
        n += 1
        dest[n] = lut[c & 0x0f]  # next pixel
        n += 1

# 2023-1007 PP added from rdagger-github: NOT TESTED
def color565(r, g, b):
    """Return RGB565 color value.

    Args:
        r (int): Red value.
        g (int): Green value.
        b (int): Blue value.
    """
    return (r & 0xf8) << 8 | (g & 0xfc) << 3 | b >> 3


class ILI9341(framebuf.FrameBuffer):

    lut = bytearray(32)
    
    # 2023-1007 PP added for rotation display
    #           and changed in binary buffer
    ROTATE = {
        0: b'\x88',
        90: b'\xE8',
        180: b'\x48',
        270: b'\x28'
    }

    # Convert r, g, b in range 0-255 to a 16 bit colour value
    # LS byte goes into LUT offset 0, MS byte into offset 1
    # Same mapping in linebuf so LS byte is shifted out 1st
    # ILI9341 expects RGB order
    @staticmethod
    def rgb(r, g, b):
        return (r & 0xf8) | (g & 0xe0) >> 5 | (g & 0x1c) << 11 | (b & 0xf8) << 5

    # Transpose width & height for landscape mode
    # 2023-1007 PP added led-pin for backlight control
    def __init__(self, spi, cs, dc, rst, led, height=240, width=320,
                 usd=False, init_spi=False):
        self._spi = spi
        self._cs = cs
        self._dc = dc
        self._rst = rst
        self._led = led  # 2023-1007 PP added
        self.height = height
        self.width = width
        self._spi_init = init_spi
        mode = framebuf.GS4_HMSB
        self.palette = BoolPalette(mode)
        gc.collect()
        buf = bytearray(self.height * self.width // 2)
        self._mvb = memoryview(buf)
        super().__init__(buf, self.width, self.height, mode)
        self._linebuf = bytearray(self.width * 2)
        # Hardware reset
        self._rst(0)
        sleep_ms(50)
        self._rst(1)
        sleep_ms(50)
        if self._spi_init:  # A callback was passed
            self._spi_init(spi)  # Bus may be shared
        self._lock = asyncio.Lock()
        # Send initialization commands
        self._wcmd(b'\x01')  # SWRESET Software reset
        sleep_ms(100)
        self._wcd(b'\xcf', b'\x00\xC1\x30')  # PWCTRB Pwr ctrl B
        self._wcd(b'\xed', b'\x64\x03\x12\x81')  # POSC Pwr on seq. ctrl
        self._wcd(b'\xe8', b'\x85\x00\x78')  # DTCA Driver timing ctrl A
        self._wcd(b'\xcb', b'\x39\x2C\x00\x34\x02')  # PWCTRA Pwr ctrl A
        self._wcd(b'\xf7', b'\x20')  # PUMPRC Pump ratio control
        self._wcd(b'\xea', b'\x00\x00')  # DTCB Driver timing ctrl B
        self._wcd(b'\xc0', b'\x23')  # PWCTR1 Pwr ctrl 1
        self._wcd(b'\xc1', b'\x10')  # PWCTR2 Pwr ctrl 2
        self._wcd(b'\xc5', b'\x3E\x28')  # VMCTR1 VCOM ctrl 1
        self._wcd(b'\xc7', b'\x86')  # VMCTR2 VCOM ctrl 2
        # (b'\x88', b'\xe8', b'\x48', b'\x28')[rotation // 90]
        if self.height > self.width:
            self._rotation=180 if usd else 0        # rotation 0 or 180
            #self._wcd(b'\x36', b'\x48' if usd else b'\x88')  # MADCTL: RGB portrait mode
        else:
            self._rotation=270 if usd else 90        # rotation 90 or 270
            #self._wcd(b'\x36', b'\x28' if usd else b'\xe8')  # MADCTL: RGB landscape mode
        self.init()
        #self._wcmd(b'\x29')  # DISPLAY_ON
        #self._led.value(1)   # 2023-1007 PP added - backlight is on
        #self rotate()    # update display according to _rotation value
        #sleep_ms(100)

    # 2023-1007 PP added and code moved from constructor
    def init(self):
        """ Initialise the display"""
        self._wcd(b'\x37', b'\x00')  # VSCRSADD Vertical scrolling start address
        self._wcd(b'\x3a', b'\x55')  # PIXFMT COLMOD: Pixel format 16 bits (MCU & interface)
        self._wcd(b'\xb1', b'\x00\x18')  # FRMCTR1 Frame rate ctrl
        self._wcd(b'\xb6', b'\x08\x82\x27')  # DFUNCTR
        self._wcd(b'\xf2', b'\x00')  # ENABLE3G Enable 3 gamma ctrl
        self._wcd(b'\x26', b'\x01')  # GAMMASET Gamma curve selected
        self._wcd(b'\xe0', b'\x0F\x31\x2B\x0C\x0E\x08\x4E\xF1\x37\x07\x10\x03\x0E\x09\x00')  # GMCTRP1
        self._wcd(b'\xe1', b'\x00\x0E\x14\x03\x11\x07\x31\xC1\x48\x08\x0F\x0C\x31\x36\x0F')  # GMCTRN1
        #self._wcmd(b'\x11')  # SLPOUT Exit sleep
        self.sleep(enable=False)  # exit sleep
        sleep_ms(100)
        #self._wcmd(b'\x29')  # DISPLAY_ON
        #self._led.value(1)   # 2023-1007 PP added - backlight is on -> included in display_on
        self.rotate()    # update display according to _rotation value
        self.display_on() # DISPLAY_ON
        sleep_ms(100)
        
    # Write a command.
    def _wcmd(self, buf):
        self._dc(0)
        self._cs(0)
        self._spi.write(buf)
        self._cs(1)

    # Write a command followed by a data arg.
    def _wcd(self, command, data):
        self._dc(0)
        self._cs(0)
        self._spi.write(command)
        self._cs(1)
        self._dc(1)
        self._cs(0)
        self._spi.write(data)
        self._cs(1)

# Time (ESP32 stock freq) 196ms portrait, 185ms landscape.
# mem free on ESP32 43472 bytes (vs 110192)
    @micropython.native
    def show(self):
        clut = ILI9341.lut
        wd = self.width // 2
        ht = self.height
        lb = self._linebuf
        buf = self._mvb
        if self._spi_init:  # A callback was passed
            self._spi_init(self._spi)  # Bus may be shared
        # Commands needed to start data write 
        self._wcd(b'\x2a', int.to_bytes(self.width, 4, 'big'))  # SET_COLUMN
        self._wcd(b'\x2b', int.to_bytes(ht, 4, 'big'))  # SET_PAGE
        self._wcmd(b'\x2c')  # WRITE_RAM
        self._dc(1)
        self._cs(0)
        for start in range(0, wd*ht, wd):  # For each line
            _lcopy(lb, buf[start :], clut, wd)  # Copy and map colors
            self._spi.write(lb)
        self._cs(1)

    async def do_refresh(self, split=4):
        async with self._lock:
            lines, mod = divmod(self.height, split)  # Lines per segment
            if mod:
                raise ValueError('Invalid do_refresh arg.')
            clut = ILI9341.lut
            wd = self.width // 2
            ht = self.height
            lb = self._linebuf
            buf = self._mvb
            # Commands needed to start data write 
            self._wcd(b'\x2a', int.to_bytes(self.width, 4, 'big'))  # SET_COLUMN
            self._wcd(b'\x2b', int.to_bytes(ht, 4, 'big'))  # SET_PAGE
            self._wcmd(b'\x2c')  # WRITE_RAM
            self._dc(1)
            line = 0
            for _ in range(split):  # For each segment
                if self._spi_init:  # A callback was passed
                    self._spi_init(self._spi)  # Bus may be shared
                self._cs(0)
                for start in range(wd * line, wd * (line + lines), wd):  # For each line
                    _lcopy(lb, buf[start :], clut, wd)  # Copy and map colors
                    self._spi.write(lb)
                line += lines
                self._cs(1)  # Allow other tasks to use bus
                await asyncio.sleep_ms(0)
        
    # ======================================
    # 2023-1007 PP added from rdagger-github
    # ======================================
    def display_on(self):
        """turn display on."""
        self._wcmd(b'\x29')  # DISPLAY_ON
        self._led.value(1)   # 2023-1007 PP added - backlight is on
        sleep_ms(100)
    
    def display_off(self):
        """turn display off."""
        self._wcmd(b'\x28')  # DISPLAY_OFF
        self._led.value(0)   # 2023-1007 PP added - backlight is off
        sleep_ms(100)

    def sleep(self, enable=True):
        """Enters or exits sleep mode.
            Args:
                enable (bool): True (default)=Enter sleep mode, False=Exit sleep
        """
        if enable:
            self._wcmd(b'\x10')  # Enter sleep mode
        else:
            self._wcmd(b'\x11')  # Exit sleep mode

    @property
    def rotation(self):
        return self._rotation
    
    @rotation.setter
    def rotation(self, value):
        #print(f"rotation({value}) entered...")
        assert value in self.ROTATE.keys(), 'Rotation must be 0, 90, 180 or 270.'
        self._rotation = value  #self.ROTATE[value] <- commando to rotate display

    def rotate(self, refresh=True):
        """rotate display according to self._rotation value
            refresh: True - update display as well (=default)"""
        data = self.ROTATE[self._rotation]
        #print(f"rotation={self._rotation}, data={data}")
        self._wcd(b'\x36', data)
        if refresh is True:
            self.show()  # required to update display
        sleep_ms(100)

    def is_off_grid(self, xmin, ymin, xmax, ymax):
        """Check if coordinates extend past display boundaries.
        Args:
            xmin (int): Minimum horizontal pixel.
            ymin (int): Minimum vertical pixel.
            xmax (int): Maximum horizontal pixel.
            ymax (int): Maximum vertical pixel.
        Returns:
            boolean: False = Coordinates OK, True = Error.
        """
        if xmin < 0:
            print('x-coordinate: {0} below minimum of 0.'.format(xmin))
            return True
        if ymin < 0:
            print('y-coordinate: {0} below minimum of 0.'.format(ymin))
            return True
        if xmax >= self.width:
            print('x-coordinate: {0} above maximum of {1}.'.format(
                xmax, self.width - 1))
            return True
        if ymax >= self.height:
            print('y-coordinate: {0} above maximum of {1}.'.format(
                ymax, self.height - 1))
            return True
        return False

    # NOT TESTED -> self.block is missing
    def draw_image(self, path, x=0, y=0, w=320, h=240):
        """Draw image from flash.
        Args:
            path (string): Image file path.
            x (int): X coordinate of image left.  Default is 0.
            y (int): Y coordinate of image top.  Default is 0.
            w (int): Width of image.  Default is 320.
            h (int): Height of image.  Default is 240.
        """
        x2 = x + w - 1
        y2 = y + h - 1
        if self.is_off_grid(x, y, x2, y2):
            return
        with open(path, "rb") as f:
            chunk_height = 1024 // w
            chunk_count, remainder = divmod(h, chunk_height)
            chunk_size = chunk_height * w * 2
            chunk_y = y
            if chunk_count:
                for c in range(0, chunk_count):
                    buf = f.read(chunk_size)
                    self.block(x, chunk_y,
                               x2, chunk_y + chunk_height - 1,
                               buf)
                    chunk_y += chunk_height
            if remainder:
                buf = f.read(remainder * w * 2)
                self.block(x, chunk_y,
                           x2, chunk_y + remainder - 1,
                           buf)


