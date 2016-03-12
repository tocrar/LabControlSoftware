import Adafruit_BBIO.GPIO as GPIO
import time

class gpio_Interface:

	def __init__(self):
		self.__PinList =["P8_8","P8_10","P8_12"]
		for i in range(len( self.__PinList)):
			GPIO.setup(self.__PinList[i],GPIO.OUT)			
	

	def __del__(self):
		GPIO.cleanup()

	def outputval(self,val):
		if (val > 7):
			print "value should be < or = 7"
			return False 

		binarynum = bin(val)
		print "binary: ",binarynum
		binval = binarynum[2:]
		print binval
		print type(binval)
		for i in range(len(binval)):
			if(binval[-1-i] == '1'):  # list statrs from left to right but binary number starts from right to left 
				print ("pin %s : 1"% i)
				GPIO.output(self.__PinList[i],GPIO.HIGH)
			else:
				print ("pin %s : 0"% i)
				GPIO.output(self.__PinList[i],GPIO.LOW)

		return True 			


def main():

	mygpioInterface = gpio_Interface()
	mygpioInterface.outputval(7)
	while True:
		input_text = raw_input('>>>')
#		mygpioInterface.outputval(7)
				
if __name__ == "__main__":
	main()


