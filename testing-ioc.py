#!/usr/bin/env python
import threading
import numpy

from pcaspy import Driver, SimpleServer

MAX_POINTS      = 1000
FREQUENCY       = 1000
AMPLITUDE       = 1.0
NUM_DIVISIONS   = 10
MIN_UPDATE_TIME = 0.01
IMAGE_SIZE      = 512

prefix = 'MTEST:'
pvdb = {
        'Run'              : { 'type' : 'enum',
                                'enums': ['STOP', 'RUN'], 'asg'  : 'default'},
        'ReadOnly'     : { 'type' : 'enum',
                                'enums': ['FALSE', 'TRUE'], 'value': 0 },
        'UpdateTime'       : { 'prec' : 3, 'unit' : 's', 'value' : 1, 'asg' : 'default'     },
        'TimePerDivision'  : { 'prec' : 5, 'unit' : 's', 'value' : 0.001, 'asg' : 'default' },
        'TriggerDelay'     : { 'prec' : 5, 'unit' : 's', 'value' : 0.0005, 'asg' : 'default'},
        'VoltsPerDivision' : { 'prec' : 3, 'unit' : 'V', 'value' : 0.2, 'asg' : 'default'   },
        'VoltOffset'       : { 'prec' : 3, 'unit' : 'V', 'asg' : 'default' },
        'NoiseAmplitude'   : { 'prec' : 3, 'value' : 0.2, 'asg' : 'default'   },
        'Waveform'         : { 'count': MAX_POINTS,
                                'prec' : 5, 'asg' : 'default' },
        'Cosine'         : { 'count': MAX_POINTS,
                                'prec' : 5, 'asg' : 'default' },
        'TimeBase'         : { 'count': MAX_POINTS,
                               'prec' : 5,
                               'value': numpy.arange(MAX_POINTS, dtype=float) 
                                            * NUM_DIVISIONS / (MAX_POINTS -1), 'asg' : 'default'},
        'MinValue'         : { 'prec' : 4, 'asg' : 'default' },
        'MaxValue'         : { 'prec' : 4, 'asg' : 'default' },
        'MeanValue'        : { 'prec' : 4, 'asg' : 'default' },
        'XPos'             : { 'prec' : 2, 'value' : 0.0, 'asg' : 'default' },
        'YPos'             : { 'prec' : 2, 'value' : 0.0, 'asg' : 'default' },
        'Image'            : { 'type' : 'char', 'count': IMAGE_SIZE**2, 'value': numpy.zeros(IMAGE_SIZE**2,dtype=numpy.uint8), 'asg' : 'default' },
        'TwoSpotImage'     : { 'type' : 'char', 'count': IMAGE_SIZE**2, 'value': numpy.zeros(IMAGE_SIZE**2,dtype=numpy.uint8), 'asg' : 'default' },
        'ImageWidth'       : { 'type' : 'int', 'value' : IMAGE_SIZE, 'asg' : 'default' },
        'String'           : { 'type' : 'string', 'value': "Test String", 'asg' : 'default'},
        'Float'            : { 'type' : 'float', 'value': 0.0, 'lolim': -1.2, 'lolo': -1.0, 'low': -0.8, 'high': 0.8, 'hihi': 1.0, 'hilim': 1.2, 'units': 'mJ', 'prec': 3, 'asg' : 'default' },
        'StatusBits'       : { 'type' : 'int', 'value': 0b101010, 'lolim': 0, 'hilim': 32, 'asg' : 'default' }
}

def double_gaussian_2d(x, y, x0, y0, xsig, ysig):
    return numpy.exp(-0.5*(((x-x0) / xsig)**2 + ((y-y0) / ysig)**2)) + numpy.exp(-0.5*(((x+3) / xsig)**2 + ((y+3) / ysig)**2)) 
    
def gaussian_2d(x, y, x0, y0, xsig, ysig):
    return numpy.exp(-0.5*(((x-x0) / xsig)**2 + ((y-y0) / ysig)**2)) 
 
class myDriver(Driver):
    def __init__(self):
        Driver.__init__(self)
        self.eid = threading.Event()
        self.tid = threading.Thread(target = self.runSimScope) 
        self.tid.setDaemon(True)
        self.tid.start()

    def write(self, reason, value):
        status = True
        # take proper actions
        if reason == 'UpdateTime':
            value = max(MIN_UPDATE_TIME, value)
        elif reason == 'Run':
            if not self.getParam('Run') and value == 1:
                self.eid.set()
                self.eid.clear()
        # store the values
        if status:
            self.setParam(reason, value)
        return status

    def runSimScope(self):
        # simulate scope waveform
        x = numpy.linspace(-5.0,5.0,IMAGE_SIZE)
        y = numpy.linspace(-5.0,5.0,IMAGE_SIZE)
        xgrid,ygrid = numpy.meshgrid(x,y)
        while True:
            run = self.getParam('Run')
            updateTime = self.getParam('UpdateTime')
            if run:
                self.eid.wait(updateTime)
            else:
                self.eid.wait()
            run = self.getParam('Run')
            if not run: continue
            # retrieve parameters
            noiseAmplitude    = self.getParam('NoiseAmplitude')
            timePerDivision   = self.getParam('TimePerDivision')
            voltsPerDivision  = self.getParam('VoltsPerDivision')
            triggerDelay      = self.getParam('TriggerDelay')
            voltOffset        = self.getParam('VoltOffset')
            # calculate the data wave based on timeWave scale 
            timeStart = triggerDelay
            timeStep  = timePerDivision * NUM_DIVISIONS / MAX_POINTS
            timeWave  = timeStart + numpy.arange(MAX_POINTS) * timeStep 
            noise  = noiseAmplitude * numpy.random.random(MAX_POINTS)
            data = AMPLITUDE * numpy.sin(timeWave * FREQUENCY * 2 * numpy.pi) + noise
            cos_data = AMPLITUDE * numpy.cos(timeWave * FREQUENCY * 2 * numpy.pi) + noise
            # calculate statistics
            self.setParam('MinValue',  data.min())
            self.setParam('MaxValue',  data.max())
            self.setParam('MeanValue', data.mean())
            # scale/offset
            yScale = 1.0 / voltsPerDivision
            data   = NUM_DIVISIONS/2.0 + yScale * (data + voltOffset)
            cos_data = NUM_DIVISIONS/2.0 + yScale * (cos_data + voltOffset)
            self.setParam('Waveform',  data)
            self.setParam('Cosine', cos_data)
            #Generate the image data
            x0 = 0.5*(numpy.random.rand()-0.5) + self.getParam('XPos')
            y0 = 0.5*(numpy.random.rand()-0.5) - self.getParam('YPos')
            xsig = 0.8 - 0.2*numpy.random.rand()
            ysig = 0.8 - 0.2*numpy.random.rand()
            z = gaussian_2d(xgrid,ygrid, x0, y0, xsig, ysig)
            image_data = numpy.abs(256.0*(z)).flatten(order='C').astype(numpy.uint8, copy=False)
            self.setParam('Image', image_data)
            two_spots = double_gaussian_2d(xgrid, ygrid, x0, y0, xsig, ysig)
            two_spot_image = numpy.abs(256.0*(two_spots)).flatten(order='C').astype(numpy.uint8, copy=False)
            self.setParam('TwoSpotImage', two_spot_image)
            
            # do updates so clients see the changes
            self.updatePVs()

if __name__ == '__main__':
    server = SimpleServer()
    server.initAccessSecurityFile('access_rules.as', P=prefix)
    server.createPV(prefix, pvdb)
    driver = myDriver()
    #Manually set the ReadOnly PV to force access rule calculation.
    #You can set ReadOnly to 1 to disable write access on all PVs.
    driver.setParam('ReadOnly', 0)
    # process CA transactions
    while True:
        server.process(0.1)