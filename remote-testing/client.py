from splinter import Browser

class Client():
  def __init__(self):
    self.b = Browser()
    self.url = "http://169.229.63.33:8888/?plant=1"

  def activate(self):
    self.b.visit(self.url)

if __name__ == '__main__':
  c = Client()
  c.activate()
