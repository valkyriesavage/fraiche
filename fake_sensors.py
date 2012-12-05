#!/usr/bin/env python

import os, syslog, time, urllib, sys

from server import log_data_file
from model.gen_data import Simulation

##############################################################
# the main function
def mainloop(world, plants):
  for i in xrange(plants):
    plant_num = str(i)
    state = str(world.get_approximate_state()[0])
    log_data(plant_num, state)
    alert_server(plant_num, state)

def log_data(plant_num, sensor_value):
  oclock = time.time()
  lf = open(log_data_file(plant_num), "a")
  lf.write(str(oclock) + " " + sensor_value + "\n")
  lf.close()

def alert_server(plant_num, sensor_data):
  urllib.urlopen('http://127.0.0.1:8888/sensorupdated/' + plant_num + '/' + sensor_data)

if __name__ == '__main__':
  world = Simulation()
  if len(sys.argv) == 1:
    print "Usage:"
    print "%s <number of plants> <delay in seconds>" % sys.argv[0]
    sys.exit(0)
  plants = int(sys.argv[1])
  wait_time = float(sys.argv[2])

  print "Sensor Manager..."
  print "CS294-84 project based on code from Tinaja labs"
  print "-----------------------------------------------"
  # open up the serial port to get data transmitted to xbee
  syslog.syslog("<<<  Starting the Smart Watering Sensor System for H2OIQ  >>>")

  while True:
    mainloop(world, plants)
    time.sleep(wait_time)
    world.timestep()
