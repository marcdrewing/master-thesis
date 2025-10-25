import time

collector = 2
glass = 1
silicon = 0

def procedure(t):       ##this function is being executed
    procedure_6(t)
    

def procedure_6(t):
    t.startSerialConnection("voltageSource", "COM7")
    t.setMeasurementInterval("voltageSource", 0.1)
    t.startMeasuring("voltageSource", channel=0)
    t.startMeasuring("voltageSource", channel=1)
    t.startMeasuring("voltageSource", channel=2)

    t.startSerialConnection("pressureSensor", "COM6")
    t.setMeasurementInterval("pressureSensor", interval=0.1)
    t.startMeasuring("pressureSensor", channel=1)

    t.startSerialConnection("temperatureSensor", "COM9")
    t.setMeasurementInterval("temperatureSensor", interval=0.1)
    t.startMeasuring("temperatureSensor")

    t.startLogging(filename="250811_QM1_Messung2", attributesToLog=["time", "temperature", "pressure", "V_CH0", "C_CH0", "V_CH1", "C_CH1", "V_CH2", "C_CH2"])

    t.setVoltage(channel=silicon, voltage=0)
    t.setVoltage(channel=glass, voltage=0)
    t.setVoltage(channel=collector, voltage=750)

    t.setCurrent(channel=silicon, current="10E-6")
    t.setCurrent(channel=glass, current="10E-6")
    t.setCurrent(channel=collector, current="250E-6")

    t.setVoltageRampingSpeed(channel=silicon, speed=10)
    t.setVoltageRampingSpeed(channel=glass, speed=10)
    t.setVoltageRampingSpeed(channel=collector, speed=25)

    t.turnOn(device="voltageSource", channel=silicon)
    t.turnOn(device="voltageSource", channel=glass)
    t.turnOn(device="voltageSource", channel=collector)

    time.sleep(40)

    t.setCurrent(channel=silicon, current="10E-6")
    t.setCurrent(channel=glass, current="10E-6")
    t.setCurrent(channel=collector, current="250E-6")


    t.fixedCurrentTrapezoid_2Channels(current="50E-6", channel_1=silicon, channel_2=glass, voltagesChannel_1=[100,200,250], voltagesChannel_2=[100,200,250], holdTime=2700, cooldownTime=120, rampSpeed=10)

    t.fixedCurrentTrapezoid_2Channels(current="100E-6", channel_1=silicon, channel_2=glass, voltagesChannel_1=[100,200,250], voltagesChannel_2=[100,200,250], holdTime=2700, cooldownTime=120, rampSpeed=10)

    t.fixedCurrentTrapezoid_2Channels(current="125E-6", channel_1=silicon, channel_2=glass, voltagesChannel_1=[100,200,250], voltagesChannel_2=[100,200,250], holdTime=2700, cooldownTime=120, rampSpeed=10)

    t.setVoltage(channel=silicon, voltage=0)
    t.setVoltage(channel=glass, voltage=0)
    t.setVoltage(channel=collector, voltage=0)

    
    

