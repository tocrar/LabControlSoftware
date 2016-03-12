
class TaskForMachine:
	""""
 Class for tasks for individual machines 

"""


	def __init__(self,MachineNumber,RequiredProcessingTime,Priority):
	
		print ("initializing machine %s task statrted ........"% MachineNumber)
		self._MachineNumber= MachineNumber
		self._RequiredProcessingTime= RequiredProcessingTime
		self._Priority = Priority
		self._processingStatus = False	# not done
		self._ProcessingLeftTime = RequiredProcessingTime
		self._StartTime = 0
		self._EndTime = 0
		self._DeadLine = 0 
		#self._ContractNumber = ContractNumber
		print ("Required processing time  : %s , priority: %s , procssing status : %s , processing left time : %s"  %(self._RequiredProcessingTime ,  self._Priority ,self._processingStatus,self._ProcessingLeftTime))
		print "initializing machine task done ........"


	def GetMachineNumber(self):
		return self._MachineNumber

	def GetRequiredProcessingTime(self):
		return self._RequiredProcessingTime

	def GetProcessingStatus(self):
		return self._processingStatus

	def SetProcessingStatus(self,status):
		self._processingStatus = status

	def GetProcessingLeftTime(self):
		return self._ProcessingLeftTime

	def SetProcessingLeftTime(self,leftTime):
		self._ProcessingLeftTime = leftTime


