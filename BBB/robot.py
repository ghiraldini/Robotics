#!/usr/bin/python

from moves import BotMoves
import time

# ----------------------------------------------------------
#
# ----------------------------------------------------------
def main():

	r = BotMoves()
	time.sleep(1)

	r.cleanUp()
	r.initHR_SC04()
	r.initMotor()
	r.testMotors()

	time.sleep(2)
	
	while r.is_bot_on():	
		r.loop()
	
	r.cleanUp()
	
# ----------------------------------------------------------
#
# ----------------------------------------------------------	
if __name__ == "__main__":
    main()
	
	
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
