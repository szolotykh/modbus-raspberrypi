import RPi.GPIO as GPIO
import time
import argparse
import sys, traceback

from pymodbus.client.sync import ModbusTcpClient

GPIO_Pins = [3, 5, 7, 8, 10, 11, 12, 13, 15, 16, 18, 19, 21, 22, 23, 24, 26]

led = 21
status = 1

if __name__ == "__main__":
	
	print "=== Modbus client ==="
	parser = argparse.ArgumentParser(description='Modbus client')
	parser.add_argument('ip',  default='localhost', help='IP adress of modbus server')
	args = parser.parse_args()
	
	client = ModbusTcpClient(args.ip)

	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(led, GPIO.OUT)
	
	try:
		while True:
			result = client.read_coils(1, 1)
			status = result.bits[0]
			print status
			GPIO.output(led, status)
	except KeyboardInterrupt:
		print "Exiting"
	except Exception:
		traceback.print_exc(file=sys.stdout)	
	GPIO.cleanup()
	client.close()
	sys.exit(0)
