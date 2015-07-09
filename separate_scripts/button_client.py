import RPi.GPIO as GPIO
import time
import argparse
import sys, traceback

from pymodbus.client.sync import ModbusTcpClient

button_pin = 21
pin_status = 1
update_interval = 0.05

if __name__ == "__main__":
	
	print "=== Modbus client (Single button) ==="
	parser = argparse.ArgumentParser(description='Modbus client')
	parser.add_argument('ip',  default='localhost', help='IP adress of modbus server')
	args = parser.parse_args()
	
	client = ModbusTcpClient(args.ip)

	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(led, GPIO.IN)
	
	try:
		while True:	
			pin_status = GPIO.input(led)
			print status
			client.write_coil(20, pin_status)
			time.sleep(update_interval)
	except KeyboardInterrupt:
		print "Stopping program"
	except Exception:
		traceback.print_exc(file=sys.stdout)	
	GPIO.cleanup()
	client.close()
	print "Done"
	sys.exit(0)
