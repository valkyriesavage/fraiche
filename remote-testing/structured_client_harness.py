import random
from math import floor, pi, sin
from multiprocessing import Process

from client import Client

MAX_NUM_CLIENTS = 5

clients = []
for i in range(MAX_NUM_CLIENTS):
  clients.append(Client())

def main(which_client):
  clients[which_client].activate()

def scale(val, src, dst):
  return ((val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

def randomize_with_sin(counter):
  sined = sin(counter)
  randomized = sined + random.random() - .5
  scaled = scale(randomized, [-1.5, 1.5], [1, MAX_NUM_CLIENTS + 1])
  return int(floor(scaled))

if __name__ == '__main__':
  while True:
    counter = 0
    while counter < 2*pi:
      counter += .001
      client_number = randomize_with_sin(counter)
      for i in range(client_number):
        p = Process(target=main, args=(i,))
        p.start()
        p.join()
