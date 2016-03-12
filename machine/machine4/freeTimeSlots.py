from itertools import count 

class FreeTimeSlot:
	slotsNumber = 0 
	def __init__(self):
		self.__Duration = 0
		self.__StartTime = 0
		self.__EndTime = 0
		self.__PreviousTask =''
		self.__NextTask = '' 
		FreeTimeSlot.slotsNumber += 1

	def setDuration(self,duration):
		self.__Duration = duration

	def getDuration(self):
		return self.__Duration

	def setStartTime(self,startTime):
		self.__StartTime = startTime

	def getStartTime(self):
		return self.__StartTime

	def setEndTime(self,endTime):
		self.__EndTime = endTime

	def getEndTime(self):
		return self.__EndTime 

	def setNextTask(self,task):
		self.__NextTask = task

	def getNextTask(self):
		return self.__NextTask

	def setPreviousTask(self,task):
		self.__PreviousTask = task
	
	def getPreviousTask(self):
		return self.__PreviousTask
