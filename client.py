from splinter import Browser

class Client():
  def __init__(self):
    self.b = Browser()
    self.url = "http://169.229.63.33:8888/?plant=1"
    self.logging_url = "http://localhost:8888/"

  def activate(self):
    self.b.visit(self.url)
    while not self.b.evaluate_script("incoming_data.length") > 2:
      pass

  def log(self, timing):
    self.b.visit(self.logging_url + timing)

if __name__ == '__main__':
  c = Client()
  c.activate()
