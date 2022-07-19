"""
led36_demo.py - sample program from https://pybd.io/hw/tile_led36.html
2021-0410 PP new
"""
import time, machine

LED_BROADCAST = 1           # broadcast I2C address
LED_ADDR = 60               # default individual LED36 address

machine.Pin('EN_3V3').on()  # enable power on LED36 bus
i2c = machine.I2C('X')      # select X bus

def cyc(addr, dt=250):
    """ Set all LEDs to black, red, green, yellow, blue, magenta, cayn and white for dt ms
        ramp up brightnes from 0 % to 100 %
    """
    while True:
        try:
            fill_rgb(addr, 100, 100, 100)
            break
        except:
            time.sleep_ms(100)
    for i in range(8):
        fill_rgb(addr, (i & 1) * 255, ((i >> 1) & 1) * 255, ((i >> 2) & 1) * 255)
        time.sleep_ms(dt)
    for i in range(100):
        brightness(addr, i)
        time.sleep_ms(20)

def brightness(addr, b=100):
    """ Set brigntness """
    ba = bytearray(b'\x02\x16 ')
    ba[-1] = b & 0xff
    i2c.writeto(addr, ba)

def bloop(addr, dt=100, maxv=100, inc=1):
    """ Cycle through brigntness ramp """
    b = 0
    while True:
        print(b)
        brightness(addr, b)
        b += inc
        b %= maxv
        time.sleep_ms(dt)

def pump(addr, dt=10, maxv=100):
    """ Cycle through brightness modulation """
    import math
    sinar = []
    for i in range(90):
        sinar.append(int((math.sin(i * 4 / 180 * math.pi) + 1) * maxv / 2))
    i = 0
    while True:
        brightness(addr, sinar[i])
        i += 1
        i %= len(sinar)
        time.sleep_ms(dt)

def fill_rgb(addr, r, g, b):
    """ Fill LED array using set pixel command """
    i2c.writeto(addr, b'\x02X\x00\x00')
    buf = bytearray(b'\x02A   ')
    buf[2] = r
    buf[3] = g
    buf[4] = b
    for i in range(36):
        i2c.writeto(addr, buf)

def illu(addr, r, g, b):
    """ Fill LED array using set illumination command """
    buf = bytearray(b'\x02i   ')
    buf[2] = r
    buf[3] = g
    buf[4] = b
    i2c.writeto(addr, buf)

def fill_frame(addr, r, g, b):
    """ Fill LED array using fill frame command """
    i2c.writeto(addr, b'\x02ml')
    buf = bytearray(b'   ')
    buf[0] = r
    buf[1] = g
    buf[2] = b
    for i in range(36):
        i2c.writeto(addr, buf)

def set_dot(addr, x, y, r, g, b):
    """ Set single LED color at position """
    buf = bytearray(b'\x02X  ')
    buf[2] = x
    buf[3] = y
    i2c.writeto(addr, buf)

    buf = bytearray(b'\x02A   ')
    buf[2] = r
    buf[3] = g
    buf[4] = b
    i2c.writeto(addr, buf)

def fill_raw(addr, r, g, b):
    """ Fill LED array with raw values using fill frame command """
    i2c.writeto(addr, b'\x02nl')
    buf = bytearray(b'   ')
    buf[0] = r
    buf[1] = g
    buf[2] = b
    for i in range(36):
        i2c.writeto(addr, buf)

def led_pins(addr, v):
    """ Permute LED colors (use with care) """
    buf = bytearray(b'\x02\x1c\x00')
    buf[-1] = v & 3
    i2c.writeto(addr, buf)

def random_dots(addr, dt=10):
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
        set_dot(addr, x, y, r, g, b)
        time.sleep_ms(dt)
