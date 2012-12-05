#!/usr/bin/env python
#
# this is required to serialize the client timing data coming in from the client processes

import logging
import os
import time
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket

class MainHandler(tornado.web.RequestHandler):
  def get(self, timing):
    logging.info("time: " + timing)

class Application(tornado.web.Application):
  def __init__(self):
    handlers = [
        (r"/(.*)", MainHandler),
        ]
    settings = dict(
        cookie_secret="it'sarandomcookiesecrethopefullynooneguessesit!",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies=True,
        autoescape=None,
        )
    tornado.web.Application.__init__(self, handlers, **settings)

def main():
  tornado.options.parse_command_line()
  app = Application()
  app.listen('8888')
  tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
  main()
