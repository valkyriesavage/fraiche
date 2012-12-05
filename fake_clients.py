import logging
import logging.handlers
from math import floor, pi, sin
import multiprocessing
import random
import sys
import time

from client import Client

clients = []
MAX_NUM_CLIENTS = -1

def main(which_client):
  start = time.time()
  clients[which_client].activate()
  clients[which_client].log(str(time.time() - start))

def scale(val, src, dst):
  return ((val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

def randomize_with_sin(counter):
  sined = sin(counter)
  randomized = sined + random.random() - .5
  scaled = scale(randomized, [-1.5, 1.5], [0, MAX_NUM_CLIENTS + 1])
  return int(floor(scaled))

if __name__ == '__main__':
  if not len(sys.argv) >= 2:
    print "usage: " + sys.argv[0] + " numclients"
    print "make sure you ran 'python logging_server.py' beforehand!"
    sys.exit(0)
  MAX_NUM_CLIENTS = int(sys.argv[1])
  for i in range(MAX_NUM_CLIENTS):
    clients.append(Client())
  while True:
    counter = 0
    while counter < 2*pi:
      counter += .001
      client_number = randomize_with_sin(counter)
      for i in range(client_number):
        p = multiprocessing.Process(target=main, args=(i,))
        p.start()
        p.join()
