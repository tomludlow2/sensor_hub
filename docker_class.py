#Dccker Pi Class
import smbus, os, socket, json, time

class docker_class:

    def read_docker(self):
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
        sensorHubInput.append(0x00)
        #This function, when called, will return simply a dictionary of the environmental sensors
        for i in range(TEMP_REG,HUMAN_DETECT + 1):
            sensorHubInput.append(bus.read_byte_data(DEVICE_ADDR, i))

        snapshot = {}
        if sensorHubInput[STATUS_REG] & 0x01 :
            snapshot["ext_temperature"] = "over"
            snapshot["error"] = 1
        elif sensorHubInput[STATUS_REG] & 0x02 :
            snapshot["ext_temperature"] = "disconnect"
            snapshot["error"] = 1
        else :
            snapshot["ext_temperature"] = sensorHubInput[TEMP_REG]



        if sensorHubInput[STATUS_REG] & 0x04 :
            snapshot["light"] = "over"
            snapshot["error"] = 1
        elif sensorHubInput[STATUS_REG] & 0x08 :
            snapshot["light"] = "error"
            snapshot["error"] = 1
        else :
            #Need to Bitshift the high and low light sensors
            #Units = Lux
            brightness = (sensorHubInput[LIGHT_REG_H] << 8 | sensorHubInput[LIGHT_REG_L])
            snapshot['light'] = brightness



        #Store the on-board temperature sensor
        temp_onboard = sensorHubInput[ON_BOARD_TEMP_REG]
        snapshot['dht11_temperature'] = temp_onboard

        #Store the on-board humidity sensor
        humid_onboard = sensorHubInput[ON_BOARD_HUMIDITY_REG]
        snapshot['dht11_humidity'] = humid_onboard

        #If there is an error, store this as a message
        if sensorHubInput[ON_BOARD_SENSOR_ERROR] != 0 :
            snapshot['onboard_info'] = "On Board Sensor may not be up to date"
            snapshot["error"] = 1

        #Store the input from the barometer
        #Again this needs bitshifting (as a 24 bit integer)

        if sensorHubInput[BMP280_STATUS] == 0 :
            temp_280 = sensorHubInput[BMP280_TEMP_REG]
            pres_280 = (sensorHubInput[BMP280_PRESSURE_REG_L] | sensorHubInput[BMP280_PRESSURE_REG_M] << 8 | sensorHubInput[BMP280_PRESSURE_REG_H] << 16)
            snapshot["bmp280_temperature"] = temp_280
            snapshot["bmp280_pressure"] = pres_280
        else :
            snapshot["bmp280_temperature"] = "error"
            snapshot["bmp280_pressure"] = "error"
            snapshot["error"] = 1

        #Finally - return the dictionary
        return snapshot

    def __init__(self):
        print("Docker Class Initiated")

    def print_reading(self):
        print("Docker Pi Sensor Hub - Collecting data for you - now printing")
        readings = self.read_docker()
        print( json.dumps(readings, indent=4, sort_keys=True) )

    def get_dict(self):
        print("Getting a dictionary of data for you")
        print("Returns [ERR_CODE, dict]")
        error_codes = {
            1:"Data is intact",
            0:"At least one field has an error",
            2:"Board may be out of date",
            3:"Failed"
        }
        print( json.dumps(error_codes, indent=4, sort_keys=True) )
        r = self.read_docker()
        if( (r.get("onboard_info") == None) and (r.get("error") == None) ):
            return [1,r]
        elif( r.get("error") != None ):
            return [0,r]
        elif( r.get("onboard_info") != None):
            return [2,r]
        else:
            return [3,0]

    def get_api_packet(self):
        print("Getting you a packet that can be sent to the weather_api")
        print("This comes as an array of dictionaries")
        r = self.read_docker()
        if( r.get("onboard_info") == None):
            dht11_temperature = {"dht11_temperature":r['dht11_temperature']}
            dht11_humidity = {"dht11_humidity":r['dht11_humidity']}
        else:
            dht11_temperature = {"dht11_temperature":"null"}
            dht11_humidity = {"dht11_humidity":"null"}


        if( r['bmp280_temperature'] != "error"):
            bmp280_temperature = {"bmp280_temperature":r['bmp280_temperature']}
            bmp280_pressure = {"bmp280_pressure":r['bmp280_pressure']}
        else:
            bmp280_temperature = {"bmp280_temperature":"null"}
            bmp280_pressure = {"bmp280_pressure":"null"}

        if( r['ext_temperature'] != "over" and r['ext_temperature'] != "disconnect"):
            ext_temperature = {"ext_temperature":r['ext_temperature']}
        else:
            ext_temperature = {"ext_temperature":"null"}

        if( r['light'] != "over" and r['light'] != "error"):
            light = {"light":r['light']}
        else:
            light = {"light":"null"}
        arr = [dht11_temperature, dht11_humidity, bmp280_temperature,bmp280_pressure, ext_temperature, light]
        return arr;
    
    def get_ir_detection_now(self):
        DEVICE_BUS = 1
        DEVICE_ADDR = 0x17
        HUMAN_DETECT = 0x0D
        bus = smbus.SMBus(DEVICE_BUS)
        ir_detect = bus.read_byte_data(DEVICE_ADDR, HUMAN_DETECT)
        print(ir_detect)

    def get_ir_detection_period(self, duration):
        print("Info: Listening for movement, will do this for " + str(duration) + "seconds")
        DEVICE_BUS = 1
        DEVICE_ADDR = 0x17
        HUMAN_DETECT = 0x0D
        bus = smbus.SMBus(DEVICE_BUS)
        
        move_count = 0.0
        total_duration = duration*5
        i = 0
        while( i < total_duration):
            ir_detect = bus.read_byte_data(DEVICE_ADDR, HUMAN_DETECT)
            if( ir_detect ):
                move_count += 1.0
            time.sleep(0.2)
            i += 1

        print("Info: Watched for " + str(duration) + "s - counted " + str(move_count) + " bits of movement")
        percentage_movement = move_count / (duration*5) * 100
        print("Info: Movement Percentage = " + str(percentage_movement) + "%")