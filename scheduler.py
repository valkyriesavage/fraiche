class Scheduler:
  import time

  def __init__(self):
    self.haveFreshSensorData = False
    self.lastFreshSensorDataTime = -1
    self.lastMLRuntime = -1
    self.modelFreshAtTime = -1
    return

  def gotSensorEvent(self):
    self.lastFreshSensorDataTIme = time.time()
    self.__dealWithSensorEvent__()

  def __dealWithSensorEvent__(self):
    # children implement this
    pass

  def gotClientRequest(self):
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
    # children implement this
    pass

class NaiveScheduler(Scheduler):

  def timeToRunML(self):
    return False

  def __dealWithClientRequest__(self):
    __executeML__(self)

  def __executeML__(self):
    # do it!
    return

class PeriodicScheduler(Scheduler):
  LEARNING_THRESHOLD = 1000000;

  def timeToRunML(self):
    return time.time() - self.timeSinceLastLearning > self.THRESHOLD

  def runML(self):
    # do it!
    return

class HybridScheduler(Scheduler):

  periodicScheduler = PeriodicScheduler()
  naiveScheduler = NaiveScheduler()

  def timeToRunML(self):
    return self.periodicScheduler.timeToRunML() or self.naiveScheduler.timeToRunML()

  def __dealWithSensorEvent__(self):
    self.naiveScheduler.gotSensorEvent()
    self.periodicScheduler.gotSensorEvent()

  def runML(self):
    # do it!
    return

class SensorBasedScheduler(Scheduler):

  def timeToRunML(self):
    return self.haveFreshSensorData

  def __dealWithSensorEvent__(self):
    self.haveFreshSensorData = True

  def __executeML__(self):
    # do it!
    return

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
                             self.recentClientRequests)))

  def timeToRunML(self):
    runML = self.loadIsLow()
    self.recentClientRequests = []
    return runML

class PredictiveScheduler(Scheduler):

  def __dealWithClientRequest__(self):
    # feed me to a ML algo!
    pass

  def timeToRunML(self):
    # return ML says so
    return False
