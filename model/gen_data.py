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
###    vals.append(random.normalvariate(mu, noise)) # Allows sensor to return nonsensical values
    vals.append(min(max(0, random.normalvariate(mu, noise)), 100)) # Bounds to [0, 100]
  return vals

class Simulation:
  def __init__(self):
    self.moisture = 0

    # Current rate of moisture addition by rain or fog
    self.rain = 0
    self.fog = 0

    # World properties that will indirectly influence moisture
    self.wind = (0, 0) # Current wind strength (North, East)
    self.storm = [0, 0] # Current storm [severity, time left]
    self.temperature = [0, 0] # day and night temperatures

    # Time is organised by:
    #  - Time of day (0 - day, 1 - night)
    #  - Day of season (0, 89)
    #  - Season of year (0, 3 - summer, autumn, winter, spring)
    self.time = [0, 0, 0]

    # System properties
    self.drainage = 0 # Rate at which water drains from soil
    self.absorption = 0 # Rate at which plants absorb water
    self.evaporation = 0 # Base rate of evaporation

  def evaporation(self):
    # Calculate amount of water that evaporates, based on current conditions
    # TODO: decide how wind would influence this
    if self.time[0] == 0:
      return self.temperature[0] * self.evaporation * 2
    else:
      return self.temperature[1] * self.evaporation

  def timestep(self):
    # Update state, with some randomness
    self.moisture -= self.drainage
    self.moisture -= self.absorption
    self.moisture -= self.evaporation()
    self.moisture += self.rain
    self.moisture += self.fog

    # Apply storm
    if self.storm[1] > 0:
      pass

    # Increment time
    self.time[0] += 1
    if self.time[0] == 2:
      self.time[0] = 0
      self.time[1] += 1
      if self.time[1] == 90:
        self.time[1] = 0
        self.time[2] += 1
        if self.time[2] == 4:
          self.time[2] = 0

  def water(self):
    # Simulate a short period of increased moisture
    pass

if __name__ == '__main__':
  for noise in [0, 1] + [i * 3 for i in xrange(1, 20)]:
    vals = gen_noisy_linear_data(90, -2, noise, 20)
    print ' '.join(["%.2f" % val for val in vals])
