#!/usr/bin/env python

import sys, random

class Model:
  def __init__(self):
    pass

class Least_Squares(Model):
  def __init__(self):
    self.sum_1 = 0.0
    self.sum_x = 0.0
    self.sum_x2 = 0.0
    self.sum_y = 0.0
    self.sum_xy = 0.0

  def update(self, nval):
    y = float(nval)
    x = self.sum_1 + 1
    self.sum_1 += 1.0
    self.sum_x += x
    self.sum_x2 += x * x
    self.sum_y += y
    self.sum_xy += x * y

  def get_line(self):
    av_xy = self.sum_xy / self.sum_1
    av_y = self.sum_y / self.sum_1
    av_x = self.sum_x / self.sum_1
    av_x2 = self.sum_x2 / self.sum_1
    beta = (av_xy - av_x * av_y) / (av_x2 - av_x * av_x)
    alpha = av_y - beta * av_x
    return (alpha, beta)

  def multiupdate(self, vals):
    for val in vals:
      self.update(val)

if __name__ == '__main__':
  for line in sys.stdin:
    vals = [float(val) for val in line.strip().split()]
    print "vals:", ' '.join(["%.2f" % val for val in vals])
    model = Least_Squares()
    model.multiupdate(vals)
    print "sls:", model.get_line()
