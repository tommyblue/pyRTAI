# pyRTAI

Python library designed to interact with [RTAI - the RealTime Application Interface for Linux from DIAPM](https://www.rtai.org/)

## Installation and configuration

Just clone this repository:

    git clone git@github.com:tommyblue/pyRTAI.git
    cd pyRTAI

Then configure **pyrtai/defaults.cfg** and launch python console to start work with the library.

## Use

### Standard connection to a target

    from pyrtai.rtai_server import RtaiServer
    from test_observer import TestObserver

    # Get the server
    rtai = RtaiServer("TEST")

    # Get the slave target
    target = rtai.getTarget()

    #
    # Play with target!
    #

    # ..then stop
    rtai.halt()

### Connect to a running target

Assuming **"TEST"** as target name and **"Master"** as master password

    from pyrtai.rtai_server import RtaiServer
    from test_observer import TestObserver

    # Get the first slave
    rtai = RtaiServer("TEST")

    # Get the slave target passing the master password
    target = rtai.getTarget(None, "Master")

    #
    # Play with target!
    #

    # ..then stop
    rtai.halt()

From now on we'll assume you have a valid **target** var.
Follow the standard connection procedure to obtain a valid **target**

### Get parameters

    params = target.getParameters()

You'll get an array of dictionaries:

    params = [
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
        }
    ]

### Update parameters

Update the **params** var then pass it to **setParameters()**

    params[0][values] = [1.5]
    target.setParameters(params)

### Update a single parameter

Use the helper **Target::setParam** using **block_name + param_name** as identifier:

    target.setParam("testsine/RPARAM[2]/Value[0]", [1.5])

### Signal structure

signals = target.getSignalStructure()

    # Channel 0
    channel = signals[0]['number']
    # channel == signal_number
    sample_time = signals[0]['sample_time']

If the signal have more then a single channel you have to cycle **signals**

### Create and register an observer

    observer_1 = TestObserver()
    observer_id_1 = target.addObserver(observer_1.getLine, sample_time, None, channel)

### Launch data stream

    if target.startData(channel, sample_time, decimation):
        print ("Started signal %d" % channel)
    else:
        print ("Can't start signal %d" % channel)

## API documentation

The code was documented using Doxygen.
HTML docs are in *./doc/html*. An updated mirror is hosted by Github at [http://tommyblue.github.com/pyRTAI](http://tommyblue.github.com/pyRTAI)
Latex docs can be found into *./doc/latex*
