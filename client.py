from splinter import Browser
import random

class Client():
  def __init__(self, plants):
    self.b = Browser()
    self.url = "http://169.229.63.33:8888/?plant="
    self.plants = plants
    self.logging_url = "http://localhost:8888/"

  def activate(self):
    self.b.visit(self.url + str(random.choice(self.plants)))
    print("url = " + self.url + str(random.choice(self.plants)))
    while not self.b.evaluate_script("incoming_data.length") > 2:
      pass

  def log(self, timing):
    self.b.visit(self.logging_url + timing)

if __name__ == '__main__':
  c = Client()
  c.activate()
