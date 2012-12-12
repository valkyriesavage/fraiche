import random, subprocess, time

class Client():
  PHANTOM = "phantomjs"
  WAITFOR = "testing/waitfor.js"

  def __init__(self, plants):
    self.plants = plants

  def activate(self):
    plant = random.choice(self.plants)
    print str(plant) + " start at " + str(time.time())
    params = [Client.PHANTOM, Client.WAITFOR, str(plant)]
    subprocess.check_call(params)

if __name__ == '__main__':
  c = Client([0,1,2,3,4])
  c.activate()
