import time
import argparse
import sys, traceback
import threading
import RPi.GPIO as GPIO
import smbus

import pymodbus

from pymodbus.server.async import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext

from pymodbus.client.sync import ModbusTcpClient
from pymodbus.server.sync import ModbusTcpServer

global server
global ip

def ServerThread(e):
	global server
	# Configure the service logging
	#import logging
	#logging.basicConfig()
	#log = logging.getLogger()
	#log.setLevel(logging.DEBUG)

	# Initialize your data store
	store = ModbusSlaveContext(
		di = ModbusSequentialDataBlock(0, [17]*100),
		co = ModbusSequentialDataBlock(0, [17]*100),
		hr = ModbusSequentialDataBlock(0, [17]*100),
		ir = ModbusSequentialDataBlock(0, [17]*100))
	context = ModbusServerContext(slaves=store, single=True)
	 
	# Initialize the server information
	identity = ModbusDeviceIdentification()
	identity.VendorName  = 'Pymodbus'
	identity.ProductCode = 'PM'
	identity.VendorUrl   = 'http://github.com/bashwork/pymodbus/'
	identity.ProductName = 'Pymodbus Server'
	identity.ModelName   = 'Pymodbus Server'
	identity.MajorMinorRevision = '1.0'


	# Run the server 
	# StartTcpServer(context, identity=identity, address=(args.ip, 502))
	server = ModbusTcpServer(context, identity=identity, address=(ip, 502))
	print 'Server started'
	server.serve_forever(0.1)
	print 'Server stopped'

def TemperatureUpdateThread(update_interval, e):
	print 'TemperatureUpdateThread'
	client = ModbusTcpClient(ip)
	while True:
		if not e.isSet():
			tfile = open("/sys/bus/w1/devices/28-00000625a0cd/w1_slave") 
			text = tfile.read()  
			tfile.close() 
			secondline = text.split("\n")[1] 
			temperaturedata = secondline.split(" ")[9] 
			temperature = float(temperaturedata[2:])
			client.write_register(0, temperature)
			print (temperature/1000)
			time.sleep(update_interval)
		else:
			break
	client.close()
	print 'Temperature sensor thread stoped'

def LEDUpdateThread(pin, update_interval, e):
	print 'LEDUpdateThread'
	client = ModbusTcpClient(args.ip)
	GPIO.setup(pin, GPIO.OUT)
	while True:
		if not e.isSet():
			result = client.read_coils(0, 1)
			if result is not None:
				pin_status = result.bits[0]
				GPIO.output(pin, pin_status)
				print pin_status
			time.sleep(update_interval)
		else:
			break
	client.close()
	print 'LED thread stoped'
	
def RGBLEDUpdateThread(pins, update_interval, e):
	print 'RGBLEDUpdateThread'
	client = ModbusTcpClient(ip)
	
	# Setup pins mode
	for i in range(0, 3):
		GPIO.setup(pins[i], GPIO.OUT)

	while True:
		if not e.isSet():
			result = client.read_coils(10, 3)
			print 'RGB LED. R:', result.bits[0], 'G:', result.bits[1], 'B:', result.bits[2]
			for i in range(0, 3):
				GPIO.output(pins[i], result.bits[i])
			time.sleep(update_interval)
		else:
			break
	client.close()
	print 'RGB LED Stopped'
	
def ButtonUpdateThread(pin, update_interval, e):
	print 'ButtomUpdateThread'
	client = ModbusTcpClient(ip)
	
	# Setup pin mode
	GPIO.setup(pin, GPIO.IN)

	while True:
		if not e.isSet():
			pin_status = GPIO.input(pin)
			print status
			client.write_coil(20, pin_status)
			time.sleep(update_interval)
		else:
			break
	client.close()
	print 'Button Stopped'
	
def ColorSensorUpdateThread(update_interval, e):
	print 'ColorSensorUpdateThread'
	client = ModbusTcpClient(ip)
	
	bus = smbus.SMBus(1)
	# I2C address 0x29
	# Register 0x12 has device ver. 
	# Register addresses must be OR'ed with 0x80
	bus.write_byte(0x29,0x80|0x12)
	ver = bus.read_byte(0x29)
	# version # should be 0x44
	if ver == 0x44:
		print "Device found\n"
		bus.write_byte(0x29, 0x80|0x00) # 0x00 = ENABLE register
		bus.write_byte(0x29, 0x01|0x02) # 0x01 = Power on, 0x02 RGB sensors enabled
		bus.write_byte(0x29, 0x80|0x14) # Reading results start register 14, LSB then MSB
		while True:
			if not e.isSet():
				data = bus.read_i2c_block_data(0x29, 0)
				clear = clear = data[1] << 8 | data[0]
				red = data[3] << 8 | data[2]
				green = data[5] << 8 | data[4]
				blue = data[7] << 8 | data[6]
				print 'Color Sensor. C:', clear, 'R:', red, 'G:', green, 'B:', blue
				
				client.write_register(10, clear)
				client.write_register(11, red)
				client.write_register(12, green)
				client.write_register(13, blue)
				
				time.sleep(update_interval)
			else:
				break
	else: 
		print 'Color sensor not found'
		
	client.close()
	print 'Color Sensor Stopped'


if __name__ == "__main__":
	global server
	global ip
	print "=== Modbus Device ==="
	parser = argparse.ArgumentParser(description='Modbus server')
	parser.add_argument('ip',  default='localhost', help='IP adress of modbus server')
	args = parser.parse_args()
	ip = args.ip
	
	
	e_exit = threading.Event()
	
	thServer = threading.Thread(name='ServerThread', target=ServerThread, args=(e_exit,))
	thTemperature = threading.Thread(name='TemperatureUpdateThread', target=TemperatureUpdateThread, args=(1, e_exit,))
	thLED = threading.Thread(name='LEDUpdateThread', target=LEDUpdateThread, args=(21, 0.8, e_exit,))
	
	thRGBLED = threading.Thread(name='RGBLEDUpdateThread', target=RGBLEDUpdateThread, args=([18, 23, 24], 0.5, e_exit,))
	thButton = threading.Thread(name='ButtonUpdateThread', target=ButtonUpdateThread, args=(20, 0.1, e_exit,))
	#thColorSensor = threading.Thread(name='ColorSensorUpdateThread', target=ColorSensorUpdateThread, args=(1, e_exit,))
	
	# Init hardware
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	
	thServer.start()
	time.sleep(1)
	
	# Start clients
	thLED.start()
	time.sleep(1)
	thTemperature.start()
	time.sleep(1)
	thRGBLED.start()
	time.sleep(1)
	thButton.start()

	# Wait for keyboard interrupt
	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		print "Stopping program"
	except Exception:
		traceback.print_exc(file=sys.stdout)
		
	
	
	# Set stop event for clients
	e_exit.set()

	# Wait until all clients stop
	# or thColorSensor.isAlive()
	while thLED.isAlive() or thTemperature.isAlive() or thRGBLED.isAlive() or thButton.isAlive():
		time.sleep(0.01)
	
	# Shutdown server
	server.shutdown()

	# Wait until server shutdown
	while thServer.isAlive():
		time.sleep(0.01)
		
	# Clean up
	GPIO.cleanup()
		
	# Stop the program
	print 'Done'
	sys.exit(0)