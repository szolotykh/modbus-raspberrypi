import RPi.GPIO as GPIO
import time
import argparse
import sys, traceback

from pymodbus.client.sync import ModbusTcpClient

LED_Pins = [3, 5, 7]
update_interval = 0.1

if __name__ == "__main__":
	
	print '=== Modbus client (RGB LED) ==='
	parser = argparse.ArgumentParser(description='Modbus client')
	parser.add_argument('ip',  default='localhost', help='IP adress of modbus server')
	args = parser.parse_args()
	
	client = ModbusTcpClient(args.ip)

	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	for i in range(0, 3):
		GPIO.setup(LED_Pins[i], GPIO.OUT)
	
	try:
		while True:
			result = client.read_coils(10, 3)
			print 'R:', result.bits[0], 'G:', result.bits[1], 'B:', result.bits[2]
			for i in range(0, 3):
				GPIO.output(LED_Pins[i], result.bits[i])
			time.sleep(update_interval)
	except KeyboardInterrupt:
		print 'Stopping program'
	except Exception:
		traceback.print_exc(file=sys.stdout)	
	GPIO.cleanup()
	client.close()
	print 'Done'
	sys.exit(0)
