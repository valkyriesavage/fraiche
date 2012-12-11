#!/usr/bin/env python

import sys, random, time

class Model:
  def __init__(self):
    pass

  def update(self, nval):
    pass

  def predict(self, steps_ahead):
    pass

class Least_Squares(Model):
  def __init__(self):
    self.av_delta = 0.0
    self.pval = None
    self.history = 10.0

  def update(self, nvals):
    if type(nvals) != type([]):
      nvals = [nvals]
    for nval in nvals:
      if self.pval is not None:
        delta = float(nval) - self.pval
        self.av_delta *= (self.history - 1) / self.history
        self.av_delta += delta / self.history
      self.pval = float(nval)
      time.sleep(0.002)

  def predict(self, steps_ahead):
    if self.pval is None:
      return 0
    return self.pval + self.av_delta * steps_ahead

class StormHMM(Model):
  def __init__(self, states=4):
    self.tras_mat = [[0 for i in xrange(states)] for j in xrange(states)]
    self.emit_mat = [0 for i in xrange(states)]

  def train(self, data):
    pass

  def update(self, nval):
    pass

  def predict(self, steps_ahead):
    # Very much a stub...
    time.sleep(1)
    return random.randint(10, 100)


if __name__ == '__main__':
  for line in sys.stdin:
    vals = [float(val) for val in line.strip().split()]
    print "vals:", ' '.join(["%.2f" % val for val in vals])
    model = Least_Squares()
    model.update(vals)
    print "sls:", ' '.join([str(model.predict(steps)) for steps in xrange(20)])
