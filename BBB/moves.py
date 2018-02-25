#!/usr/bin/python

import Adafruit_BBIO.ADC as ADC
import Adafruit_BBIO.GPIO as DIO
import Adafruit_BBIO.PWM as PWM
import time

# Turn on Bot Pins (read)
SWITCH = "P8_11"

# HC-SR04 Ultrasound Sensor pins
TRIG = "P8_13"
ECHO = "P8_14"

# MotoCape Pins
M1 = "P9_15" #(IN_LOW_1)
M2 = "P9_23" #(IN_LOW_2)
M4 = "P9_27" #(IN_LOW_4)
M3 = "P9_12" #(IN_LOW_3)

LMOT_PWM = "P9_14" #EHRPWM1A (PWM_LOWA)
RMOT_PWM = "P9_16" #EHRPWM1B (PWM_LOWB)


# ----------------------------------------------------------
#
# ----------------------------------------------------------
class BotMoves:

	# ----------------------------------------------------------
	# Switch to turn on Bot/SW
	# ----------------------------------------------------------
	def is_bot_on(self):
		if  DIO.input(SWITCH) == 1:
			return True
		else:
			return False

	# ----------------------------------------------------------
	# Main Loop to keep Bot Moving
	# ----------------------------------------------------------
	def loop(self):

		while True:
			while self.getDistance() > 40:
				print("Moving Forward")
				self.goForward( self.getDistance() )
				time.sleep(0.025)
				
			print("Obstacle Detected!!!")
			self.stop()
			time.sleep(1)

			lDist = self.survey("LEFT",1)
			time.sleep(1)

			rDist = self.survey("RIGHT",2)
			time.sleep(1)				

			print("Left Dist: %f Right Dist: %f" % (lDist,rDist))

			if(lDist > rDist):
				print("Going Left to avoid obstacle")
				self.moveLeft()
				time.sleep(1)
				self.goForward( self.getDistance() )
				time.sleep(1)
				self.moveRight()
				time.sleep(1)
				self.goForward( self.getDistance() )
				self.loop()
			else:
				print("Going Right to avoid obstacle")
				self.moveRight()
				time.sleep(1)
				self.goForward( self.getDistance() )
				time.sleep(1)
				self.moveLeft()
				time.sleep(1)
				self.goForward( self.getDistance() )
				self.loop()		
		
		return;

	# ----------------------------------------------------------
	# Init DIO for Sensor
	# ----------------------------------------------------------
	def initHR_SC04(self):
		print "Initializing HR-SC04 sensor..."
		ADC.setup()	
		time.sleep(0.5)
		
		DIO.setup(TRIG, DIO.OUT)
		time.sleep(0.25)
		DIO.setup(ECHO, DIO.IN)
		
		DIO.output(TRIG, DIO.LOW)	

		return;

	# ----------------------------------------------------------
	# Init DIO and PWM for motors
	# ----------------------------------------------------------
	def initMotor(self):
		print "Initializing DG012-SV motors.."
		time.sleep(0.5)

		DIO.setup(M1, DIO.OUT)
		DIO.setup(M2, DIO.OUT)
		DIO.setup(M3, DIO.OUT)
		DIO.setup(M4, DIO.OUT)	
		
		DIO.setup(LMOT_PWM, DIO.OUT)
		DIO.setup(RMOT_PWM, DIO.OUT)
		
		PWM.start(LMOT_PWM,0)
		PWM.start(RMOT_PWM,0)

		return;

		
	# ----------------------------------------------------------
	# Init DIO for Bot Turn ON/OFF switch
	# ----------------------------------------------------------
	def initBotPin(self):
		print "Registering bot switch..."
		time.sleep(0.5)
		
		DIO.setup(SWITCH, DIO.IN)
		return;
		
	# ----------------------------------------------------------
	# Activate Sensor to calculate distance
	# ----------------------------------------------------------
	@staticmethod
	def getDistance(self):
		s = 0
		start = 0
		end = 0
		distAve = 0
		distSum = 0
		i = 1
		count = 4
		timeout = 0.036

		
		while i < count:
			# Send Trigger HIGH for 10us then low and wait for echo
			#print("Sending pulse to Trigger")
			DIO.output(TRIG, DIO.HIGH)
			time.sleep(0.000010)
			DIO.output(TRIG, DIO.LOW)

			s = time.time()
			# Get pulse width by grabbing time at rise edge and falling edge
			while DIO.input(ECHO)==0:
				start = time.time()
				if(start - s >= timeout):
					reset()
					return 0;

			while DIO.input(ECHO)==1:
				end = time.time()

			# pulse width in microseconds
			# 10us seems to be low limit on BBB (~3.3cm)
			# 23ms is max value for HC-SR04 (~400cm)
			duration = end-start
			#print("Pulse Width: %f" % (duration))

			# Calculate distance in cm
			distance = 0.5 * duration * 34300
			#print("Distance %f, interval %f" % (distance,i))
			#print("Distance: %f" % (distance))
			distSum = distSum + distance
			i = i+1
			time.sleep(.0100)
			
			distAve = distSum/3
			#print("Average distance: %f, Distance Sum: %f" % (distAve,distSum))
			
		return distAve;
	#	return distance

	# ----------------------------------------------------------
	# Sample AIN method
	# ----------------------------------------------------------
	@staticmethod
	def getAIN(self):
		start = time.time()
		timer = True
		elapsed = 10
		timeCount = 0

		while timer:
			val = ADC.read("P9_33")
			t = time.time()
			print("Value: %d at\t%f \t%f" % (COUNT,t,val))
			print("READ: %f" % (val))
			time.sleep(0.1)
			timeCount = time.time()-start
			print("Timer: %f" % (timeCount))
			if(timeCount > elapsed):
				timer = False

		return val;


	# ----------------------------------------------------------
	# Turn Bot right/left for X seconds (duration)
	# ----------------------------------------------------------
	@staticmethod
	def survey(self, direction, duration):
		start = time.time()
		timer = True
		elapsed = duration
		timeCount = 0
		MAX = -1000

		if(direction == "RIGHT"):
			moveRight()
		else:
			moveLeft()
		
		while timer:
			d = getDistance()
			if(d > MAX):
				MAX = d
			t = time.time()
			timeCount = time.time()-start
			if(timeCount > elapsed):
				timer = False
				
		stop()
				
		return MAX;

		
	# ----------------------------------------------------------
	#
	# ----------------------------------------------------------
	@staticmethod
	def moveRight(self):
		print("Turning Right")
		# Forward Left Motor		
		PWM.set_duty_cycle(LMOT_PWM,75)
		DIO.output(M1, DIO.HIGH)
		DIO.output(M2, DIO.LOW)
		
		# Reverse Right Motor
		PWM.set_duty_cycle(RMOT_PWM,75)
		DIO.output(M3, DIO.LOW)
		DIO.output(M4, DIO.HIGH)
		return;

		
	# ----------------------------------------------------------
	#
	# ----------------------------------------------------------
	@staticmethod
	def moveLeft(self):
		print("Turning Left")
		# Reverse Left Motor
		PWM.set_duty_cycle(LMOT_PWM,75)
		DIO.output(M1, DIO.LOW)
		DIO.output(M2, DIO.HIGH)	
		
		# Forward Right Motor
		PWM.set_duty_cycle(RMOT_PWM,75)
		DIO.output(M3, DIO.HIGH)
		DIO.output(M4, DIO.LOW)
		return;

	# ----------------------------------------------------------
	#
	# ----------------------------------------------------------
	@staticmethod
	def goForward(self,dist):
		if dist >= 100.0:
			DC = 100
		if (dist < 100.0) & (dist > 50.0):
			DC = 85
		if dist <= 50.0:
			DC = 65
		
		print("Moving Forward, dist: %f ,DC: %f" % (dist,DC))
		# Left Motor FWD
		PWM.set_duty_cycle(LMOT_PWM,DC)
		DIO.output(M1, DIO.HIGH)
		DIO.output(M2, DIO.LOW)
		
		# Right Motor FWD
		PWM.set_duty_cycle(RMOT_PWM,DC)
		DIO.output(M3, DIO.HIGH)
		DIO.output(M4, DIO.LOW)
		
		return;

	# ----------------------------------------------------------
	#
	# ----------------------------------------------------------
	@staticmethod
	def reverse(self):
		print("Moving in Reverse")
		# Left Motor Reverse
		PWM.set_duty_cycle(LMOT_PWM,100)
		DIO.output(M1, DIO.LOW)
		DIO.output(M2, DIO.HIGH)
		
		# Right Motor Reverse
		PWM.set_duty_cycle(RMOT_PWM,100)
		DIO.output(M3, DIO.LOW)
		DIO.output(M4, DIO.HIGH)
		
		return;

		
	# ----------------------------------------------------------
	#
	# ----------------------------------------------------------	
	@staticmethod
	def stop(self):
		print("Stopping")
		PWM.set_duty_cycle(LMOT_PWM,0)
		PWM.set_duty_cycle(RMOT_PWM,0)
		return;
		

	# ----------------------------------------------------------
	#
	# ----------------------------------------------------------
	def cleanUp(self):
		print("Cleaning...")
		PWM.stop(LMOT_PWM)
		PWM.stop(RMOT_PWM)
		
		time.sleep(1)
		
		DIO.cleanup()
		PWM.cleanup()
		
		return;	
		
	# ----------------------------------------------------------
	#
	# ----------------------------------------------------------
	@staticmethod	
	def reset(self):
		self.stop()
		self.cleanUp()
		self.initHR_SC04()
		self.initMotor()
		

	# ----------------------------------------------------------
	#
	# ----------------------------------------------------------
	def testMotors(self):
		print("Testing Motor movements...")
		self.initMotor()
		time.sleep(1)
		self.goForward( 100 )
		time.sleep(2)
		self.stop()
		self.reverse()
		time.sleep(2)
		self.stop()
		self.moveLeft()
		time.sleep(2)
		self.stop()
		self.moveRight()
		time.sleep(2)
		self.stop()
		print("Done...")
		
		self.cleanUp()
		return;
		
# ---------------------------------------------
# Notes:
# ---------------------------------------------
# 	LOOP_COUNT = 10
#	for COUNT in range(1,LOOP_COUNT):
#		<do stuff here>
#
# PWM example
#	Set pin with duty cycle of 50%
# 	PWM.start("P9_14", 50)
#
#	Changing PWM duty cycle
#	PWM.set_duty_cycle("P9_14",25)
#
