import datetime
import operator
import sys  
import signal 
import os
import time
import threading 
from threading import Timer
from subprocess import call

#sys.path.append("../../../tests")
#from gpiotest import gpio_Interface # works only for beagle bone 

sys.path.append('../../../common')
from p2p_framework import P2P_Interface 

sys.path.append('../../includes')
import machine_queue
from machine_queue import queueElement
import timeTest
from timeTest import myTime

class MachineScheduler():

	def __init__(self,trnsportTime,addHandler,sendMessage,shutdown):
		self.sendMessageFunc = sendMessage 
		self.addHandlerFunc = addHandler
		self.shutdown = shutdown 
		self.__scheduleFail = False
		self.__newTask = {}
		self.__taskDic={}
		print "current time :",  datetime.datetime.now()
		#self.__gpioInterface = gpio_Interface()
		#self.__gpioInterface.clearpins()# works only for beagle bone 
		self.__transportationTime = trnsportTime # works only for beagle bone 
		signal.signal(signal.SIGINT,self.kill_signal_handler)
		print "pid is : ",os.getpid()
	
	def kill_signal_handler(self,signal,frame):
		self.shutdown = False
		#self.__gpioInterface.clearpins()
		print "you pressed ctrl+c !!"
		call(["kill","-9",str(os.getpid())])
		

# function to keep track of the time to start the next task 
	def tasksHandler(self): # cannot make it private because it is called outside the class in addhandler
		while not self.shutdown[0]:
			currentTime = self.getCurrentTimeInSeconds()
			for key,value in self.__taskDic.iteritems():
				if(value._StartTime <= currentTime and value._Status =='Scheduled'):
					# should hier tell the machine which program to run 
					value._Status ='Running'
					print "current time :",  datetime.datetime.now()
					print "value._ProcessingTime :", value._ProcessingTime/60
					print "task started ",value._Name
					print "contract number: ", value._ContractNumber
					#self.__gpioInterface.outputval(value._ContractNumber) # works only for beagle bone 
					t=Timer(value._ProcessingTime,self.timeout,[value._Name]) # argument has to passed as an array 
					t.start() 
					print "Timer started"		
			time.sleep(30)

	def timeout(self,name):
		print "task finished ......"
		#self.__gpioInterface.clearpins() # works only for beagle bone 
		msg={}
		msg['sendername']= name
		self.removeTask(msg)

	def __del__(self):
		print "machine destructor......"
	
	def print_elements_queue(self):
		print "|\tTask name\t|\tStart Time\t|\tFinish Time\t|\tProcessing Time\t|\tDeadline\t|\tStatus"
		print "|\t---------\t|\t----------\t|\t-----------\t|\t---------\t|\t------\t\t|\t-------"
		for key,value in self.__taskDic.iteritems():
			print("|\t%s\t|\t%d:%d\t\t|\t%d:%d\t\t|\t%d:%d\t\t|\t%d:%d\t\t|\t%s\t\t"%(key,value._StartTime/3600,(value._StartTime%3600)/60,value._WorstCaseFinishingTime/3600,(value._WorstCaseFinishingTime%3600)/60,value._ProcessingRmainingTime/3600,(value._ProcessingRmainingTime%3600)/60,value._EndTime/3600,(value._EndTime%3600)/60,value._Status))


	# create new task object and add it to the the task queue of the machine
	def __addNewTask(self):
		tempdic = {}
		key = self.__newTask.keys()
		minimumStartTime = 0
		print key[0]
		tempdic[key[0]] = self.__newTask[key[0]]
		self.__taskDic[key[0]] = queueElement(tempdic[key[0]]['priority'],tempdic[key[0]]['endTime'],tempdic[key[0]]['processingTime'],key[0],tempdic[key[0]]['ContractNumber'],minimumStartTime)
		print "task added to self.__dic :",self.__taskDic
		self.__newTask.clear()
		tempdic.clear()
		return True

####################################################
	#handler to cancel task scheduling and remove it from the task queue of the machine 
	def removeTask(self,msg):
		if msg['sendername'] in self.__taskDic:
			print "Removing..... ",self.__taskDic[msg['sendername']]._Name
			del self.__taskDic[msg['sendername']]
			print "Task removed ......" 
		else:
			print ("%s: you are trying to remove a not existing task"% self.removeTask.__name__)
 
####################################################
	def __converttoseconds(self,strtime):

		temp =timeTest.getendtimestr(strtime)
		#print temp 
		temp = myTime(temp)
		seconds = (temp.hours * 60 + temp.minutes) * 60
		return seconds


######################################################
	def getCurrentTimeInSeconds(self):
		currenttime = datetime.datetime.now()
		currenttimeinseconds = ( currenttime.hour * 60 + currenttime.minute ) * 60
		return currenttimeinseconds

##############################################
	def __scheduleTasks(self):
		print "entered task schedule ......"
		tasksEndTime ={}
		tempRunningTask = object
		currenttimeinseconds = self.getCurrentTimeInSeconds()

		# save running task befor deleting it from task dic   
		for key,value in self.__taskDic.iteritems():
			if value._Status == 'Running':
				tempRunningTask = self.__taskDic[value._Name] 
				print "tempRunningTask: ",tempRunningTask

		#delete the running task from task dic and make its end time as the start time for scheduling
		if hasattr(tempRunningTask,'_Status'):
				del self.__taskDic[tempRunningTask._Name]	
				print ("task %s deleted"% tempRunningTask._Name)

		for key,value in self.__taskDic.iteritems():
			tasksEndTime[key] =value._EndTime 
		# sort the tasks according to their endtime (earliest deadline first) 
		sortdtasks = sorted(tasksEndTime.items(),key=operator.itemgetter(1)) 
		print "sorted tasks according to Ealiest Deadline First " , sortdtasks
		#print "current time in seconds : ",currenttimeinseconds
		firstelement = (sortdtasks[0][0])
		if hasattr(tempRunningTask,'_EndTime'):
			#set running task end time as the start time for first task
			self.__taskDic[firstelement]._TempStartTime = tempRunningTask._WorstCaseFinishingTime + (self.__transportationTime)
			print ("self.__taskDic[firstelement]._TempStartTime  %d:%d "%(self.__taskDic[firstelement]._TempStartTime/3600,(self.__taskDic[firstelement]._TempStartTime%3600)/60))
		else:
			self.__taskDic[firstelement]._TempStartTime = currenttimeinseconds + (self.__transportationTime)
			print ("self.__taskDic[firstelement]._TempStartTime  %d:%d "%(self.__taskDic[firstelement]._TempStartTime/3600,(self.__taskDic[firstelement]._TempStartTime%3600)/60))

		self.__taskDic[firstelement]._TempWorstCaseFinishingTime =  self.__taskDic[firstelement]._TempStartTime + self.__taskDic[firstelement]._ProcessingRmainingTime
		# calculat the worst case finishing time for each task  Priority,EndTime,ProcessingTime,name)
		for i in range(1,len(self.__taskDic)):
			currenttask = self.__taskDic[(sortdtasks[i][0])]
			lasttask = self.__taskDic[(sortdtasks[i-1][0])]
			currenttask._TempStartTime = lasttask._TempWorstCaseFinishingTime + (self.__transportationTime)
			currenttask._TempWorstCaseFinishingTime = currenttask._TempStartTime + currenttask._ProcessingRmainingTime 
			
		# compare worst case finishing time with end time for each task
		for i in range(len(self.__taskDic)):
			if (self.__taskDic[(sortdtasks[i][0])]._TempWorstCaseFinishingTime) < (self.__taskDic[(sortdtasks[i][0])]._EndTime): 
				print (" %s pass guarantee test "% self.__taskDic[(sortdtasks[i][0])]._Name)
			elif(self.__taskDic[(sortdtasks[i][0])]._TempWorstCaseFinishingTime) > (self.__taskDic[(sortdtasks[i][0])]._EndTime): 
				self.__scheduleFail = True
				print (" %s fail in  guarantee test "% self.__taskDic[(sortdtasks[i][0])]._Name)
				return False # 
			# No fails -->> assign the new values of start and end times 
		print "no fails scheduling ......"
		for i in range(len(self.__taskDic)):
			self.__taskDic[(sortdtasks[i][0])]._StartTime = self.__taskDic[(sortdtasks[i][0])]._TempStartTime
			self.__taskDic[(sortdtasks[i][0])]._WorstCaseFinishingTime = self.__taskDic[(sortdtasks[i][0])]._TempWorstCaseFinishingTime
			self.__taskDic[(sortdtasks[i][0])]._Status ='Scheduled' # change status to scheduled

		if hasattr(tempRunningTask,'_Name'):
		# insert back the running task to the task dictionary 
			self.__taskDic[tempRunningTask._Name] = tempRunningTask

		return True

					


		#user defined function 
	def taskArrived(self,message): # cannot make it private because it is called outside the class in addhandler
		taskAdded = False
		tmpmsg = message['data']
		tempint = list(tmpmsg)
		taskNum = int(tempint[0])  # should be passed to the machine while the start time comes 
		priority = int(tempint[1])
		processingTime =int(tempint[2]+tempint[3]+tempint[4]) * 60 # converted to seconds
		if(len(tempint) == 9):
			endTime = int(tempint[5]+tempint[6]+tempint[7]+tempint[8]) # already in seconds
		else:
		  endTime = int(tempint[5]+tempint[6]+tempint[7]+tempint[8]+tempint[9]) # already in seconds
		self.__newTask[message['sendername']]= {'priority':priority,'processingTime':processingTime,'endTime':endTime,'ContractNumber':taskNum}
		#self.__newTask[message['sendername']]['endTime']=self.__converttoseconds(self.__newTask[message['sendername']]['endTime'])
		taskAdded = self.__addNewTask() # create new task object and add it to the the task queue of the machine 
		print "taskAdded: ",taskAdded
		taskScheduled = self.__scheduleTasks() #tasks scheduleability test according to EDF 
		print "taskScheduled: ",taskScheduled
		# test success
		if (taskScheduled):
			response = str(self.__taskDic[message['sendername']]._StartTime) +' '+ str(self.__taskDic[message['sendername']]._WorstCaseFinishingTime)					
			self.sendMessageFunc('TCP', message['sendername'],'', 'SCHEDULED', response)
		#test fails
		if(not taskScheduled):
			del self.__taskDic[message['sendername']]
			response = '00'
			self.sendMessageFunc('TCP', message['sendername'],'', 'SCHEDULEFAIL', response)
		self.print_elements_queue()
		




def main():
	print os.getpid()
	print "main statrted ....."
	shutdown = [False]
	if len(sys.argv) !=3:
		print "error"
		print"Usage : filename.py <router_ip> <send_name>"
		sys.exit()
	router_ip = sys.argv[1]
	name = sys.argv[2]
	trnasportTime = 5 * 60 # in seconds
	Type = "machine"
	print "router ip is : ",router_ip
	myInterface = P2P_Interface(shutdown,name,Type,router_ip)
	myScheduler = MachineScheduler(trnasportTime,myInterface.add_handler,myInterface.sendmessage,shutdown)
	myInterface.display_message_list() 
	myScheduler.addHandlerFunc('ADD', myScheduler.taskArrived)
	myScheduler.addHandlerFunc('CANCEL', myScheduler.removeTask)
	t_handleTasks = threading.Thread( target = myScheduler.tasksHandler)
	t_handleTasks.start()
	while not shutdown[0]:
		# save the user's input in a variable
		input_text = raw_input('>>>')
		#if the user enters 'EXIT', the inifinte while-loop quits and the
		# program can terminate
		if input_text == 'EXIT':
			shutdown[0] = True
			del myInterface
		elif input_text == 'PRINTQUEUE':
			myScheduler.print_elements_queue();


if __name__ == "__main__":
	main()
