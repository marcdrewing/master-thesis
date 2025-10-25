import serial
import serial.tools.list_ports
from datetime import datetime
import random
from interMessage import interMessage
import time
import pfeiffer_vacuum_protocol as pvp

"""
 Addresses depend on the information and the number of connected devices
 base device: 100
  1)  (Option 0)  Option Data                 111     (Data / USB / µSD)
  2)  (Option 1)  Gauge/IO                    131
                  Parameter Gauge/IO.gauge    132
                  Parameter Gauge/IO.gauge    133
  3)  (Option 2)  Gauge/IO                    121
                  Parameter Gauge/IO.gauge    122
                  Parameter Gauge/IO.gauge    123
                  
"""

"""
Pfeiffer Vacuum OmniControl – Parameter Set (Seite 9–10)
--------------------------------------------------------

3.2 Control Commands
--------------------------------------------------------
#   ID   | Indicator     | Description        | Function Description               | Data Type | Access | Min     | Max     | Default
--------|---------------|--------------------|------------------------------------|-----------|--------|---------|---------|---------
040     | DeGas         | DeGas procedure    | Cleaning measuring element         | 6         | RW     | 000000  | 000001  | 000000
041     | Sens OnOff    | BA/CC on/off       | Switches cold cathode or BA/CC     | 7         | RW     | 000000  | 000001  | 000000
070     | Dir DigOut    | Digital outputs    | Reset / Set / Do not change        | 1         | RW     | 000000  | 999999  | 222200
071     | Dir RelOut    | Relay outputs      | Reset / Set / Do not change        | 1         | RW     | 000000  | 999999  | 222200

--------------------------------------------------------

3.3 Status Requests
--------------------------------------------------------
#   ID   | Indicator     | Description        | Function Description               | Data Type | Access
--------|---------------|--------------------|------------------------------------|-----------|--------
303     | Error code    | Error code         | Returns current error code         | 4         | R
312     | FW version    | Firmware version   | Returns firmware version           | 4         | R
349     | ElecName      | Designation        | Returns device name                | 4         | R
354     | HW version    | Hardware version   | Returns hardware version           | 4         | R
355     | Serial No     | Serial number      | Returns serial number              | 11        | R
386     | Dir DigInp    | Digital inputs     | Returns digital input status       | 1         | R
387     | Dir AlgInp    | Analog input       | Returns analog input value         | 2         | R       | Unit: V
388     | Order Code    | Order number       | Returns device order number        | 11        | R

--------------------------------------------------------

3.4 Set Value Settings
--------------------------------------------------------
#   ID   | Indicator     | Description        | Function Description               | Data Type | Access | Unit  | Min     | Max     | Default
--------|---------------|--------------------|------------------------------------|-----------|--------|--------|---------|---------|---------
727     | Dir AlgOut    | Analog output      | Output value                       | 2         | RW     | V      | 000000  | 999999  | 000000
740     | Pressure      | Pressure value     | W = 0 → zero on, else → zero off   | 10        | RW     | hPa    | 000000  | 999999  | —
742     | UserGasCor    | Correction factor  | Gas correction factor              | 2         | RW     | —      | 000000  | 999999  | 000100
797     | BaseAdr       | Interface address  | RS485 device address               | 1         | RW     | —      | 000000  | 999999  | 000100


Hinweise:
- RW = Read/Write
- R  = Read only
- Datenformattypen siehe Seite 6 im Handbuch (z. B. 1 = u_integer, 2 = u_real, 4 = string, 6 = boolean_old, 7 = u_short_int, 10 = u_expo_new, 11 = string16)
"""

"""
Pfeiffer Vacuum OmniControl – Exakte Adressierung der Parameter (Seite 11–13)
===============================================================================

4.2.1 Addressing gauge/IO – Parameter 040–354
---------------------------------------------
ID    | Indicator     | Access | Data Type | Gültige Adressen
------|---------------|--------|-----------|------------------------------------------------
040   | DeGas         | RW     | 6         | 112, 122, 132, 142
041   | Sens OnOff    | RW     | 7         | 112, 122, 132, 142
070   | Dir DigOut    | RW     | 1         | 113, 123, 133, 143
071   | Dir RelOut    | RW     | 1         | 113, 123, 133, 143
303   | Error code    | R      | 4         | 101, 111, 112, 113, 121, 122, 123, 131, 132, 133, 141, 142, 143
312   | FW version    | R      | 4         | 101, 111, 112, 113, 121, 122, 123, 131, 132, 133, 141, 142, 143
349   | Name          | R      | 4         | 101, 111, 112, 113, 121, 122, 123, 131, 132, 133, 141, 142, 143
354   | HW version    | R      | 4         | 101, 111, 112, 113, 121, 122, 123, 131, 132, 133, 141, 142, 143

4.2.2 Addressing gauge/IO – Parameter 355–797
---------------------------------------------
ID    | Indicator      | Access | Data Type | Einheit | Gültige Adressen
------|----------------|--------|-----------|---------|------------------------------------------------
355   | Serial No      | R      | 11        | —       | 101
386   | Dir DigInp     | R      | 1         | —       | 113, 123, 133, 143
387   | Dir AlgInp     | R      | 2         | V       | 113, 123, 133, 143
388   | Order Code     | R      | 11        | —       | 101
727   | Dir AlgOut     | RW     | 2         | V       | 113, 123, 133, 143
740   | Pressure       | RW     | 10        | hPa     | 112, 122, 132, 142
742   | UserGasCor     | RW     | 2         | —       | 112, 122, 132, 142
797   | BaseAdr        | RW     | 1         | —       | 101

Adressstruktur:
---------------
101 : Base device (OmniControl)
111 : Option 0 – gauge/IO data
112 : Option 0 – gauge/IO.gauge
113 : Option 0 – gauge/IO.IO
121 : Option 1 – gauge/IO data
122 : Option 1 – gauge/IO.gauge
123 : Option 1 – gauge/IO.IO
131 : Option 2 – gauge/IO data
132 : Option 2 – gauge/IO.gauge
133 : Option 2 – gauge/IO.IO
141 : Option 3 – gauge/IO data
142 : Option 3 – gauge/IO.gauge
143 : Option 3 – gauge/IO.IO

Hinweise:
---------
- Adressen mit `.IO` (113, 123…) gelten für digitale Ein-/Ausgänge
- `Sens OnOff` ist **nicht** für `.gauge` oder `.IO` gültig, sondern nur für bestimmte `.data`-Adressen
- Die Gültigkeit je Parameter ist exakt aus den Tabellen übernommen

"""

class pfeifferInterfaceClass(object):
    def __init__(self, inputQueue, outputQueue, serialConnection=None, connectionEstablished=False, measuringActive=[False,False,False,False], measurementInterval=1):
        self.outputQueue = outputQueue
        self.inputQueue = inputQueue
        self.serialConnection = serialConnection
        self.connectionEstablished = connectionEstablished
        self.measuringActive = measuringActive
        self.measurementInterval = measurementInterval
        self.testMode = False
        

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

            if message.task == "getPressure":
                measuredPressure = self.getPressure(channel=message.channel)
                now = datetime.now()
                returnMessage = interMessage(target="procedureProcess", task="pressureMeasurement", topic="pressure")
                returnMessage.channel = message.channel
                returnMessage.value = measuredPressure
                returnMessage.timestamp = now.strftime("%Y-%m-%d")+"T"+now.strftime("%H:%M:%S.%f")[:-3]
                self.outputQueue.put(returnMessage)

            if message.task == "startMeasuring":
                self.startMeasuring(message.channel)
                
            if message.task == "stopMeasuring":
                if message.channel is None:
                    message.channel = 0
                self.stopMeasuring(message.channel)

            if message.task == "setMeasurementInterval":
                self.setMeasurementInterval(message.value)
                    

    def measureRoutine(self):
        startTime = time.time()*1000
        while not (startTime%100) == 0:
            startTime = time.time()*1000
            
        for i in range(0,3):
            if self.measuringActive[i]:
                measuredPressure = self.getPressure(channel=i)
                now = datetime.now()
                returnMessage = interMessage(target="dataLogger", topic="pressure")
                returnMessage.channel = 0
                returnMessage.value = measuredPressure
                returnMessage.timestamp = now.strftime("%Y-%m-%d")+"T"+now.strftime("%H:%M:%S.%f")[:-3]
                self.outputQueue.put(returnMessage)
            

    def startMeasuring(self, channel):
        self.measuringActive[channel] = True

    def stopMeasuring(self, channel):
        self.measuringActive[channel] = False

    def setMeasurementInterval(self, interval):
        self.measurementInterval = interval

########## Communication with ISEG Device ########################################################################################

    def startSerialConnection(self, serialPort):
        if not self.testMode:
            self.serialConnection = serial.Serial(serialPort, 9600, timeout=1)#, parity=serial.PARITY_EVEN, rtscts=1)
        self.connectionEstablished = True

    def serialSend(self, serialMessage):
        self.serialConnection.write((serialMessage+"\r"+"\n").encode('utf-8'))

    def serialRead(self):
        return self.serialConnection.read_until().decode('UTF-8')

    def sendCommand(self, command):
        if not self.connectionEstablished:
            print("Serial Connection for pfeiffer Device not yet established")
            return False
        self.serialSend(command)

    def getMeasurement(self, command):
        if not self.connectionEstablished:
            print("Serial Connection for pfeiffer Device not yet established")
            return None
        self.serialSend(command)
        measuredValue = self.serialRead()
        measuredValue = measuredValue.rstrip()
        return measuredValue

################################################################################################################

########### Functions of ISEG Device ###########################################################################
    
    def testConnection(self, addr=None):
        firmwareVersionAddr = [101, 111, 112, 113, 121, 122, 123, 131, 132, 133, 141, 142, 143]
        if addr is None:
            addr = firmwareVersionAddr[0]
        returnedMessage = read_software_version(self.serialConnection, addr, valid_char_filter=None)
        return returnedMessage

    def getPressure(self, channel=None, addr=None):
        pressureChannelAddr = [122, 132, 142]
        if addr is None:
            addr = pressureChannelAddr[channel]
        if addr is None and channel is None:
            print("Neither Channel nor Address defined for Pressure Measurement")
            return False
        if not self.testMode:
            return pvp.read_pressure(self.serialConnection, addr)
        return str(random.randint(1,100))



        
        
        
        
