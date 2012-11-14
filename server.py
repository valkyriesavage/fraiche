#!/usr/bin/env python
#
# Based off example code found in the Tornado package, and code from
# the tinaja labs xbee package.

import datetime, logging, math, os, random, serial, sys, syslog, time, uuid

import tornado.escape
import tornado.ioloop
import tornado.options
from tornado.options import define, options
import tornado.web
import tornado.websocket

from xbee import xbee

import sensorhistory

define("port", default=8888, help="run on the given port", type=int)

SERIALPORT = "/dev/ttyAMA0"
BAUDRATE = 9600
'''
# open up the serial port to get data transmitted to xbee
try:
    ser = serial.Serial(SERIALPORT, BAUDRATE)
    ser.open()
    print "h2oiq - serial port opened..."
    syslog.syslog("h2oiq.opening: serial port opened...")
except Exception, e:
    print "Serial port exception: "+str(e)
    syslog.syslog("h2oiq.opening exception: serial port: "+str(e))
    # in test mode, we want to let it run, anyway
    #exit
'''
class Application(tornado.web.Application):
  def __init__(self):
    handlers = [
        (r"/plant/(.*)", WaterDataSocketHandler),
        (r"/*", MainHandler),
        ]
    settings = dict(
        cookie_secret="it'sarandomcookiesecrethopefullynooneguessesit!",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies=True,
        autoescape=None,
        )
    tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
  def get(self):
    self.render("index.html", messages=WaterDataSocketHandler.instructions)

class WaterDataSocketHandler(tornado.websocket.WebSocketHandler):

  clients = {}
  instructions = []

  def allow_draft76(self):
    # for iOS 5.0 Safari
    return True

  def open(self, plant_num):
    WaterDataSocketHandler.clients[plant_num] = self
    self.plant_num = plant_num
    logging.info("got client for plant " + plant_num)

  def on_close(self):
    del WaterDataSocketHandler.clients[self.plant_num]

  @classmethod
  def update_cache(cls, instruction):
    cls.instructions.append(instruction)

  @classmethod
  def send_updates(cls, data):
    try:
      clients[data[plant_num]].write_message(data)
    except:
      logging.error("Error sending message", exc_info=True)

  def on_message(self, instruction):
    logging.info("got message %r", instruction)
    parsed = tornado.escape.json_decode(instruction)
    WaterDataSocketHandler.update_cache(instruction)

def main():
  tornado.options.parse_command_line()
  app = Application()
  app.listen(options.port)
  tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
  main()
