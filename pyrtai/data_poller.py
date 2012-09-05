# @package data_poller
# Retrieves data from the datastream queue

from threading import Thread

import random
import time

class DataPoller(Thread):
    ## @var observers
    # The generic observers to call when a new data string arrives

    ## @var queue
    # The datastream queue

    ## @var decimation
    # Decimation of the trace

    ## @var sample_time
    # Sampling time of the trace

    ## @var done
    # Flag to stop the thread

    ## @var cycle
    # The ID cycle we are currently in, which became 0 after 65536

    ## Initializes the object setting the queue and the thread
    # @param queue
    # @param decimation The decimation to use. 1.0 if false
    def __init__(self, queue, decimation = None):
        self.observers = []
        self.queue = queue
        self.cycle = 0
        # sample_time is safely initialized at 0.1 but it has to be set
        # calling updateSampleTime with real value for the channel
        # BEFORE starting this thread
        self.sample_time = 0.1

        if decimation:
            self.decimation = decimation
        else:
            self.decimation = 1.0
        Thread.__init__(self)
        self.name = "DataPoller"
        self.daemon = True

    ## Sets sample time
    # @param sample_time The sample time of the signal
    def updateSampleTime(self, sample_time):
        self.sample_time = float(sample_time)
        
    ## Stops thread
    def stop(self):
        # Poison
        self.queue.insert(0, None)
        self.done = True
        #self.stopObservers()

    ## Gets the stream from the queue and notifies the observers
    def run(self):
        # Set the conditional flag to true
        self.done = False
        while not self.done:
            if len(self.queue):

                line = self.queue.pop() # line: "ID_canale id_sample n_canali"
                if line:
                    # TODO: ID_canale puo' essere negativo (LED)
                    splitted_line = line.split(" ")

                    structured_data = {}
                    id_number = int(splitted_line[1]) + (65535*self.cycle)
                    structured_data['id'] = id_number
                    structured_data['traces'] = splitted_line[2:]
                    structured_data['channel'] = (int(splitted_line[0]) if splitted_line[0] else None)
                    ## Time calculation using cycle number
                    structured_data['time'] = (float(id_number) * float(self.decimation) * float(self.sample_time))

                    # Increments cycle
                    if int(splitted_line[1]) == 65535:
                        self.cycle += 1

                    self.updateObservers(structured_data)
            else:
                #print "Empty queue"
                time.sleep(0.5)

    ## Add a new observer "update" method to the list of observers.
    # @param update_method Is the method of the observer which will be called when new data arrives. The method name is arbitrary, but it must accept a string parameter
    # @param channel The (optional) channel on which observers to be notified are registered
    # @return The ID of the observer, to be used to remove the observer
    def addObserver(self, update_method, channel):
        new_observer = {}

        # Security check to avoid the same id
        ids = []
        for observer in self.observers:
            ids.append(observer['id'])

        random_id = str(random.getrandbits(64))
        while random_id in ids:
            random_id = str(random.getrandbits(64))

        # Now I'm sure random_id is unique :)
        new_observer['id'] = random_id
        new_observer['method'] = update_method
        # Channel is None for "generic" observers
        new_observer['channel'] = channel

        self.observers.append(new_observer)

        return new_observer['id']

    ## Removes the observer
    # @param observer_id The ID of the observer to remove
    # @return False if the observer isn't in the observers list, True if it was correctly removed
    def stopObservers(self):
        for observer in self.observers:
          observer['method'](None)

    ## Removes the observer
    # @param observer_id The ID of the observer to remove
    # @return False if the observer isn't in the observers list, True if it was correctly removed
    def removeObserver(self, observer_id):
        try:
            for observer in self.observers:
                if observer['id'] == observer_id:
                    self.observers.remove(observer)
                    return True
        except ValueError:
            return False

    ## Update the observers with the new data
    # @param data The data to send to observers
    def updateObservers(self, data):
        for observer in self.observers:
            try:
                print("Updating observer")
                # Send data to observers registered to the channel or generic observers (channel == None)
                if observer['channel'] == data['channel'] or observer['channel'] == None:
                    observer['method'](data)
                    print("Updated")
            except AttributeError:
                print "An error occurred while updating an observer"
                continue
