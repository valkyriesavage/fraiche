import time
from model.model import Least_Squares, StormHMM

class Scheduler:

  def __init__(self, fname):
    self.haveFreshSensorData = False
    self.lastFreshSensorDataTime = -1
    self.lastMLRuntime = -1
    self.modelFreshAtTime = -1
    self.model = {}
    self.notUpdatedValues = []
    self.modelFreshnessWhenServed = open('freshness-data/' + fname, 'w+')
    return

  def gotSensorEvent(self, plant_num, value):
    if plant_num not in self.model:
      self.model[plant_num] = Least_Squares()
    self.lastFreshSensorDataTime = time.time()
    self.notUpdatedValues.append((plant_num, value))
    self.__dealWithSensorEvent__(plant_num, value)

  def __dealWithSensorEvent__(self, plant_num, value):
    # children implement this
    pass

  def gotClientRequest(self, plant_name):
    plant_num = plant_name.split('_')[-1]
    self.modelFreshnessWhenServed.write(
         str(time.time() - self.modelFreshAtTime) + '\n')
    self.__dealWithClientRequest__(plant_num)

  def __dealWithClientRequest__(self, plant_num):
    # children implement this
    pass

  def timeToRunML(self):
    # children implement this
    pass

  def runMLPredict(self, plant_num):
    return self.__executeMLPredict__(plant_num)

  def __executeMLPredict__(self, plant_num):
    return self.model[plant_num].predict(1)

  def runMLUpdate(self):
    if not self.timeToRunML():
      return
    self.lastMLRuntime = time.time()
    self.__executeMLUpdate__()
    self.modelFreshAtTime = time.time()

  def __executeMLUpdate__(self):
    print self.notUpdatedValues
    for num in self.model:
      self.model[num].update([val[1] for val in self.notUpdatedValues if val[0] == num])

class NaiveScheduler(Scheduler):

  def timeToRunML(self):
    return False

  def __dealWithClientRequest__(self, plant_num):
    self.runMLUpdate()
    return self.runMLPredict(plant_num)

class PeriodicScheduler(Scheduler):
  LEARNING_THRESHOLD = 5*60*1000;

  def timeToRunML(self):
    return time.time() - self.lastMLRuntime > LEARNING_THRESHOLD

class HybridScheduler(Scheduler):

  periodicScheduler = PeriodicScheduler('ignoreme')
  naiveScheduler = NaiveScheduler('ignoremetoo')

  def timeToRunML(self):
    return self.periodicScheduler.timeToRunML() or self.naiveScheduler.timeToRunML()

  def __dealWithSensorEvent__(self, plant_num, value):
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

  def __dealWithSensorEvent__(self, plant_num, value):
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
    if runML:
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
