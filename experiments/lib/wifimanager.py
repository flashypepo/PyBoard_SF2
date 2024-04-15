"""
class wifiManager to try out...
NOT TESTED YET

2020-0512 from https://forum.micropython.org/viewtopic.php?f=20&t=6579
"""
import pyb, network, utime, time, micropython

class WifiManager():
    """
        A pythonic Wifi Manager which will:
        1) Allow you to configure SSID and Password to connect and maintain/check that connection.
        2) Retry and connect if it's been asked to connect and the connection goes down.
        3) Use a WiFi SSID/Password from Flash if it exists.
        4) Encrypt the WiFi SSID/Password on Flash if it does not exist.
        5) Stop a connection and stop the retry/check
        6) Switch to an Access Point mode

        The Wifi manager has internal states for:
        - the current SSID
        - the current password
        - active (i.e. managing a connection )
        - connected
        - last connected local time
    """

    def __init__(self, ssid=None, password=None):
        self.ssid=ssid
        self._password = password
        self._timer = None           # The timer object which handles periodic retries
        self._wifi = network.WLAN(network.STA_IF)  # An instance of the network WLAN manager
        print("WiFi Manager bringing up wlan interface.")
        self.x = 0.1
        self.bar_bound = self.bar

    # 2020-0512 PP added verbose
    def bar(self, bar_value, verbose=False):
        self.x *= 1.2
        if verbose is True:
            print("bar value is: {}".format(bar_value))
            print("SSID is: {}".format(self.ssid))
            # print("Password is: {}".format(self._password))
            print("X value is: {}".format(self.x))
        if self.ssid is None:
            self.ssid = '********'
        if self._password is None:
            self._password = '********'
        self._wifi.connect(self.ssid, self._password)

    def cb(self, timer, verbose=False):
        # Passing self.bar would cause memory allocation failure.
        #print("Timer counter is: {}".format(timer.counter()))      # This causes a timer exception to be thrown when it's part of the callback.
        if verbose is True:
            print(timer.counter())
        micropython.schedule(self.bar_bound, "hello world")

    def connect(self):
        print("connect 2 started.....")
        self._wifi.active(True)  # 2020-0512 added
        self._timer = pyb.Timer(1, freq=0.1)
        self._timer.callback(self.cb)
