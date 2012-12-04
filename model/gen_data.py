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
    self.moisture = 20

    # Current rate of moisture addition by rain or fog
    self.fog = 10
    self.storm = [0, 0] # Current storm [rain, time left]

    # World properties that will indirectly influence moisture
    self.wind = (0, 0) # Current wind strength (North, East)
    self.temperature = [25, 15] # day and night temperatures

    # Time is organised by:
    #  - Time of day (0 - day, 1 - night)
    #  - Day of season (0, 89)
    #  - Season of year (0, 3 - summer, autumn, winter, spring)
    self.time = [0, 0, 0]

    # System properties
    self.drainage = 5 # Rate at which water drains from soil
    self.absorption = 10 # Rate at which plants absorb water
    self.evaporation_coeff = 0.5 # Base rate of evaporation


  def timestep(self):
    # Update state, with some randomness
    self.moisture -= self.drainage
    self.moisture -= self.absorption
    self.moisture += self.fog

    # Apply storm
    if self.storm[1] > 0:
      self.moisture += self.storm[0]
      self.storm[1] -= 1
    else:
      # Start a storm with 10% probability
      if random.random() < 0.1 * 10 / abs(self.temperature[self.time[0]]):
        self.storm[0] = random.random() * 20
        self.storm[1] = random.randint(1, 20)
    
    # Apply evaporation
    if self.storm[1] == 0:
      self.moisture -= self.temperature[self.time[0]] * self.evaporation_coeff * 2
    else:
      self.moisture -= self.temperature[self.time[0]] * self.evaporation_coeff / 3
    self.moisture = max(0, self.moisture)

    # Increment time and update params
    self.time[0] += 1
    if self.time[0] == 2:
      self.time[0] = 0
      self.time[1] += 1
      if self.time[1] == 90:
        self.time[1] = 0
        self.time[2] += 1
        if self.time[2] == 1:
          self.temperature = [20, 10]
        elif self.time[2] == 2:
          self.temperature = [10, 2]
        elif self.time[2] == 3:
          self.temperature = [20, 15]
        elif self.time[2] == 4:
          self.temperature = [25, 15]
        if self.time[2] == 4:
          self.time[2] = 0

  def water(self, amount):
    # Simulate a short period of increased moisture
    self.moisture += amount

  def get_approximate_state(self):
    moisture  = (random.random()*0.2 + 0.9) * self.moisture + random.random() * 5
    fog  = (random.random()*0.5 + 0.75) * self.fog
    rain  = (random.random()*0.3 + 0.85) * self.storm[0]
    wind0  = (random.random()*0.2 + 0.8) * self.wind[0]
    wind1  = (random.random()*0.2 + 0.8) * self.wind[1]
    temp  = (random.random()*0.3 + 0.85) * self.temperature[self.time[0]]
    time = self.time
    return (moisture, fog, rain, wind0, wind1, temp, time)

  def get_exact_state(self):
    return (self.moisture,
      self.fog,
      self.storm,
      self.wind,
      self.temperature,
      self.time,
      self.drainage,
      self.absorption,
      self.evaporation_coeff)

if __name__ == '__main__':
  world = Simulation()
  pstate = None
  for i in xrange(10000):
    state = world.get_approximate_state()
    if pstate is not None:
      print state[0]
    pstate = state
    if random.random() > 0.2:
      world.water(10)
    world.timestep()

###  for noise in [0, 1] + [i * 3 for i in xrange(1, 20)]:
###    vals = gen_noisy_linear_data(90, -2, noise, 20)
###    print ' '.join(["%.2f" % val for val in vals])
