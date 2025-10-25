from collections import defaultdict
from interMessage import interMessage
import time
from datetime import datetime, timedelta
import pandas as pd
import os.path
import multiprocessing



class dataLoggerClass(object):
    def __init__(self, inputQueue, outputQueue, attrToLog=[None], filename=None):
        self.inputQueue = inputQueue
        self.outputQueue = outputQueue
        self.dbEntryList = []
        self.datenDict = defaultdict(dict)
        self.attrToLog = attrToLog
        self.filename = filename
        self.bufferHandleInterval = 1
        self.bufferHandleLastExecute = 1
        self.saveDataInterval = 0
        self.saveDataLastExecute = 0
        self.entriesToAddToDB = [] #collect the entries that are supposed to be added to the db

    def run(self):
        while True:
            if not self.inputQueue.empty():
                #print("found data im Posteingang")
                message = self.inputQueue.get()
                self.addMeasurement(message)

            if self.bufferHandleLastExecute + self.bufferHandleInterval < time.time() and self.datenDict:
                self.bufferHandleLastExecute = time.time()
                self.handleBuffer()

            if self.saveDataLastExecute + self.saveDataInterval < time.time() and self.entriesToAddToDB:
                self.saveDataLastExecute = time.time()
                #self.addToDB()
                self.addToCSV()

    def run_once(self):
        if not self.inputQueue.empty():
            #print("found data im Posteingang")
            message = self.inputQueue.get()
            self.addMeasurement(message)

        if self.bufferHandleLastExecute + self.bufferHandleInterval < time.time() and self.datenDict:
            self.bufferHandleLastExecute = time.time()
            self.handleBuffer()

        if self.saveDataLastExecute + self.saveDataInterval < time.time() and self.entriesToAddToDB:
            self.saveDataLastExecute = time.time()
            #self.addToDB()
            self.addToCSV()


    def addMeasurement(self, entry):
        timestamp = entry.timestamp.isoformat() if hasattr(entry.timestamp, "isoformat") else str(entry.timestamp)
        timestamp = timestamp[:21] #remove all the parts behind the 21. character to the format should always look like this: 2025-06-29T12:00:00.1
        #print(timestamp)
        self.datenDict[timestamp]["time"] = timestamp
        self.datenDict[timestamp][entry.topic] = entry.value
        #self.datenDict[timestamp]["entryAge"] = time.time()
            

    def handleBuffer(self):
        entriesToDelete = []
        now = datetime.now()
        for timestamp, item in self.datenDict.items():
            allAttrContained = True
            for attr in self.attrToLog:         #check of the entry has all the attributes that the entry needs to be entered into the database
                if item.get(attr) is None:
                    allAttrContained = False
                    #print(self.datenDict[timestamp])
                    #print(attr + "is not contained")
                    break
            if allAttrContained:
                #print("all attributes contained")
                self.entriesToAddToDB.append(self.datenDict[timestamp])
                entriesToDelete.append(timestamp)

        #print(self.datenDict)

        #print(self.entriesToAddToDB) #actually write the code that adds stuff to the db

        #for timestamp in entriesToDelete:
        #    print(self.datenDict[timestamp])

        for timestamp in entriesToDelete: #delete before checking the times, to avoid iterating over it if its already being deleted
            del self.datenDict[timestamp]
        entriesToDelete = []


        if self.datenDict:
            for timestamp in list(self.datenDict.keys()):
                #print("Content of DatenDict")
                #print(self.datenDict[timestamp])
                dataTime = datetime.fromisoformat(timestamp)
                if now - dataTime > timedelta(seconds=10):
                    entriesToDelete.append(timestamp)
                
            for timestamp in entriesToDelete:
                print("Missing Information in Data Row:")
                print(self.datenDict[timestamp])
                del self.datenDict[timestamp]
            
    def addToDB(self):
        if self.filename is None:
            now = datetime.now()
            self.filename = "Messung"+str(now.strftime("%Y-%m-%d")+"T"+now.strftime("%H:%M"))
            
        
        df = pd.DataFrame(self.entriesToAddToDB)
        #print(df)
        self.entriesToAddToDB = []

    def addToCSV(self):
        if self.filename is None or self.filename == "":
            now = datetime.now()
            self.filename = "Messung"+str(now.strftime("%Y-%m-%d")+"T"+now.strftime("%H_%M"))

        df = pd.DataFrame(self.entriesToAddToDB, columns=self.attrToLog)
        #print("saving following data to the csv")
        print(df)
        df.to_csv((str(self.filename)+".csv"), mode="a", header=not os.path.exists(self.filename+".csv"), index=False)
        self.entriesToAddToDB = []


def testClass():
    controlInputQueue = multiprocessing.Queue()
    controlOutputQueue = multiprocessing.Queue()
    loggerTest = dataLoggerClass(inputQueue=controlInputQueue, outputQueue=controlOutputQueue, attrToLog=["temperature", "current", "voltage"], filename="Test2")

    while True:
        loggerTest.run_once()
        now = datetime.now()
        timeNow = now.strftime("%Y-%m-%d")+"T"+now.strftime("%H:%M:%S.%f")[:-3]

        newEntry = interMessage(target="dataLogger", topic="v1", value=4, timestamp=timeNow)
        controlInputQueue.put(newEntry)

        newEntry = interMessage(target="dataLogger", topic="v2", value=5, timestamp=timeNow)
        controlInputQueue.put(newEntry)
        
        newEntry = interMessage(target="dataLogger", topic="voltage", value=1, timestamp=timeNow)
        controlInputQueue.put(newEntry)

        newEntry = interMessage(target="dataLogger", topic="current", value=2, timestamp=timeNow)
        controlInputQueue.put(newEntry)

        newEntry = interMessage(target="dataLogger", topic="temperature", value=3, timestamp=timeNow)
        controlInputQueue.put(newEntry)

        time.sleep(1)

#testClass()

#| Emitter\_ID | t\_abs (min) | I\_emit (µA) | V\_extr (V) | T\_emitter (°C) | P\_vac (mbar) | Setpoint\_I (µA) | Cum\_emission\_time (min) | Cum\_charge (µC) | Health\_Index | Label\_RUL (min) |
#| ----------- | ------------ | ------------ | ----------- | --------------- | ------------- | ---------------- | ------------------------- | ---------------- | ------------- | ---------------- |
#| E001        | 0            | 5.01         | 1050        | 800             | 1e-7          | 5                | 0                         | 0.0              | 1.0           | 1500             |
#| E001        | 1            | 5.01         | 1050        | 802             | 1e-7          | 5                | 1                         | 0.3              | 0.999         | 1499             |
#| …           | …            | …            | …           | …               | …             | …                | …                         | …                | …             | …                |
#| E001        | 735          | 14.9         | 1120        | 860             | 1e-7          | 15               | 735                       | 145.3            | 0.68          | 765              |




