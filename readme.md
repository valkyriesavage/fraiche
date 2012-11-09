This is a fork from tinajalabs' gateway_raspi

This project is intended to experiment with using the Raspberry Pi as an XBee
gateway, machine learning platform, and web server.  We are experimenting
with different scheduling algorithms to keep client throughput high and also
keep machine learning data fresh.

The system components are as follows:

devices co-located with plants
  * solar panel, moisture sensor, XBee radio, 4 buttons, servo controlling
    open-ness of drip irrigation valve
  * every hour, wake up, take soil moisture reading, and transmit via XBee
  * after transmit, wait several seconds to see if water levels or thresholds
    need to be adjusted (as informed by Pi)
  * four buttons controlling threshold and water amount can wake the device
    for transmit

Raspberry Pi
  * machine learning performed on moisture data from plants, determining what
    times and moisture levels lead to watering.  this data will be used to
    automatically water the plants when the user desires.
  * webserver runs a simple page that displays the moisture level of each plant
    connected to the system.  users can also use this page to adjust settings
    on when the plants should be watered, which are sent to the plant-based
    XBees at next communication
  * XBee mounted on Pi is a gateway for all XBees on plants; it receives
    moisture level readings (which are fed into the machine learning algorithm)
    twice an hour, except when devices are awoken sooner by user interaction

Look at the import commands and you'll see it will require the following python modules:

* pySerial
* tornado
