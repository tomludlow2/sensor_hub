import smbus, os, socket, json

DEVICE_BUS = 1
DEVICE_ADDR = 0x17

TEMP_REG = 0x01
LIGHT_REG_L = 0x02
LIGHT_REG_H = 0x03
STATUS_REG = 0x04
ON_BOARD_TEMP_REG = 0x05
ON_BOARD_HUMIDITY_REG = 0x06
ON_BOARD_SENSOR_ERROR = 0x07
BMP280_TEMP_REG = 0x08
BMP280_PRESSURE_REG_L = 0x09
BMP280_PRESSURE_REG_M = 0x0A
BMP280_PRESSURE_REG_H = 0x0B
BMP280_STATUS = 0x0C
HUMAN_DETECT = 0x0D

bus = smbus.SMBus(DEVICE_BUS)

sensorHubInput = []

sensorHubInput.append(0x00) #

#Create a Dictionary (Python assoc array) to hold our data snapshot
#Within that dict, store the file name 
snapshot = {
    "script" : os.path.basename(__file__),
    "host": socket.gethostname()
}

for i in range(TEMP_REG,HUMAN_DETECT + 1):
    sensorHubInput.append(bus.read_byte_data(DEVICE_ADDR, i))

#Store the distance temperature probe temperature (Black Probe)
if sensorHubInput[STATUS_REG] & 0x01 :
    snapshot["temp_probe"] = "over"
elif sensorHubInput[STATUS_REG] & 0x02 :
    snapshot["temp_probe"] = "disconnect"
else :
    snapshot["temp_probe"] = sensorHubInput[TEMP_REG]


#In order to collect larger numbers we must do a Bit Shift
#Consider that the numbers are communicated in bit form
#That is for example: the ones and zeros that code for an integer might be 00000100 = 4, 00001010 = 10 
#The inputs received are as bytes = 8 bits in one go
#The maximum number that can be held in a byte is 256, therefore there is a set of HIGH and LOW bytes for each reading
#So we need to move what is essential input1 = 00100110   and input2 = 01011101 *example numbers
#To
#0010011001011101 -  input1input2
#So we perform a Bitshift to the left of the higher one
#Let the higher bit = 00000010, this would become 00000010 00000000 - codes for 512
#Let the higher bit = 00000001, (instead) becomes 00000001 00000000 - codes for 256
#So we essentially bitshift and then join the low bit
#Typically for the sensor, the HIGH bit will be 512, so we add the low bit to 512 to get to the LUX reading


if sensorHubInput[STATUS_REG] & 0x04 :
    snapshot['brightness'] = "over"
elif sensorHubInput[STATUS_REG] & 0x08 :
    snapshot['brightness'] = "error"
else :
    #Need to Bitshift the high and low light sensors
    #Units = Lux
    brightness = (sensorHubInput[LIGHT_REG_H] << 8 | sensorHubInput[LIGHT_REG_L])
    snapshot['brightness'] = brightness


#Store the on-board temperature sensor
snapshot["temp_onboard"] = sensorHubInput[ON_BOARD_TEMP_REG]
snapshot["humidity_onboard"] = sensorHubInput[ON_BOARD_HUMIDITY_REG]

#If there is an error, store this as a message
if sensorHubInput[ON_BOARD_SENSOR_ERROR] != 0 :
    snapshot["onboard_info"] = "On Board Sensor may not be up to date"

#Store the input from the barometer
#Again this needs bitshifting (as a 24 bit integer)

if sensorHubInput[BMP280_STATUS] == 0 :
    snapshot["temp_barometer"] = sensorHubInput[BMP280_TEMP_REG]
    snapshot["pressure"] = (sensorHubInput[BMP280_PRESSURE_REG_L] | sensorHubInput[BMP280_PRESSURE_REG_M] << 8 | sensorHubInput[BMP280_PRESSURE_REG_H] << 16)
else :
    snapshot["temp_barometer"] = "error"
    snapshot["pressure"] = "error"

#Store whether a detection (IR) has occurred
if sensorHubInput[HUMAN_DETECT] == 1 :
    snapshot["ir_detect"] = 1
else:
    snapshot["ir_detect"] = 0

print( json.dumps(snapshot, indent=4, sort_keys=True) )