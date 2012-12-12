#!/usr/bin/env python

import os, syslog, time, urllib, sys, string, random

from server import log_data_file
from model.gen_data import Simulation

##############################################################
# the main function
def mainloop(world, plant_num, use_localhost):
  state = str(world.get_approximate_state()[0])
  log_data(str(plant_num), state)
  alert_server(str(plant_num), state, use_localhost)

def log_data(plant_num, sensor_value):
  oclock = time.time()
  lf = open(log_data_file(plant_num) + '.log.fake', "a")
  lf.write(str(oclock) + " " + sensor_value + "\n")
  lf.close()

def alert_server(plant_num, sensor_data, use_localhost):
  if use_localhost:
    urllib.urlopen('http://127.0.0.1:8888/sensorupdated/' + plant_num + '/' + sensor_data)
  else:
    urllib.urlopen('http://169.229.63.33:8888/sensorupdated/' + plant_num + '/' + sensor_data)

if __name__ == '__main__':
  world = Simulation()
  if len(sys.argv) < 3:
    print "Usage:"
    print "%s <number of plants> <delay in seconds> <localhost? default=False" % sys.argv[0]
    sys.exit(0)
  plants = int(sys.argv[1])
  wait_time = float(sys.argv[2])
  localhost = False
  if len(sys.argv) == 4:
    if 't' in string.lower(sys.argv[3]):
      localhost = True

  # open up the serial port to get data transmitted to xbee
  syslog.syslog("<<<  Starting the Smart Watering Sensor System for H2OIQ  >>>")

  timing = []
  for i in xrange(plants):
    timing.append(random.random() * wait_time)
  timing.sort()
  diffs = [timing[0] + wait_time - timing[-1]]
  for i in xrange(1, len(timing)):
    diffs.append(timing[i] - timing[i-1])

  while True:
    for i in xrange(len(diffs)):
      mainloop(world, i, localhost)
      time.sleep(diffs[i])
    world.timestep()
