#Dccker Pi Version 3 reader
#This script loads in the docker information, as well as the tomludlow2/weather_api
#It then stores the data in the api, and prints it out

import smbus, os, socket, json
import weather_api.weather_api as api

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

#Build a series of dictionaries to store some data:
#These will be passed to the API
dht11_temperature = {}
dht11_humidity = {}
bmp280_temperature = {}
bmp280_pressure = {}
ext_temperature = {}
light = {}

#Define the api
a = api.API()

for i in range(TEMP_REG,HUMAN_DETECT + 1):
    sensorHubInput.append(bus.read_byte_data(DEVICE_ADDR, i))

#Store the distance temperature probe temperature (Black Probe)
if sensorHubInput[STATUS_REG] & 0x01 :
    print("Error: External Probe Over")
elif sensorHubInput[STATUS_REG] & 0x02 :
    print("Error: External Probe Disconnected")
else :
    t = sensorHubInput[TEMP_REG]
    a.save_reading("ext_temperature", t)
    ext_temperature["ext_temperature"] = t


if sensorHubInput[STATUS_REG] & 0x04 :
    print("Error: Light sensor over")
elif sensorHubInput[STATUS_REG] & 0x08 :
    print("Error: Light sensor error")
else :
    #Need to Bitshift the high and low light sensors
    #Units = Lux
    brightness = (sensorHubInput[LIGHT_REG_H] << 8 | sensorHubInput[LIGHT_REG_L])
    a.save_reading("light", brightness)
    light["light"] = brightness


#Store the on-board temperature sensor
temp_onboard = sensorHubInput[ON_BOARD_TEMP_REG]
a.save_reading("dht11_temperature", temp_onboard)
dht11_temperature["dht11_temperature"] = temp_onboard

#Store the on-board humidity sensor
humid_onboard = sensorHubInput[ON_BOARD_HUMIDITY_REG]
a.save_reading("dht11_humidity", humid_onboard)
dht11_humidity["dht11_humidity"] = humid_onboard

#If there is an error, store this as a message
if sensorHubInput[ON_BOARD_SENSOR_ERROR] != 0 :
    print("On Board Sensor may not be up to date")

#Store the input from the barometer
#Again this needs bitshifting (as a 24 bit integer)

if sensorHubInput[BMP280_STATUS] == 0 :
    temp_280 = sensorHubInput[BMP280_TEMP_REG]
    pres_280 = (sensorHubInput[BMP280_PRESSURE_REG_L] | sensorHubInput[BMP280_PRESSURE_REG_M] << 8 | sensorHubInput[BMP280_PRESSURE_REG_H] << 16)
    a.save_reading("bmp280_temperature", temp_280)
    bmp280_temperature["bmp280_temperature"] = temp_280

    a.save_reading("bmp280_pressure", pres_280)
    bmp280_pressure["bmp280_pressure"] = pres_280
else :
    print("Error: BMP280 error")

#Save the info in the API config files
a.save()

#Generate a reading object - this could be used to send to the server..
reading = [dht11_temperature, dht11_humidity, bmp280_pressure, bmp280_temperature, ext_temperature, light ]
print("\n\nHere is the READING:\n")
print( json.dumps(reading, indent=4, sort_keys=True) )