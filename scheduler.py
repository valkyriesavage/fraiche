import time
from model.model import Least_Squares, StormHMM

class Scheduler:

  def __init__(self):
    self.haveFreshSensorData = False
    self.lastFreshSensorDataTime = -1
    self.lastMLRuntime = -1
    self.modelFreshAtTime = -1
    self.modelFreshnessWhenServed = []
    self.model = Least_Squares()
    self.notUpdatedValues = []
    return

  def gotSensorEvent(self, value):
    self.lastFreshSensorDataTime = time.time()
    self.notUpdatedValues.append(value)
    self.__dealWithSensorEvent__(value)

  def __dealWithSensorEvent__(self, value):
    # children implement this
    pass

  def gotClientRequest(self):
    self.modelFreshnessWhenServed.append(
         time.time() - self.modelFreshAtTime)
    self.__dealWithClientRequest__()

  def __dealWithClientRequest__(self):
    # children implement this
    pass

  def timeToRunML(self):
    # children implement this
    pass

  def runML(self):
    self.lastMLRuntime = time.time()
    self.__executeML__()
    self.modelFreshAtTime = time.time()

  def __executeML__(self):
    for value in self.notUpdatedValues:
      self.model.update(value)
    return

class NaiveScheduler(Scheduler):

  def timeToRunML(self):
    return False

  def __dealWithClientRequest__(self):
    self.runML()

class PeriodicScheduler(Scheduler):
  LEARNING_THRESHOLD = 1000000;

  def timeToRunML(self):
    return time.time() - self.lastMLRuntime > LEARNING_THRESHOLD

class HybridScheduler(Scheduler):

  periodicScheduler = PeriodicScheduler()
  naiveScheduler = NaiveScheduler()

  def timeToRunML(self):
    return self.periodicScheduler.timeToRunML() or self.naiveScheduler.timeToRunML()

  def __dealWithSensorEvent__(self, value):
    self.naiveScheduler.gotSensorEvent(value)
    self.periodicScheduler.gotSensorEvent(value)

  def __executeML__(self):
    if self.periodicScheduler.timeToRunML():
      self.periodicScheduler.__executeML__()
    if self.naiveScheduler.timeToRunML():
      self.naiveScheduler.__executeML__()
    return

class SensorBasedScheduler(Scheduler):

  def timeToRunML(self):
    return self.haveFreshSensorData

  def __dealWithSensorEvent__(self, value):
    self.haveFreshSensorData = True

class LowLoadScheduler(Scheduler):
  RECENCY_THRESHOLD = 10000000
  RECENT_REQUESTS_LOW_THRESHOLD = 15
  recentClientRequests = []

  def __dealWithClientRequest__(self):
    self.recentClientRequests.append(time.time())

  def loadIsLow(self):
    '''
    load is low iff
    # requests within RECENCY_THRESHOLD < RECENT_REQUESTS_LOW_THRESHOLD
    '''
    return reduce(lambda x, y: x + y,
                  map(lambda x: 1,
                      filter(lambda x: x + RECENCY_THRESHOLD > time.time(),
                             self.recentClientRequests))) < RECENT_REQUESTS_LOW_THRESHOLD

  def timeToRunML(self):
    runML = self.loadIsLow()
    self.recentClientRequests = []
    return runML

class PredictiveScheduler(Scheduler):

  def __dealWithClientRequest__(self):
    # feed me to a ML algo!
    if not self.clientModel:
      self.clientModel = LeastSquares()
    self.clientModel.update(time.time())

  def timeToRunML(self):
    return self.clientModel.predict()
