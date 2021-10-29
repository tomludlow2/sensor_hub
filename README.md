# sensor_hub
DockerPi SensorHub Repo

Source and Credit:
https://wiki.52pi.com/index.php/DockerPi_Sensor_Hub_Development_Board_SKU:_EP-0106
For the inital install allowing further development

For use with the DockerPi Sensor Hub
- Files include the evolutions of the system through simple in/out reading
- Through to generating JSON outputs
- Eventually pushing to mysql_databases

# How to use
1. With RPI switched off: install the HAT directly onto RPI
2. Turn on rpi and connect via SSH
3. Clone this Git repo to a folder
4. To get it to "just work" - python docker_v1.py
5. This will output the info you need!

# For Interest
In regards to input devices:
In order to collect larger numbers we must do a Bit Shift
Consider that the numbers are communicated in bit form
That is for example: the ones and zeros that code for an integer might be 00000100 = 4, 00001010 = 10 
The inputs received are as bytes = 8 bits in one go
The maximum number that can be held in a byte is 256, therefore there is a set of HIGH and LOW bytes for each reading
So we need to move what is essential input1 = 00100110   and input2 = 01011101 *example numbers
To
0010011001011101 -  input1input2
So we perform a Bitshift to the left of the higher one
Let the higher bit = 00000010, this would become 00000010 00000000 - codes for 512
Let the higher bit = 00000001, (instead) becomes 00000001 00000000 - codes for 256
So we essentially bitshift and then join the low bit
Typically for the sensor, the HIGH bit will be 512, so we add the low bit to 512 to get to the LUX reading


# docker_class
This is a class that allows you to extract values very easily from the DockerPi Sensor Hub Board
See class_test.py for examples of how to use, but essentially:
- Import - import docker_class
- sensor = docker_class.docker_class()
- Then use a variety of functions:
- sensor.read_docker() will return a raw dictionary from the bus (may include errors)
- sensor.get_dict()  will return an array of [ERR_CODE, dict]. 
- d = sensor.get_dict();    if(d[0] == 1) {values = d[1])} else {there is an error}
- sensor.print_reading() will simply print a JSON pretty dict
- sensor.get_api_packet()  returns an error-proof array of data for integration with [https://github.com/tomludlow2/weather_api]
- simply get the packet: packet = sensor.get_api_packet() and then send to the api with api.send_multiple(packet)
- The IR functions are sensor.get_ir_detection_now() and returns 1/0 for whether motion is detected
- get_ir_detection_period(duration(seconds)) returns a percentage movement over the duration of seconds (every 0.2 seconds interval)

