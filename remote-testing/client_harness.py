import random
from math import pi
from multiprocessing import Process

from client import Client

NUM_CLIENTS = 5

clients = []
for i in range(NUM_CLIENTS):
  clients.append(Client())

def main(which_client):
  clients[which_client].activate()

if __name__ == '__main__':
  while True:
    client_number = random.nextInt(NUM_CLIENTS)
    for i in range(client_number):
      p = Process(target=main, args=(i,))
      p.start()
      p.join()
