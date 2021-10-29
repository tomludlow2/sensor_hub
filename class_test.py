import docker_class as sensor
import json

s = sensor.docker_class()

print("Test the print function")
s.print_reading()

print("\nTest the get_dict function")
readings_raw = s.get_dict()

if( readings_raw[0] == 1 ):
	print("Data is intact, here it is")
	print( json.dumps(readings_raw[1], indent=4, sort_keys=True) )
else:
	print("There is a problem with the data - would need manual submission")


print("\nTest the get_api_packet function")
packet = s.get_api_packet()
print( json.dumps(packet, indent=4, sort_keys=True) )


print("\nTest the IR Motion Sensor Function")
s.get_ir_detection_now()

s.get_ir_detection_period(5)
