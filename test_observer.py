## A very simple observer to register to the target.
# Useful for debugging purpose
from threading import Thread
import time
class TestObserver(Thread):
    ## @var data
    # The structured data from the signal channel of the target
    def __init__(self, timeout = 0):
        Thread.__init__(self)
        self.name = 'Observer'
        self.daemon = True
        self.timeout = timeout
        self.initial_time = time.time()
        self.data = None

    def setLine(self, data):
        self.data = data
        
    def printLine(self, wait_time):
      # TODO: Pulire il timeout
      #if self.cycle >= self.timeout:
      #  self.cycle = 0
      if self.data:
        print "ID:{0}\nTraces: {1}\nTime: {2}\n".format(self.data['id'], self.data['traces'], self.data['time'])
        print("DELTA: %f" % (float(wait_time) - float(self.data['time'])))
      #else:
      #  self.cycle += 1
    
    def run(self):
      while(True):
        wait_time = time.time() - self.initial_time
        print ("TEMPO: %f" % wait_time)
        self.printLine(wait_time)
        time.sleep(int(self.timeout))
