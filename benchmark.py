"""
benchmark - In this simple benchmark, we compare two ways of 
finding the amplitude of a signal. 

* normalized_rms computes it in a traditional way, 
   handling each number one by one in Python code.

* normalized_rms_ulab computes more quickly by working on 
  groups of numbers in a ulab array at the same time.  

* ulab.numerical.std computes most quickly by moving all 
  operations from Python to ulab.

URL:
https://learn.adafruit.com/ulab-crunch-numbers-fast-with-circuitpython/a-simple-benchmark


Firmware esp32 micropython with ulab 0.5.4
https://gitlab.com/rcolistete/micropython-samples/-/tree/master/Pyboard/Firmware


2020-1101 PP adopted to firmware including ulab 0.5.4
             and vanilla MicroPython - see comments.

"""
import time
import math
import ulab
# not neccessay for firmware: import ulab.numerical


def mean(values):
    return sum(values) / len(values)


def normalized_rms(values):
    minbuf = int(mean(values))
    samples_sum = sum(
        float(sample - minbuf) * (sample - minbuf)
        for sample in values
    )
    return math.sqrt(samples_sum / len(values))


def normalized_rms_ulab(values):
    # this function works with ndarrays only
    minbuf = ulab.numerical.mean(values)
    values = values - minbuf
    samples_sum = ulab.numerical.sum(values * values)
    return math.sqrt(samples_sum / len(values))


def timeit(s, f, n=100):
    # circuitpython: t0 = time.monotonic_ns()
    t0 = time.ticks_us()
    for _ in range(n):
        x = f()
    # circuitpython: t1 = time.monotonic_ns()
    t1 = time.ticks_us()
    r = (t1 - t0) * 1e-3 / n # circuitpython: 1e-6 / n
    print("%-30s : %8.3fms [result=%f]" % (s, r, x))


# 2020-1101 PP - added the main function
def run():
    # Instead of using sensor data, we generate some data
    # The amplitude is 5000 so the rms should be around 5000/1.414 = 3536
    nums_list = [int(8000 + math.sin(i) * 5000) for i in range(100)]
    nums_array = ulab.array(nums_list)

    print("Computing the RMS value of 100 numbers")
    timeit("traditional", lambda: normalized_rms(nums_list))
    timeit("ulab, with ndarray, algorithm in python",
            lambda: normalized_rms_ulab(nums_array))
    timeit("ulab only, with list",
            lambda: ulab.numerical.std(nums_list))
    timeit("ulab only, with ndarray",
            lambda: ulab.numerical.std(nums_array))

print("benchmark loaded...")

if __name__ == "__main__":
    run()

    """  2020-1101 results -----------------------------------
    Results in article URL:
    traditional               :    2.951ms [result=3535.843611]
    ulab, algorithm in python :    0.251ms [result=3535.853624]
    ulab only, with list      :    0.336ms [result=3535.854340]
    ulab only, with ndarray   :    0.068ms [result=3535.854340]

    Results from run():
    Computing the RMS value of 100 numbers
    traditional                :    2.908ms [result=3535.854101]
    ulab, algorithm in python  :    0.171ms [result=3535.854340]
    ulab only, with list       :    0.238ms [result=3535.854340]
    ulab only, with ndarray    :    0.041ms [result=3535.854340]
    """
