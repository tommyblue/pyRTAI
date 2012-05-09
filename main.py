## This file shows some basic action of the library

from pyrtai.rtai_server import RtaiServer
from test_observer import TestObserver

# Get the first slave
rtai = RtaiServer("EASYHW")

# Get the slave target
target = rtai.getTarget()

params = target.getParameters()

## ESEMPIO DI PARAMS
ex_params = [
    {
     'block_name': 'testsine/gain', 
     'rows': 1, 
     'values': [1.0], 
     'cols': 1, 
     'param_name': 'Value[0]'
    }, 
    {
     'block_name': 'testsine/RPARAM[2]', 
     'rows': 1, 
     'values': [1.0], 
     'cols': 1, 
     'param_name': 'Value[0]'
    }, 
    {
     'block_name': 'testsine/RPARAM[2]', 
     'rows': 1, 
     'values': [50.0], 
     'cols': 1, 
     'param_name': 'Value[1]'
    }, 
    {
     'block_name': 'testsine/RPARAM[2]', 
     'rows': 1, 
     'values': [0.0], 
     'cols': 1, 
     'param_name': 'Value[2]'
    }, 
    {
     'block_name': 'testsine/RPARAM[2]', 
     'rows': 1, 
     'values': [0.0], 
     'cols': 1, 
     'param_name': 'Value[3]'
    }, 
    {
     'block_name': 'testsine/RPARAM[2]', 
     'rows': 1, 
     'values': [0.0], 
     'cols': 1, 
     'param_name': 'Value[4]'
    }, 
    {
     'block_name': 'testsine/IPARAM[1]', 
     'rows': 1, 
     'values': [1.0], 
     'cols': 1, 
     'param_name': 'Value[0]'
    }
]


#target.disconnect()
#target.close()
#slave.stop()
#master.stop()
# TODO: rtai.stop()

# Removes it
#target.removeObserver(observer_id)

##
## SIGNAL STRUCTURE
##
signals = target.getSignalStructure()

# Channel 0
channel = signals[0]['number']
# channel == signal_number
sample_time = signals[0]['sample_time']

# Devo ciclare!
# for signal in signals:
#    print signal['number'] #ecc.

##
## REGISTER A SIMPLE OBSERVER
##
observer_1 = TestObserver()
observer_id_1 = target.addObserver(observer_1.getLine, sample_time, None, channel)

observer_2 = TestObserver()
observer_id_2 = target.addObserver(observer_2.getLine, sample_time, None, channel)

observer_3 = TestObserver()
observer_id_3 = target.addObserver(observer_3.getLine, sample_time, None, channel)

##
## START DATA SIGNAL
##
if target.startData(channel, sample_time):
    print ("Started signal %d" % channel)
else:
    print ("Can't start signal %d" % channel)


# stopData()

## Stop everything
rtai.halt()