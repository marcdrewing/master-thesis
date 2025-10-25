import serial
import serial.tools.list_ports
from datetime import datetime
import random
from interMessage import interMessage
import time

class temperatureSensorClass(object):
    def __init__(self, inputQueue, outputQueue, serialConnection=None, connectionEstablished=False, measuringActive=[False, False, False, False], measurementInterval=1, timeSinceLastSerialCommand=0):
        self.outputQueue = outputQueue
        self.inputQueue = inputQueue
        self.serialConnection = serialConnection
        self.connectionEstablished = connectionEstablished
        self.measuringActive = measuringActive
        self.measurementInterval = measurementInterval
        self.timeSinceLastSerialCommand = timeSinceLastSerialCommand #if the commands are sent to the sensor too fast, it might break the communication
        self.currentTemperature = 0
        self.testMode = False
        self.serialPort = None

    def run(self):
        last_execution = time.time()
        last_reconnect_try = time.time()
        last_successfull_measurement = time.time()
        while True:
            
            self.checkForInput()

            if not self.testMode:
                
                if self.connectionEstablished:
                    try:
                        answer = self.measureRoutine()
                        if answer == True:
                            last_successfull_measurement = time.time()

                        if last_successfull_measurement + 5 <= time.time():
                            self.connectionEstablished = False
                            self.serialConnection.close()
                            
                    except serial.SerialException:
                        self.connectionEstablished = False
                        print("Connection to temperature sensor lost. Reconnecting...")
                        self.serialConnection.close()
                        self.startSerialConnection(self.serialPort)
                        if self.connectionEstablished:
                            self.setMeasurementIntervalCommand(self.measurementInterval)
                            self.startMeasuringCommand()
                else:
                    if last_execution + self.measurementInterval <= time.time():
                        last_execution = time.time()
                        self.connectionLostRoutine()

                    if last_reconnect_try + 4 <= time.time():
                        last_reconnect_try = time.time()
                        self.startSerialConnection(self.serialPort)
                        if self.connectionEstablished:
                            self.setMeasurementIntervalCommand(self.measurementInterval)
                            self.startMeasuringCommand()
                    
            if self.testMode:
                if last_execution + self.measurementInterval <= time.time():
                    last_execution = time.time()
                    measuredTemperature = self.getTemperature()
                    measuredTemperature = measuredTemperature.rstrip()
                    now = datetime.now()
                    returnMessage = interMessage(target="testingProcedureProcess", topic="temperature")
                    returnMessage.value = measuredTemperature
                    returnMessage.channel = 0
                    returnMessage.timestamp = now.strftime("%Y-%m-%d")+"T"+now.strftime("%H:%M:%S.%f")[:-3]
                    self.outputQueue.put(returnMessage)
                
            
                
                
    def checkForInput(self):
        if not self.inputQueue.empty():
            message = self.inputQueue.get()
            
            if str(message.task) == "test":
                print("Testing Message Answer:"+message.content)

            if message.task == "testConnection":
                #print("Testing Message Answer:"+self.testConnection())
                self.testConnection()

            if message.task == "startSerialConnection":
                print("connecting to"+str(message.channel))
                self.serialPort = message.channel
                self.startSerialConnection(message.channel)

            if message.task == "getTemperature":
                if message.channel == None:
                    message.channel = 0
                if self.measuringActive[message.channel] == True and self.currentTemperature != 0 and self.currentTemperature is not None and self.currentTemperature != "":
                    measuredTemperature = self.currentTemperature
                else:
                    measuredTemperature = self.getTemperature(message.channel)
                now = datetime.now()
                returnMessage = interMessage(target="procedureProcess", task="temperatureMeasurement", topic="temperature")
                returnMessage.channel = None
                returnMessage.value = measuredTemperature
                returnMessage.timestamp = now.strftime("%Y-%m-%d")+"T"+now.strftime("%H:%M:%S.%f")[:-3]
                self.outputQueue.put(returnMessage)

            if message.task == "startMeasuring":
                message.channel = 0
                self.startMeasuring(message.channel)
                
            if message.task == "stopMeasuring":
                message.channel = 0
                self.stopMeasuring(message.channel)

            if message.task == "setMeasurementInterval":
                self.setMeasurementInterval(message.value)
                    

    def measureRoutine(self):   #after starting the sensor measurement, just wait for incoming values
        if self.serialConnection.inWaiting() != 0:
            measuredTemperature = self.serialRead()
            measuredTemperature = measuredTemperature.rstrip()
            self.currentTemperature = measuredTemperature
            #print(measuredTemperature)
            now = datetime.now()
            returnMessage = interMessage(target="dataLogger", topic="temperature")
            returnMessage.value = measuredTemperature
            returnMessage.channel = 0
            returnMessage.timestamp = now.strftime("%Y-%m-%d")+"T"+now.strftime("%H:%M:%S.%f")[:-3]
            self.outputQueue.put(returnMessage)
            return True
        else:
            return False
            

        #for i in range(0,3):
        #    if self.measuringActive[i]:
        #        measuredTemperature = self.getTemperature()
        #        now = datetime.now()
        #        returnMessage = interMessage("testingProcedureProcess", "temperatureMeasurement")
        #        returnMessage.value = measuredTemperature
        #        returnMessage.channel = i
        #        returnMessage.timestamp = now.strftime("%d.%m.%y")+"_"+now.strftime("%H:%M:%S.%f")[:-3]
        #        self.outputQueue.put(returnMessage)
    def connectionLostRoutine(self):
        now = datetime.now()
        returnMessage = interMessage(target="dataLogger", topic="temperature")
        returnMessage.value = 0
        returnMessage.channel = 0
        returnMessage.timestamp = now.strftime("%Y-%m-%d")+"T"+now.strftime("%H:%M:%S.%f")[:-3]
        self.outputQueue.put(returnMessage)
            

    def startMeasuring(self, channel):
        self.measuringActive[channel] = True
        self.startMeasuringCommand()

    def stopMeasuring(self, channel):
        self.measuringActive[channel] = False
        self.stopMeasuringCommand()

    def setMeasurementInterval(self, interval):
        self.measurementInterval = interval
        self.setMeasurementIntervalCommand(interval)

########## Communication with Temperature Sensor ########################################################################################

    def startSerialConnection(self, serialPort):
        if not self.testMode:
            try:
                self.serialConnection = serial.Serial(serialPort, 115200, timeout=3, parity=serial.PARITY_EVEN, rtscts=0)
                self.connectionEstablished = True
                time.sleep(0.5)
            except serial.SerialException:
                print("could not connect to temperature Sensor")

    def serialSend(self, serialMessage):
        self.serialConnection.write((serialMessage+"\r"+"\n").encode('utf-8'))

    def serialRead(self):
        return self.serialConnection.read_until().decode('UTF-8')

    def sendCommand(self, command):
        if not self.connectionEstablished:
            print("Serial Connection to temperature sensor not yet established")
            return False
        if not self.testMode:
            self.serialSend(command)

    def getMeasurement(self, command):
        if not self.connectionEstablished:
            print("Serial Connection to temperature sensor not yet established")
            return None
        if not self.testMode:
            self.serialSend(command)
            measuredValue = str(self.serialRead())
            measuredValue = measuredValue.rstrip()
            return measuredValue
        return str(random.randint(1,100))

################################################################################################################

########### Functions of Temperature Sensor Device ###########################################################################
    
    def testConnection(self):
        time.sleep(0.1)
        messageContent = "test"
        self.sendCommand(messageContent)
        time.sleep(0.1)

    def startMeasuringCommand(self):
        time.sleep(0.5)
        print("Starting Measurement")
        messageContent = "startMeasuring"
        self.sendCommand(messageContent)
        time.sleep(0.5)

    def stopMeasuringCommand(self):
        time.sleep(0.5)
        print("trying to stop")
        messageContent = "stopMeasuring"
        self.sendCommand(messageContent)
        time.sleep(0.5)

    def setMeasurementIntervalCommand(self, interval):
        time.sleep(0.5) #need for reaction time of the pico
        #print("test")
        messageContent = "setMeasurementInterval:"+str(interval)
        self.sendCommand(messageContent)
        time.sleep(0.5)
        #messageContent = str(interval)
        #print(messageContent)
        #self.sendCommand(messageContent)
        #print(messageContent)
        #print(self.getMeasurement(messageContent))

    def getTemperature(self, channel=0):
        messageContent = "getTemperature"
        return self.getMeasurement(messageContent)



        
        
        
        
