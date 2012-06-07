## Standard connection with 2 data streams
from pyrtai.rtai_server import RtaiServer
from test_observer import TestObserver

rtai = RtaiServer("MON")

target = rtai.getTarget()

signals = target.getSignalStructure()

observer_1 = TestObserver(1)
observer_id_1 = target.addObserver(observer_1.setLine, signals[0]['sample_time'], None, signals[0]['number'])
observer_1.start()

observer_2 = TestObserver(1)
observer_id_2 = target.addObserver(observer_2.getLine, signals[1]['sample_time'], None, signals[1]['number'])
observer_2.start()

target.startData(signals[0]['number'], signals[0]['sample_time'])
target.startData(signals[1]['number'], signals[1]['sample_time'])


## Gets a running target and stops it
from pyrtai.rtai_server import RtaiServer
from test_observer import TestObserver

rtai = RtaiServer("MON")
target = rtai.getTarget(None, "Master")
target.halt()
