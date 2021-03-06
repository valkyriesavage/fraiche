import time
from model.model import Least_Squares, StormHMM

class Scheduler:

  def __init__(self, fname, logging):
    self.haveFreshSensorData = False
    self.lastFreshSensorDataTime = -1
    self.modelFreshAtTime = -1
    self.model = {}
    self.notUpdatedValues = []
    self.modelFreshnessWhenServed = logging
    self.recentClientRequests = [0]
    return

  def gotSensorEvent(self, plant_num, value):
    if plant_num not in self.model:
      self.model[plant_num] = Least_Squares()
    self.lastFreshSensorDataTime = time.time()
    self.notUpdatedValues.append((plant_num, value))

    # Apply scheduler specific actions
    self.__dealWithSensorEvent__(plant_num, value)

  def __dealWithSensorEvent__(self, plant_num, value):
    # children implement this
    pass

  def gotClientRequest(self, plant_name):
    plant_num = plant_name.split('_')[-1]
    if plant_num not in self.model:
      self.model[plant_num] = Least_Squares()
    # Apply scheduler specific actions
    self.__dealWithClientRequest__(plant_num)

    # Record request freshness
    if self.modelFreshAtTime < 0:
      self.modelFreshnessWhenServed.info("freshness : NAN")
    else:
      self.modelFreshnessWhenServed.info("freshness : " +
           str(time.time() - self.modelFreshAtTime))

    # Return prediction
    return self.model[plant_num].predict(1)

  def __dealWithClientRequest__(self, plant_num):
    # children implement this
    pass

  def considerMLUpdate(self):
    # Periodically called by tornado
    if not self.isTimeToRunML():
      return
    self.__executeMLUpdate__()

  def isTimeToRunML(self):
    # children implement this
    pass

  def __executeMLUpdate__(self):
    for num in self.model:
      self.model[num].update([val[1] for val in self.notUpdatedValues if val[0] == num])
    self.notUpdatedValues = []
    self.modelFreshAtTime = time.time()

class NaiveScheduler(Scheduler):
  def isTimeToRunML(self):
    return False

  def __dealWithClientRequest__(self, plant_num):
    self.__executeMLUpdate__()
    self.modelFreshAtTime = time.time()

class PeriodicScheduler(Scheduler):
  LEARNING_THRESHOLD = 5*60*1000;

  def isTimeToRunML(self):
    if self.modelFreshAtTime < 0:
      return True
    return time.time() - self.modelFreshAtTime > self.LEARNING_THRESHOLD

class HybridScheduler(Scheduler):

  def __init__(self, fname, logging):
    self.periodicScheduler = PeriodicScheduler('ignoreme', logging)
    self.haveFreshSensorData = False
    self.lastFreshSensorDataTime = -1
    self.modelFreshAtTime = -1
    self.model = {}
    self.notUpdatedValues = []
    self.modelFreshnessWhenServed = logging

  def isTimeToRunML(self):
    return self.periodicScheduler.isTimeToRunML()

  def __dealWithClientRequest__(self, plant_num):
    self.__executeMLUpdate__()
    self.modelFreshAtTime = time.time()

class SensorBasedScheduler(Scheduler):
  def isTimeToRunML(self):
    return False

  def __dealWithSensorEvent__(self, plant_num, value):
    self.__executeMLUpdate__()
    self.modelFreshAtTime = time.time()

class LowLoadScheduler(Scheduler):

  def __dealWithClientRequest__(self, plant_num):
    self.recentClientRequests.append(time.time())

  def loadIsLow(self):
    RECENCY_THRESHOLD = 10000000
    RECENT_REQUESTS_LOW_THRESHOLD = 3
    '''
    load is low iff
    # requests within RECENCY_THRESHOLD < RECENT_REQUESTS_LOW_THRESHOLD
    '''
    recent_requests =  reduce(lambda x, y: x + y,
                              map(lambda x: 1,
                                  filter(lambda x: x + RECENCY_THRESHOLD > time.time(),
                                         self.recentClientRequests)))
    return recent_requests < RECENT_REQUESTS_LOW_THRESHOLD

  def isTimeToRunML(self):
    if self.loadIsLow():
      self.recentClientRequests = []
      return True
    else:
      return False

class PredictiveScheduler(Scheduler):
  last_request = 0
  av_diff = 0
  queries = 0

  def __dealWithClientRequest__(self, plant_num):
    cur = time.time()
    time_since = cur - self.last_request
    self.av_diff = self.av_diff * (self.queries / float(self.queries+1)) + (time_since / float(self.queries+1))
    self.queries += 1
    self.last_request = cur

  def isTimeToRunML(self):
    return time.time() > 0.7*self.av_diff + self.last_request
