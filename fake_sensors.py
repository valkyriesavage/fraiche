#!/usr/bin/env python

from model.gen_data import Simulation

print "Sensor Manager..."
print "CS294-84 project based on code from Tinaja labs"
print "-----------------------------------------------"

import os, syslog, time, urllib
from server import log_data_file

world = Simulation()

##############################################################
# the main function
def mainloop(idleevent):
  plant_num = '0'
  state = str(world.get_approximate_state()[0])

  # log the data
  log_data(plant_num, state)
  alert_server(plant_num, state)

ZERO_BYTES_FROM = 0
FILE_END = 2

def log_data(plant_num, sensor_value):
  oclock = time.time()
  lf = open(log_data_file(plant_num), "w+")
  lf.seek(ZERO_BYTES_FROM, FILE_END)
  lf.write(str(oclock) + " " + sensor_value + "\n")

def alert_server(plant_num, sensor_data):
  urllib.urlopen('http://127.0.0.1:8888/sensorupdated/' + plant_num + '/' + sensor_data)

# open up the serial port to get data transmitted to xbee
syslog.syslog("<<<  Starting the Smart Watering Sensor System for H2OIQ  >>>")

while True:
  mainloop(None)
  time.sleep(2)
