#!/usr/bin/env python

import sys, random

monthly_precip = [126.5, 132.3, 98, 42.2, 21.8, 3.8, 0.3, 1.5, 6.1, 34.8, 83.8, 128]

'''
Intention:  This is for a community garden, where they cannot easily install
plumbing, but can set up wireless sensors, and have a raspberry pi in the
middle, reminding people to go water their plants

Relevant points:
 - moisture content can vary at different soil depths
 - different plants require different amounts of moisture
 - morning is best, midday the sun is an issue, evening there are risks like mildew

So we want to predict future moisture levels, so we can remind people to water
plants in advance (they can't just appear when it drops below a level).

Models:
 - Simplest, use a single sensor, try to fit a line, see when it will fall below a given level
 - Next, have some global information about expected rainfall
 - Next, incorporate multiple sensors
'''

def gen_noisy_linear_data(start, slope, noise, timesteps):
  vals = []
  for i in xrange(timesteps):
    mu = start + i * slope
    vals.append(random.normalvariate(mu, noise)) # Allows sensor to return nonsensical values
###    vals.append(min(max(0, random.normalvariate(mu, noise)), 100)) # Bounds to [0, 100]
  return vals

#### Factors
### - rate at which plant uses water
### - rainfall
### - watering (i.e. brief period of very heavy rain)
### - fog / mist
### - sunlight
### - wind
### - soil type
### - 

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

print "See how well simple least squares handles noise:"
for noise in [0, 1] + [i * 3 for i in xrange(1, 20)]:
  vals = gen_noisy_linear_data(90, -2, noise, 20)
  print "sigma:", noise
  print "vals:", ' '.join(["%.2f" % val for val in vals])
  model = Least_Squares()
  model.multiupdate(vals)
  print "sls:", model.get_line()
