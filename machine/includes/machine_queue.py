
class queueElement:
	def __init__(self,Priority,EndTime,ProcessingTime,name,ContractNum,minStarTime):
		print "machine queue consructor......."
		self._Name = name
		self._ProcessingTime = ProcessingTime
		self._EndTime = EndTime
		self._DeadlineForRelatedTasks = 0
		self._Priority = Priority
		self._ElapsedTime = 0
		self._processingStatus = False	# not done
		self._ProcessingRmainingTime = ProcessingTime
		self._StartTime = 0
		self._MinStartTime = minStarTime
		self._TempStartTime = 0
		self._WorstCaseFinishingTime = EndTime
		self._TempWorstCaseFinishingTime = 0
		self._ContractNumber = ContractNum
		self._confirm = False
		self._gui_row_number = 0 # gui row number reated to this task 
		self._Status ='Unscheduled' #  ('Running,Scheduled','Unscheduled','Stopped')
		#print ("new task created with -->> Required processing time  : %s , priority: %s , procssing status : %s , processing left time : %s"  %(self._ProcessingTime ,  self._Priority ,self._processingStatus,self._ProcessingRmainingTime))
		print "machine queue init done ..... "

	def __del__(self):
		print "machine queue destructor ......."


	def GetRequiredProcessingTime(self):
		return self._ProcessingTime

	def GetProcessingStatus(self):
		return self._processingStatus

	def SetProcessingStatus(self,status):
		self._processingStatus = status

	def GetProcessingLeftTime(self):
		return self._ProcessingRemainingTime

	def SetProcessingLeftTime(self,leftTime):
		self._ProcessingRemainingTime = leftTime

