import serial
import serial.tools.list_ports
from datetime import datetime
import random
from interMessage import interMessage
import time

##Notiz: Falls es so scheint, als würden einige Messwerte nicht aufgenommen werden, dann kann das daran liegen, dass durch das Senden eines Befehls eine Verzögerung entsteht, wodurch die Messwertanfrage erst verzögert gesendet wird

class isegInterfaceClass(object):
    def __init__(self, inputQueue, outputQueue, serialConnection=None, connectionEstablished=False, measuringActive=[False,False,False,False], measurementInterval=1):
        self.outputQueue = outputQueue
        self.inputQueue = inputQueue
        self.serialConnection = serialConnection
        self.connectionEstablished = connectionEstablished
        self.measuringActive = measuringActive
        self.measurementInterval = measurementInterval
        self.rampingSpeed = [5, 5, 5, 5] #set ramping speed to 5V/s
        self.testMode = False
        self.lastCurrentMeasurements = [[],[],[],[]]
        self.lastVoltageMeasurements = [[],[],[],[]]

        #testMessage = interMessage(target="isegInterface",task="test", content="this worked flawlessly") #interMessage(target,task,content)
        #self.inputQueue.put(testMessage)
        

    def run(self):
        last_execution = time.time()
        while True:
            self.checkForInput()

            if last_execution + self.measurementInterval <= time.time():
                last_execution = time.time()
                self.measureRoutine()
                
            
                
                
    def checkForInput(self):
        if not self.inputQueue.empty():
            message = self.inputQueue.get()
            
            if str(message.task) == "test":
                print("Testing Message Answer:"+message.content)

            if message.task == "testConnection":
                print("Testing Message Answer:"+self.testConnection())

            if message.task == "startSerialConnection":
                self.startSerialConnection(message.channel)

            if message.task == "setVoltage":
                self.setVoltage(message.channel, message.value)

            if message.task == "setCurrent":
                self.setCurrent(message.channel, message.value)

            if message.task == "turnOn":
                self.turnOn(message.channel)

            if message.task == "turnOff":
                self.turnOff(message.channel)

            if message.task == "setPolarity":
                setPolarity(message.channel, message.value)

            if message.task == "getVoltage":
                #print(self.lastVoltageMeasurements[message.channel])
                if self.measuringActive[message.channel] and len(self.lastVoltageMeasurements[message.channel])>0:
                    averageVoltage = 0
                    amountOfMeasurements = len(self.lastVoltageMeasurements[message.channel])
                    for m in self.lastVoltageMeasurements[message.channel]:
                        averageVoltage = averageVoltage + m
                    averageVoltage = averageVoltage/amountOfMeasurements
                    measuredVoltage = averageVoltage
                else:
                    measuredVoltage = 0#self.getVoltage(message.channel)
                now = datetime.now()
                returnMessage = interMessage(target="procedureProcess", task="voltageMeasurement", topic="V_CH"+str(message.channel))
                returnMessage.channel = message.channel
                returnMessage.value = measuredVoltage
                returnMessage.timestamp = now.strftime("%Y-%m-%d")+"T"+now.strftime("%H:%M:%S.%f")[:-3]
                self.outputQueue.put(returnMessage)

            if message.task == "getCurrent":
                #print(self.lastCurrentMeasurements[message.channel])
                if self.measuringActive[message.channel] and len(self.lastCurrentMeasurements[message.channel])>0:
                    averageCurrent = 0
                    amountOfMeasurements = len(self.lastCurrentMeasurements[message.channel])
                    for m in self.lastCurrentMeasurements[message.channel]:
                        averageCurrent = averageCurrent + m
                    averageCurrent = averageCurrent/amountOfMeasurements
                    measuredCurrent = averageCurrent
                else:
                    measuredCurrent = self.getCurrent(message.channel)
                now = datetime.now()
                returnMessage = interMessage(target="procedureProcess", task="currentMeasurement", topic="C_CH"+str(message.channel))
                returnMessage.channel = message.channel
                returnMessage.value = measuredCurrent
                returnMessage.timestamp = now.strftime("%Y-%m-%d")+"T"+now.strftime("%H:%M:%S.%f")[:-3]
                self.outputQueue.put(returnMessage)

            if message.task == "startMeasuring":
                self.startMeasuring(message.channel)
                
            if message.task == "stopMeasuring":
                self.stopMeasuring(message.channel)

            if message.task == "setMeasurementInterval":
                self.setMeasurementInterval(message.value)

            if message.task == "setVoltageRampingSpeed":
                if message.channel >= 0 and message.channel <= 3:
                    self.rampingSpeed[message.channel] = message.value
                    self.setVoltageRampingSpeed(message.channel, message.value)

            if message.task == "setCurrentRampingSpeed":
                if message.channel >= 0 and message.channel <= 3:
                    self.rampingSpeed[message.channel] = message.value
                    self.setCurrentRampingSpeed(message.channel, message.value)
                    

    def measureRoutine(self):
        startTime = time.time()*1000
        while not (startTime%100) == 0:
            startTime = time.time()*1000
        
        for i in range(0,3):
            if self.measuringActive[i]:
                self.serialConnection.reset_input_buffer()
                parameterList = self.getChannelMeasurements(i)
                if parameterList is not None:
                    measuredCurrent = parameterList[1]
                    now_current = datetime.now()
                    measuredVoltage = parameterList[0]
                    now_voltage = datetime.now()
                    returnMessageCurrent = interMessage(target="dataLogger", topic="C_CH"+str(i))
                    returnMessageVoltage = interMessage(target="dataLogger", topic="V_CH"+str(i))
                    returnMessageCurrent.channel = i
                    returnMessageVoltage.channel = i
                    returnMessageCurrent.value = measuredCurrent
                    returnMessageVoltage.value = measuredVoltage
                    self.updateVoltageMeasurements(channel=i, voltage=measuredVoltage)
                    self.updateCurrentMeasurements(channel=i, current=measuredCurrent)
                    returnMessageCurrent.timestamp = now_current.strftime("%Y-%m-%d")+"T"+now_current.strftime("%H:%M:%S.%f")[:-3]
                    returnMessageVoltage.timestamp = now_voltage.strftime("%Y-%m-%d")+"T"+now_voltage.strftime("%H:%M:%S.%f")[:-3]
                    if returnMessageVoltage.value is not None and returnMessageCurrent.value is not None:
                        self.outputQueue.put(returnMessageCurrent)
                        self.outputQueue.put(returnMessageVoltage)
            

    def startMeasuring(self, channel):
        self.measuringActive[channel] = True

    def stopMeasuring(self, channel):
        self.measuringActive[channel] = False

    def setMeasurementInterval(self, interval):
        self.measurementInterval = interval

##delete the oldest measurement if there are more than the amount of measurements taken in 1 second
## self.measurementInterval=0.1 --> 10 Measurements, delete oldest when 11Measurements available
## self.measurementInterval=10 --> 1 measurement available every 10seconds, (1/self.measurementInterval)+1=1.1, 1.1 is not smaller or equal to 1 so measurement is kept for 10s
    def updateVoltageMeasurements(self, channel, voltage):
        if voltage is not None and voltage != "" and voltage != " ":
            voltage = float(voltage.strip("V"))
            self.lastVoltageMeasurements[channel].append(voltage)
        if len(self.lastVoltageMeasurements[channel]) >= (1/self.measurementInterval)+1: 
            self.lastVoltageMeasurements[channel].pop(0)

    def updateCurrentMeasurements(self, channel, current):
        if current is not None and current != "" and current != " ":
            current = float(current.strip("A"))
            self.lastCurrentMeasurements[channel].append(current)
        if len(self.lastCurrentMeasurements[channel]) >= (1/self.measurementInterval)+1:
            self.lastCurrentMeasurements[channel].pop(0)

########## Communication with ISEG Device ########################################################################################

    def startSerialConnection(self, serialPort):
        if not self.testMode:
            self.serialConnection = serial.Serial(serialPort, 9600, timeout=1)#, parity=serial.PARITY_EVEN, rtscts=1)
        self.connectionEstablished = True
        #messageContent = ":CONF:SERIAL:BAUD 115200"
        #self.serialSend(messageContent)
        

        #self.serialConnection.baudrate = 115200
        #print(self.serialConnection.readline())
        #time.sleep(1)

        #messageContent = ":CONF:SERIAL:BAUD?"
        #self.serialSend(messageContent)
        #print(self.serialConnection.readline())

        #messageContent = ":CONF:SERIAL:ECHO 0"
        #self.sendCommand(messageContent)

        #messageContent = ":CONF:SERIAL:ECHO?"
        #print(self.getMeasurement(messageContent))
        #time.sleep(5)

    def serialSend(self, serialMessage):
        self.serialConnection.write((serialMessage+"\r"+"\n").encode('utf-8'))

    def serialRead(self):
        return self.serialConnection.read_until().decode('UTF-8')

    def sendCommand(self, command):
        if not self.connectionEstablished:
            print("Serial Connection for ised Device not yet established")
            return False
        if not self.testMode:
            self.serialSend(command)
            echo = self.serialRead()
        #print("echo:"+echo)
        #if echo == command:
        #    return True
        #else:
        #    return False

    def getMeasurement(self, command):
        if not self.connectionEstablished:
            print("Serial Connection for ised Device not yet established")
            return None
        if not self.testMode:
            self.serialSend(command)
            #echo = self.serialRead()
            #print("echo:"+echo)
            time.sleep(0.01)
            measuredValue = self.serialRead()
            measuredValue = measuredValue.rstrip()
            while measuredValue[:1] == ":":
                measuredValue = self.serialRead()
                measuredValue = measuredValue.rstrip()
                if measuredValue == "":
                    self.serialConnection.reset_input_buffer()
                    return None
            self.serialConnection.reset_input_buffer()
            return measuredValue
        return random.randint(1,100)

################################################################################################################

########### Functions of ISEG Device ###########################################################################
    
    def testConnection(self):
        messageContent = "*IDN?"
        return self.getMeasurement(messageContent)

    def setVoltage(self, channel, voltageToSet):
        messageContent = ":VOLT "+str(voltageToSet)+",(@"+str(channel)+")"
        return self.sendCommand(messageContent)

    def setCurrent(self, channel, currentToSet):
        print("trying to set current")
        messageContent = ":CURR "+str(currentToSet)+",(@"+str(channel)+")"
        return self.sendCommand(messageContent)

    def turnOn(self, channel):
        messageContent = ":VOLT ON,(@"+str(channel)+")"
        return self.sendCommand(messageContent)

    def turnOff(self, channel):
        messageContent = ":VOLT OFF,(@"+str(channel)+")"
        return self.sendCommand(messageContent)

    def getVoltage(self, channel):
        messageContent = ":MEAS:VOLT? (@"+str(channel)+")"
        measuredValue = self.getMeasurement(messageContent)
        #print("Voltage Channel"+str(channel)+":"+str(measuredValue))
        return measuredValue
        #return random.randint(1,100)

    def getCurrent(self, channel):
        messageContent = ":MEAS:CURR? (@"+str(channel)+")"
        return self.getMeasurement(messageContent)
        #return random.randint(1,100)

    def getChannelMeasurements(self, channel):
        messageContent = ":MEAS:VOLT? (@"+str(channel)+");CURR? (@"+str(channel)+")"
        measuredValue = self.getMeasurement(messageContent)
        #print(measuredValue)
        if measuredValue is None or measuredValue == "":
            return None
        parameterList = str(measuredValue).split(";")
        #print("Voltage Channel"+str(channel)+":"+str(measuredValue))
        #print(parameterList)
        return parameterList
        #return measuredValue

    def setPolarity(self, channel, polarity):
        if message.value == "p" or message.value == "positive":
                    message.content = ":CONF:OUTP:POL "+"p"+",(@"+str(channel)+")"
                    self.sendCommand(message.content)
        if message.value == "n" or message.value == "negative":
                    message.content = ":CONF:OUTP:POL "+"n"+",(@"+str(channel)+")"
                    self.sendCommand(message.content)

    def setVoltageRampingSpeed(self, channel, speed):
        messageContent = ":CONF:RAMP:VOLT:UP "+str(speed)+",(@"+str(channel)+")"+";"+":CONF:RAMP:VOLT:DOWN "+str(speed)+",(@"+str(channel)+")"
        self.sendCommand(messageContent)

    def setCurrentRampingSpeed(self, channel, speed):
        messageContent = ":CONF:RAMP:CURR:UP "+str(speed)+",(@"+str(channel)+")"+";"+":CONF:RAMP:CURR:DOWN "+str(speed)+",(@"+str(channel)+")"
        self.sendCommand(messageContent)
        


        
        
        
        
