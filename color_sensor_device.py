import RPi.GPIO as GPIO
import time
import argparse
import sys, traceback
import smbus
import time

from pymodbus.client.sync import ModbusTcpClient

update_interval = 0.8

if __name__ == "__main__":
	
	print '=== Modbus client ( Color Sensr ) ==='
	parser = argparse.ArgumentParser(description='Modbus client')
	parser.add_argument('ip',  default='localhost', help='IP adress of modbus server')
	args = parser.parse_args()
	
	bus = smbus.SMBus(1)
	# I2C address 0x29
	# Register 0x12 has device ver. 
	# Register addresses must be OR'ed with 0x80
	bus.write_byte(0x29,0x80|0x12)
	ver = bus.read_byte(0x29)
	# version # should be 0x44
	if ver == 0x44:
		print "Device found\n"
		client = ModbusTcpClient(args.ip)
		print "Device connected to server"
		bus.write_byte(0x29, 0x80|0x00) # 0x00 = ENABLE register
		bus.write_byte(0x29, 0x01|0x02) # 0x01 = Power on, 0x02 RGB sensors enabled
		bus.write_byte(0x29, 0x80|0x14) # Reading results start register 14, LSB then MSB
		try:
			while True:
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
		except KeyboardInterrupt:
			print 'Stopping program'
		except Exception:
			traceback.print_exc(file=sys.stdout)
		client.close()
		print 'Done'
	else:
		print 'Device not found'
	# Done
	sys.exit(0)
