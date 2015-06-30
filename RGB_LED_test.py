import sys, traceback
import time
import RPi.GPIO as GPIO

pins = {'r' : 18, 'g': 23, 'b' : 24}
state = 0

if __name__ == "__main__":
	
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	
	GPIO.setup(pins['r'], GPIO.OUT)
	GPIO.setup(pins['g'], GPIO.OUT)
	GPIO.setup(pins['b'], GPIO.OUT)
	
	try:
		while True:
			r = state%2;
			g = (state>>1)%2
			b = (state>>2)%2
			print r, g, b
			GPIO.output(pins['r'], r)
			GPIO.output(pins['g'], g)
			GPIO.output(pins['b'], b)
			
			if state is 8:
				state = 0
			else:
				state += 1
			time.sleep(0.5)
	except KeyboardInterrupt:
		print "Exiting"
	except Exception:
		traceback.print_exc(file=sys.stdout)
		
	GPIO.cleanup()
	print "Done"
	sys.exit(0)