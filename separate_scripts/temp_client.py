import RPi.GPIO as GPIO
import time
import argparse
import sys, traceback
from pymodbus.client.sync import ModbusTcpClient

update_interval = 0.5

if __name__ == "__main__":
	print "=== Modbus client (Temperature Sensor) ==="
	parser = argparse.ArgumentParser(description='Modbus client')
	parser.add_argument('ip',  default='localhost', help='IP adress of modbus server')
	args = parser.parse_args()
	client = ModbusTcpClient(args.ip)
	try:
		while True:
			tfile = open("/sys/bus/w1/devices/28-00000625a0cd/w1_slave") 
			text = tfile.read()  
			tfile.close() 
			secondline = text.split("\n")[1] 
			temperaturedata = secondline.split(" ")[9] 
			temperature = float(temperaturedata[2:])
			client.write_register(1, temperature)
			temperature = temperature / 1000
			print temperature
			time.sleep(update_interval)
	except KeyboardInterrupt:
		print 'Stopping program'
	except Exception:
		traceback.print_exc(file=sys.stdout)
	client.close()
	print 'Done'
	sys.exit(0)
		
		




