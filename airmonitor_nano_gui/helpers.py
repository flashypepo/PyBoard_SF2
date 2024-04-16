# ====================================================
# Helpers
# 2024-0414 PP added print_i2c_devices, print_localtime
# ====================================================

# helper: print information of i2c-display 'ssd'
def print_display_I2C_configuration(ssd, display_name):
    print(f"GUI-nano display: {display_name}")
    print(f"I2C: {ssd.i2c}")
    print(f"\tdimensions (wxh): {ssd.width}x{ssd.height} pixels")


# helper: print information of SPI-display 'ssd'
def print_display_SPI_configuration(ssd, display_name, landscape=False, busy=False):
    print(f"GUI-nano display: {display_name}")
    print(f"\tRST : {ssd._rst}")
    print(f"\tDC  : {ssd._dc}")
    print(f"\tCS  : {ssd._cs}")
    if busy is True:
        print(f"\tBUSY: {ssd._busy}")
    print(f"\tSPI : {ssd._spi}")
    print(f"\tdimensions (wxh): {ssd.width}x{ssd.height} pixels")
    mode = "landscape" if landscape else "portrait"
    print(f"\tmode: {mode}")

# helper: print I2C address of connected I2C devices
def print_i2c_devices(i2c):
    devices = i2c.scan()
    #print(f"I2C devices: {[hex(d) for d in devices]}")
    print(f"I2C devices: {[hex(d) + '('+ str(d) + ')' for d in devices]}")
    print(f"-"*10)

# helper: print local time in readable format
def print_localtime():
    """toont in console lokale tijd en return localtime-tuple"""
    (year, month, mday, hour, minute, second, weekday, yearday) = time.localtime()
    days= {0:"Maandag", 1:"Dinsdag", 2:"Woensdag", 3:"Donderdag", 4:"Vrijdag", 5:"Zaterdag", 6:"Zondag"}
    months = {1:"Januari", 2:"Februari", 3:"Maart", 4:"April", 5:"Mei", 6:"Juni", 7:"Juli", 8:"Augustus", 9:"September", 10:"Oktober", 11:"November", 12:"December"}
    print(f"Vandaag is {days[weekday]} {mday} {months[month]} {year}")
    return (year, month, mday, hour, minute, second, weekday, yearday)

