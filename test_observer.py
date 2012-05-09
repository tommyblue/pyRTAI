## A very simple observer to register to the target.
# Useful for debugging purpose
class TestObserver:
    ## @var data
    # The structured data from the signal channel of the target
    
    def getLine(self, data):
        self.data = data
        
    def printLine(self, data):
        print "ID: %s\nTraces: %f\nTime: %f\n" % (data['id'], data['traces'], data['time'])