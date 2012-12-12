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

def scale(val, src, dst):
  return ((val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

def randomize_with_sin(counter):
  sined = sin(counter)
  randomized = sined + random.random() - .5
  scaled = scale(randomized, [-1.5, 1.5], [0, MAX_NUM_CLIENTS + 1])
  return int(floor(scaled))

if __name__ == '__main__':
  if not len(sys.argv) >= 4:
    print "usage: " + sys.argv[0] + " numclients numplantsperclient delay"
    sys.exit(0)
  MAX_NUM_CLIENTS = int(sys.argv[1])
  plants_per_client = int(sys.argv[2])
  delay = int(sys.argv[3])
  for i in range(MAX_NUM_CLIENTS):
    clients.append(Client(range(i*plants_per_client,
                                (i+1)*plants_per_client)))
  while True:
    counter = 0
    while counter < 2*pi:
      counter += .1
      client_number = randomize_with_sin(counter)
      processes = []
      for i in range(client_number):
        p = multiprocessing.Process(target=main, args=(i,))
        p.start()
        processes.append(p)
      for p in processes:
        p.join()

      time.sleep(delay)
