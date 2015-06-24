import RPi.GPIO as GPIO
import time
import argparse
import sys, traceback
from pymodbus.client.sync import ModbusTcpClient

if __name__ == "__main__":
	print "=== Modbus temperature sensor client ==="
	client = ModbusTcpClient('10.20.21.130')
	while True:
		tfile = open("/sys/bus/w1/devices/28-00000625a0cd/w1_slave") 
		text = tfile.read()  
		tfile.close() 
		secondline = text.split("\n")[1] 
		temperaturedata = secondline.split(" ")[9] 
		temperature = float(temperaturedata[2:])
		temperature = temperature / 1000
		client.write_register(1, temperature)
		print temperature
		time.sleep(1)
		
	client.close()	
		
		




