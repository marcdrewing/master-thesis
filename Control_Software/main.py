import multiprocessing
from isegInterface import isegInterfaceClass
from temperatureSensor import temperatureSensorClass
from pfeifferInterface import pfeifferInterfaceClass
import time
from interMessage import interMessage
from dataLogger import dataLoggerClass
from procedure import procedure
from procedureTools import procedureToolsClass

def isegProcess(isegInterfaceInputQueue, isegInterfaceOutputQueue):
    isegDevice = isegInterfaceClass(isegInterfaceInputQueue, isegInterfaceOutputQueue)
    isegDevice.run()

def temperatureSensorProcess(temperatureSensorInputQueue, temperatureSensorOutputQueue):
    temperatureSensorDevice = temperatureSensorClass(temperatureSensorInputQueue, temperatureSensorOutputQueue)
    temperatureSensorDevice.run()

def pressureSensorProcess(pressureSensorInputQueue, pressureSensorOutputQueue):
    pfeifferInterfaceDevice = pfeifferInterfaceClass(pressureSensorInputQueue, pressureSensorOutputQueue)
    pfeifferInterfaceDevice.run()

##def procedureProcess(temperatureSensorInputQueue, temperatureSensorOutputQueue):
##    while(1):
##        if not temperatureSensorOutputQueue.empty():
##            message = temperatureSensorOutputQueue.get()
##            print("["+str(message.timestamp)+"]"+"["+str(message.channel)+"]"+"["+str(message.task)+"]"+str(message.value))

# ["time", "temperature", "pressure", "V_CH0", "V_CH1", "C_CH0", "C_CH1"] , "V_CH0", "C_CH0", "V_CH1", "C_CH1", "V_CH2", "C_CH2"]
def dataLoggerProcess(loggerInputQueue, loggerOutputQueue):
    loggerInitiated = False
    while not loggerInitiated:
        while loggerInputQueue.empty():
            time.sleep(0.1)
        message = loggerInputQueue.get()
        if message.task == "startLogging":
            print("starting to Log incoming Messages")
            logger = dataLoggerClass(inputQueue=loggerInputQueue, outputQueue=loggerOutputQueue, attrToLog=message.contentList, filename=message.topic)
            logger.run()
    
def messageExchangeProcess(controlInputQueue, controlOutputQueue, loggerInputQueue, loggerOutputQueue, temperatureSensorInputQueue, temperatureSensorOutputQueue, isegInterfaceInputQueue, isegInterfaceOutputQueue, pressureSensorInputQueue, pressureSensorOutputQueue):
    while True:
        if not temperatureSensorOutputQueue.empty():
            message = temperatureSensorOutputQueue.get()
            if message.target == "dataLogger":
                loggerInputQueue.put(message)
            if message.target == "procedureProcess":
                controlInputQueue.put(message)
            
        if not isegInterfaceOutputQueue.empty():
            message = isegInterfaceOutputQueue.get()
            if message.target == "dataLogger":
                loggerInputQueue.put(message)
            if message.target == "procedureProcess":
                controlInputQueue.put(message)
            
        if not pressureSensorOutputQueue.empty():
            message = pressureSensorOutputQueue.get()
            if message.target == "dataLogger":
                loggerInputQueue.put(message)
            if message.target == "procedureProcess":
                controlInputQueue.put(message)
            

        if not controlOutputQueue.empty():
            message = controlOutputQueue.get()
            #print(message.target)
            match message.target:
                case "temperatureSensor":
                    temperatureSensorInputQueue.put(message)
                case "voltageSource":
                    isegInterfaceInputQueue.put(message)
                case "pressureSensor":
                    pressureSensorInputQueue.put(message)
                case "dataLogger":
                    loggerInputQueue.put(message)
            

if __name__ == '__main__': #main Program
    isegInterfaceInputQueue = multiprocessing.Queue()
    isegInterfaceOutputQueue = multiprocessing.Queue()

    temperatureSensorInputQueue = multiprocessing.Queue()
    temperatureSensorOutputQueue = multiprocessing.Queue()

    loggerInputQueue = multiprocessing.Queue()
    loggerOutputQueue = multiprocessing.Queue()

    controlInputQueue = multiprocessing.Queue()
    controlOutputQueue = multiprocessing.Queue()

    pressureSensorInputQueue = multiprocessing.Queue()
    pressureSensorOutputQueue = multiprocessing.Queue()
    

    isegProcessInstance = multiprocessing.Process(target=isegProcess, args=(isegInterfaceInputQueue, isegInterfaceOutputQueue,))
    isegProcessInstance.start()

    temperatureSensorInstance = multiprocessing.Process(target=temperatureSensorProcess, args=(temperatureSensorInputQueue, temperatureSensorOutputQueue,))
    temperatureSensorInstance.start()

    pressureSensorInstance = multiprocessing.Process(target=pressureSensorProcess, args=(pressureSensorInputQueue, pressureSensorOutputQueue,))
    pressureSensorInstance.start()

    #procedureProcessInstance = multiprocessing.Process(target=procedureProcess, args=(temperatureSensorInputQueue, temperatureSensorOutputQueue,))
    #procedureProcessInstance.start()

    dataLoggerProcessInstance = multiprocessing.Process(target=dataLoggerProcess, args=(loggerInputQueue, loggerOutputQueue,))
    dataLoggerProcessInstance.start()

    messageExchangeProcessInstance = multiprocessing.Process(target=messageExchangeProcess, args=(controlInputQueue, controlOutputQueue, loggerInputQueue, loggerOutputQueue, temperatureSensorInputQueue, temperatureSensorOutputQueue, isegInterfaceInputQueue, isegInterfaceOutputQueue, pressureSensorInputQueue, pressureSensorOutputQueue,))
    messageExchangeProcessInstance.start()

    
    procedureToolsInstance = procedureToolsClass(controlInputQueue, controlOutputQueue)
    procedure(procedureToolsInstance)


    
    while 1:
        pass
        
    
