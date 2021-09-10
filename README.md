# sensor_hub
DockerPi SensorHub Repo

For use with the DockerPi Sensor Hub
- Files include the evolutions of the system through simple in/out reading
- Through to generating JSON outputs
- Eventually pushing to mysql_databases


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
