from interMessage import interMessage
import time

class procedureToolsClass(object):
    def __init__(self, inputQueue, outputQueue):
        self.inputQueue = inputQueue
        self.outputQueue = outputQueue
        self.attributesToLog = []


    def startSerialConnection(self, device, port):
        commandRequest = interMessage(target=device,task="startSerialConnection")
        commandRequest.channel = port
        self.outputQueue.put(commandRequest)
        
    
    def startMeasuring(self, device, channel=0):
        commandRequest = interMessage(device,"startMeasuring")
        commandRequest.channel = channel
        self.outputQueue.put(commandRequest)

    def setMeasurementInterval(self, device, interval):
        commandRequest = interMessage(device,"setMeasurementInterval")
        commandRequest.value = interval
        self.outputQueue.put(commandRequest)
        
    def setVoltage(self, channel, voltage):
        commandRequest = interMessage("voltageSource","setVoltage")
        commandRequest.value = voltage
        commandRequest.channel = channel
        self.outputQueue.put(commandRequest)
        
    def setCurrent(self, channel, current):
        commandRequest = interMessage("voltageSource","setCurrent")
        commandRequest.value = current
        commandRequest.channel = channel
        self.outputQueue.put(commandRequest)
        
    def turnOn(self, device, channel=0):
        commandRequest = interMessage(device,"turnOn")
        commandRequest.channel = channel
        self.outputQueue.put(commandRequest)
        
    def turnOff(self, device, channel=0):
        commandRequest = interMessage(device,"turnOff")
        commandRequest.channel = channel
        self.outputQueue.put(commandRequest)

    def setVoltageRampingSpeed(self, channel, speed):   #speed in V/s
        commandRequest = interMessage("voltageSource","setVoltageRampingSpeed")
        commandRequest.channel = channel
        commandRequest.value = speed
        self.outputQueue.put(commandRequest)

    def setCurrentRampingSpeed(self, channel, speed):   #speed in V/s
        commandRequest = interMessage("voltageSource","setCurrentRampingSpeed")
        commandRequest.channel = channel
        commandRequest.value = speed
        self.outputQueue.put(commandRequest)

    def getVoltage(self, channel):
        timeoutWait = 2
        commandRequest = interMessage("voltageSource","getVoltage")
        commandRequest.channel = channel
        self.outputQueue.put(commandRequest)
        responseWaitBegin = time.time()
        while time.time() <= (responseWaitBegin+timeoutWait):
            if not self.inputQueue.empty():
                receivedMessage = self.inputQueue.get()
                if receivedMessage.task == "voltageMeasurement" and receivedMessage.topic == ("V_CH"+str(channel)):
                    return receivedMessage.value
                #if the message is not the one expected, it gets deleted. Since Program is waiting in loop, no other part of the software can access it anyway
                #else:
                    #self.inputQueue.put(receivedMessage)
        print("voltage source is not reacting")
        return None


    def getCurrent(self, channel):
        timeoutWait = 2
        commandRequest = interMessage("voltageSource","getCurrent")
        commandRequest.channel = channel
        self.outputQueue.put(commandRequest)
        responseWaitBegin = time.time()
        while time.time() <= (responseWaitBegin+timeoutWait):
            if not self.inputQueue.empty():
                receivedMessage = self.inputQueue.get()
                if receivedMessage.task == "currentMeasurement" and receivedMessage.topic == ("C_CH"+str(channel)):
                    return receivedMessage.value
                #if the message is not the one expected, it gets deleted. Since Program is waiting in loop, no other part of the software can access it anyway
                #else:
                    #self.inputQueue.put(receivedMessage)
        print("voltage source is not reacting")
        return None
                    

    def getPressure(self, channel):
        timeoutWait = 2
        commandRequest = interMessage("pressureSensor","getPressure")
        commandRequest.channel = channel
        self.outputQueue.put(commandRequest)
        responseWaitBegin = time.time()
        while time.time() <= (responseWaitBegin+timeoutWait):
            if not self.inputQueue.empty():
                receivedMessage = self.inputQueue.get()
                if receivedMessage.task == "pressureMeasurement" and receivedMessage.topic == "pressure":
                    return receivedMessage.value
                #if the message is not the one expected, it gets deleted. Since Program is waiting in loop, no other part of the software can access it anyway
                #else:
                    #self.inputQueue.put(receivedMessage)
        print("pressure sensor is not reacting")
        return None

    def getTemperature(self, channel):
        timeoutWait = 2
        commandRequest = interMessage("temperatureSensor","getTemperature")
        commandRequest.channel = channel
        self.outputQueue.put(commandRequest)
        responseWaitBegin = time.time()
        while time.time() <= (responseWaitBegin+timeoutWait):
            if not self.inputQueue.empty():
                receivedMessage = self.inputQueue.get()
                if receivedMessage.task == "temperatureMeasurement" and receivedMessage.topic == "temperature":
                    return receivedMessage.value
                #if the message is not the one expected, it gets deleted. Since Program is waiting in loop, no other part of the software can access it anyway
                #else:
                    #self.inputQueue.put(receivedMessage)
        print("temperature sensor is not reacting")
        return None 
        

    def startLogging(self, filename, attributesToLog):
        commandRequest = interMessage("dataLogger","startLogging")
        commandRequest.topic = filename
        commandRequest.contentList = attributesToLog
        self.outputQueue.put(commandRequest)

    def fixedCurrentStairUpDown(self, channel, currentLimit, voltageSteps, numberSteps, holdTime=5, startingVoltage=0):
        self.setVoltage(channel, startingVoltage)
        self.setCurrent(channel, currentLimit)
        rampTime = voltageSteps*(0.1) #consider the time the voltage source needs to ramp
        currentVoltage = startingVoltage
        time.sleep(holdTime)
        for i in range(0, numberSteps):
            currentVoltage = currentVoltage + voltageSteps
            self.setVoltage(channel, currentVoltage)
            time.sleep(rampTime)
            time.sleep(holdTime)

        for i in range(0, numberSteps):
            currentVoltage = currentVoltage - voltageSteps
            self.setVoltage(channel, currentVoltage)
            time.sleep(rampTime)
            time.sleep(holdTime)

    def fixedCurrentTrapezoid_2Channels(self, current, channel_1, channel_2, voltagesChannel_1, voltagesChannel_2, holdTime=600, cooldownTime=120, rampSpeed=10):
        #self.turnOff(device="voltageSource", channel=channel_1)
        #self.turnOff(device="voltageSource", channel=channel_2)

        self.setVoltage(channel=channel_1, voltage=0)
        self.setVoltage(channel=channel_2, voltage=0)
        time.sleep(0.5)
        
        voltageMem1 = 0
        voltageMem2 = 0
        voltageDiff1 = 0
        voltageDiff2 = 0

        self.setVoltageRampingSpeed(channel=channel_1, speed=rampSpeed)
        self.setVoltageRampingSpeed(channel=channel_2, speed=rampSpeed)
        time.sleep(0.5)
            
        self.setCurrent(channel=channel_1, current=current)
        self.setCurrent(channel=channel_2, current=current)
        time.sleep(0.5)


        

        #self.turnOn(device="voltageSource", channel=channel_1)
        #self.turnOn(device="voltageSource", channel=channel_2)

        numberOfVoltages = max(len(voltagesChannel_1), len(voltagesChannel_2))

        for i in range(0, numberOfVoltages):
            if i+1 <= len(voltagesChannel_1):
                print("setting voltage to:"+str(voltagesChannel_1[i]))
                self.setVoltage(channel=channel_1, voltage=voltagesChannel_1[i])
                voltageDiff1 = abs(voltagesChannel_1[i] - voltageMem1)
                voltageMem1 = voltagesChannel_1[i]
                
            if i+1 <= len(voltagesChannel_2):
                print("setting voltage to:"+str(voltagesChannel_2[i]))
                self.setVoltage(channel=channel_2, voltage=voltagesChannel_2[i])
                voltageDiff2 = abs(voltagesChannel_2[i] - voltageMem2)
                voltageMem2 = voltagesChannel_2[i]

            time.sleep(max(voltageDiff1, voltageDiff2)/rampSpeed)

        time.sleep(holdTime)

        for i in range(1, numberOfVoltages):
            if i+1 <= len(voltagesChannel_1):
                self.setVoltage(channel=channel_1, voltage=voltagesChannel_1[len(voltagesChannel_1)-i-1])
                voltageDiff1 = abs(voltagesChannel_1[len(voltagesChannel_1)-i-1] - voltageMem1)
                voltageMem1 = voltagesChannel_1[len(voltagesChannel_1)-i-1]
                
            if i+1 <= len(voltagesChannel_2):
                self.setVoltage(channel=channel_2, voltage=voltagesChannel_2[len(voltagesChannel_2)-i-1])
                voltageDiff2 = abs(voltagesChannel_2[len(voltagesChannel_2)-i-1] - voltageMem2)
                voltageMem2 = voltagesChannel_2[len(voltagesChannel_2)-i-1]

            time.sleep(max(voltageDiff1, voltageDiff2)/rampSpeed)


        self.setVoltage(channel=channel_1, voltage=0)
        self.setVoltage(channel=channel_2, voltage=0)

        time.sleep(max(voltageMem2, voltageMem1)/rampSpeed)
        
        time.sleep(cooldownTime)
            

        
                

    

        
        
            
            










            
            
