"""
Asynchrounous blinking of multiple LEDs

LED configuration:
LED    GPIO
red    GPIO12
blue   GPIO20
green  GPIO21
yellow GPIO16

2021-1129 PP added un-ending blink and keyboardinterrupt
"""
import asyncio
import board
import digitalio


# Don't forget the async!
async def blink(pin, interval, count):
    with digitalio.DigitalInOut(pin) as led:
        led.switch_to_output(value=False)
        for i in range(count):
            led.value = True
            await asyncio.sleep(interval)  # Don't forget the await!
            led.value = False
            await asyncio.sleep(interval)  # Don't forget the await!


# 2021-1129 PP added unending blink
async def blink_unending(pin, interval):
    with digitalio.DigitalInOut(pin) as led:
        led.switch_to_output(value=False)
        while True:
            led.value = True
            await asyncio.sleep(interval)  # Don't forget the await!
            led.value = False
            await asyncio.sleep(interval)  # Don't forget the await!


# main with list of LEDS and tasks
# added leds_off and global leds
def leds_off():
    #DEBUG: print(f"#leds = {len(pins)}"); print(f"pin = {pins}")
    for i in range(len(pins)):
        with digitalio.DigitalInOut(pins[i]) as led:
            led.switch_to_output(value=False)


# LED pins
pins = [board.D21, board.D20, board.D16, board.D12]
async def main(ending=True):
    import random

    # make a list of tasks
    tasks = []
    for led in pins:
        # random frequency and/or count
        freq = random.randint(1, 10) / 10  # range 0.1 .. 0.9
        if ending is True:
            # countable blink
            count = 10 # random.randint(1, 10)  # range 1 .. 10
            # debug: print(led, freq, count)
            task = asyncio.create_task(blink(led, freq, count))
        else:
            # unending blink
            task = asyncio.create_task(blink_unending(led, freq))
        tasks.append(task)

    # Don't forget the await!
    await asyncio.gather(*tasks)  # collect tasks from list
    print('Done')


if __name__ == "__main__":
    '''
    # no graceful stop of program...
    asyncio.run(main())  # ending blink
    '''
    # graceful stop of program with keys Ctrl-C
    try:
        #asyncio.run(main())  # eindigt vanzelf...
        asyncio.run(main(ending=False))
    except KeyboardInterrupt:
        leds_off()
        print('Finished')
    #'''
