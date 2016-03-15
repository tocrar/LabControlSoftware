from freeTimeSlots import FreeTimeSlot

import datetime
import operator
import sys  
import signal 
import os
import time
import threading 
from threading import Timer
from subprocess import call 

#sys.path.append("../../tests")
#from gpiotest import gpio_Interface # works only for beagle bone 


sys.path.append('../../common')
from p2p_framework import P2P_Interface 

sys.path.append('../includes')
import machine_queue
from machine_queue import queueElement
import timeTest
from timeTest import myTime

class Machine():


	def __init__(self,trnsportTime,addHandler,sendMessage,shutdown):
		self.sendMessageFunc = sendMessage 
		self.addHandlerFunc = addHandler
		self.shutdown = shutdown
		print "current time :",  datetime.datetime.now()
		self.__scheduleFail = False
		self.__scheduleSuccess = False
		self.__freeTimeSlots = 0 
		#self.__gpioInterface = gpio_Interface()# works only for beagle bone 
		#self.__gpioInterface.clearpins()# works only for beagle bone 
		self.__transportationTime = trnsportTime 
		self.__newTask = {}
		self.__taskDic={}
		self.__FreeSlots=[]
		self.__lastArrivingTask = ""
		self.__transportationTime = trnsportTime
		signal.signal(signal.SIGINT,self.kill_signal_handler)
		print "pid is : ",os.getpid()
	
	def kill_signal_handler(self,signal,frame):
		#self.__gpioInterface.clearpins()
		print "you pressed ctrl+c !!"
		call(["kill","-9",str(os.getpid())])
		
# function to keep track of the time to start the next task 
	def tasksHandler(self):
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
					t=Timer(value._ProcessingTime,self.timeout,[value._Name]) # argument has to be passed as an array 
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



####################################################
	#handler to cancel task scheduling and remove it from the task queue of the machine 
	def removeTask(self,msg):
		if msg['sendername'] in self.__taskDic:
			print "Removing..... ",self.__taskDic[msg['sendername']]._Name
			del self.__taskDic[msg['sendername']]
			print "Task removed ......" 
		else:
			print ("%s: you are trying to remove a non existing task"% self.removeTask.__name__)

####################################################
	def __converttoseconds(self,strtime):

		temp =timeTest.getendtimestr(strtime)
		temp = myTime(temp)
		seconds = (temp.hours * 60 + temp.minutes) * 60
		return seconds

######################################################
	def getCurrentTimeInSeconds(self):
		currenttime = datetime.datetime.now()
		currenttimeinseconds = ( currenttime.hour * 60 + currenttime.minute ) * 60
		return currenttimeinseconds


							

		#user defined function 
	def taskArrived(self,message): # cannot make it private because it is called outside the class in addhandler
		tmpmsg = message['data']
		#print message['data']
		#print message['sendername']
		tempint = list(tmpmsg)
		taskNum = int(tempint[0])
		print "task number: ", taskNum 
		priority = int(tempint[1])
		processingTime =int(tempint[2]+tempint[3]+tempint[4]) * 60 # converted to seconds
		endTime = tempint[5]+tempint[6]+tempint[7]+tempint[8]
		minStartTime = tempint[9]+tempint[10]+tempint[11]
		print "minStartTime: " , minStartTime
		minStartTime = int(minStartTime) * 60 + self.getCurrentTimeInSeconds()
		#print "minStartTime: " , minStartTime
		#print "End time: ",self.__converttoseconds(endTime)
		#print "self.getCurrentTimeInSeconds(): ",self.getCurrentTimeInSeconds()
		if(self.__converttoseconds(endTime) < self.getCurrentTimeInSeconds()): # should be < tasksDic[name]._MinStartTime
			print "end time less than current time ......"
			return False

		self.__newTask[message['sendername']]= {'priority':priority,'processingTime':processingTime,'endTime':endTime,'ContractNumber':taskNum,'minStartTime':minStartTime}
		self.__newTask[message['sendername']]['endTime']=self.__converttoseconds(self.__newTask[message['sendername']]['endTime'])
		self.__addNewTask() # create new task object and add it to the the task queue of the machine 
		self.__scheduleSuccess = self.__scheduleTasks(message['sendername'])
		print "self.__scheduleSuccess: ", self.__scheduleSuccess
		if (self.__scheduleSuccess):
			#print("schedule for %s done,start time: %f, End Time: %f"%(self.__taskDic[message['sendername']]._Name,self.__taskDic[message['sendername']]._StartTime/3600.0,self.__taskDic[message['sendername']]._WorstCaseFinishingTime/3600.0))
			response = str(self.__taskDic[message['sendername']]._StartTime) +' '+ str(self.__taskDic[message['sendername']]._WorstCaseFinishingTime)	
			print "ContractNumber: ",(self.__taskDic[message['sendername']]._ContractNumber)		
			#print response
			self.sendMessageFunc('TCP', message['sendername'],'', 'SCHEDULEDM4', response)

		if(not self.__scheduleSuccess):
			del self.__taskDic[message['sendername']]
			response = '00'
			self.sendMessageFunc('TCP', message['sendername'],'', 'SCHEDULEFAILM4', response)
		self.__scheduleFail = False
		print "End of task arrived ................."
		self.print_elements_queue()
		print "=====================================================================================================================\n"
		self.printSlots()
		return True
		

	# create new task object and add it to the the task queue of the machine
	def __addNewTask(self):
		tempdic = {}
		key = self.__newTask.keys()
		self.__lastArrivingTask = key[0]
		print key[0]
		tempdic[key[0]] =  self.__newTask[key[0]]
		self.__taskDic[key[0]] = queueElement(tempdic[key[0]]['priority'],tempdic[key[0]]['endTime'],tempdic[key[0]]['processingTime'],key[0],tempdic[key[0]]['ContractNumber'],tempdic[key[0]]['minStartTime'])
		print "task added to self.__dic :",self.__taskDic
		self.__newTask.clear()
		tempdic.clear() 
		return True 


	def __scheduleTasks(self,name):
			tasksEndTime ={}
			currenttimeinseconds = self.getCurrentTimeInSeconds()		
			for key,value in self.__taskDic.iteritems():
				tasksEndTime[key] =value._EndTime
			del tasksEndTime[name]  # delete the new task from the list 
			# sort the tasks according to their endtime (earliest deadline first) 
			sortdtasks = sorted(tasksEndTime.items(),key=operator.itemgetter(1)) 

			if not sortdtasks: # list is empty ,schedule the first element(task_dic contain only one element)
				self.__taskDic[name]._WorstCaseFinishingTime = self.__taskDic[name]._EndTime
				self.__taskDic[name]._StartTime = self.__taskDic[name]._EndTime - self.__taskDic[name]._ProcessingTime
				self.__taskDic[name]._DeadlineForRelatedTasks = self.__taskDic[name]._EndTime - self.__taskDic[name]._ProcessingTime - self.__transportationTime
				self.__taskDic[name]._Status ="Scheduled"
				print("First task satrt time: %d:%d ,endTime: %d:%d ,related tasks deadline: %d:%d"%(self.__taskDic[name]._StartTime/3600.0,(self.__taskDic[name]._StartTime%3600)/60,self.__taskDic[name]._EndTime/3600.0,(self.__taskDic[name]._EndTime%3600)/60,self.__taskDic[name]._DeadlineForRelatedTasks/3600.0,(self.__taskDic[name]._DeadlineForRelatedTasks%3600)/60))
				return True

			print "sorted tasks according to Ealiest Deadline First " , sortdtasks

			if sortdtasks:  # if the list is not empty 
				print "the biggest deadline is ..",sortdtasks[-1] # 
				
				if(self.__taskDic[name]._EndTime > self.__taskDic[sortdtasks[-1][0]]._EndTime): #compare the new task deadline with the biggest one in the list 								     
					print "yes greater ya prince ........."
					
					if ((self.__taskDic[sortdtasks[-1][0]]._EndTime + self.__taskDic[name]._ProcessingTime + self.__transportationTime) < self.__taskDic[name]._EndTime): # (case 1)
						print "yes it's possible to assign a direct time slot after the last task  "
						self.__taskDic[name]._WorstCaseFinishingTime = self.__taskDic[name]._EndTime
						self.__taskDic[name]._StartTime = self.__taskDic[name]._EndTime - self.__taskDic[name]._ProcessingTime
						self.__taskDic[name]._DeadlineForRelatedTasks = self.__taskDic[name]._EndTime - self.__taskDic[name]._ProcessingTime - self.__transportationTime
						self.__taskDic[name]._Status ="Scheduled"
						print("task satrt time: %d:%d ,endTime: %d:%d ,related tasks deadline: %d:%d"%(self.__taskDic[name]._StartTime/3600.0,(self.__taskDic[name]._StartTime%3600)/60,self.__taskDic[name]._EndTime/3600.0,(self.__taskDic[name]._EndTime%3600)/60,self.__taskDic[name]._DeadlineForRelatedTasks/3600.0,(self.__taskDic[name]._DeadlineForRelatedTasks%3600)/60))
						return True 
						
					else: # tasks overlap (the task has a greater dead line but overlaps with the last task )(case 4)
						print "deadline greater but it's not possible to assign a direct time slot after the last task  \n"
						self.__freeSlots = self.getFreeTimeSlots()
						for i in range(len(self.__FreeSlots)):
							if(self.__FreeSlots[i].getDuration() >= (self.__taskDic[name]._ProcessingTime+self.__transportationTime)):
								print "the time slot is suitable for the task \n"
								self.__taskDic[name]._Status ="Scheduled" 													
							 	self.__taskDic[name]._WorstCaseFinishingTime = self.__taskDic[self.__FreeSlots[i].getNextTask()]._StartTime - self.__transportationTime
								self.__taskDic[name]._StartTime = self.__taskDic[name]._WorstCaseFinishingTime - self.__taskDic[name]._ProcessingTime
								self.__taskDic[name]._DeadlineForRelatedTasks = self.__taskDic[name]._StartTime - self.__transportationTime
								print("time slot num %d is suitalbe for the task "%(i))
								return True
							else:
								print("time slot num %d is not suitalbe for the task "%(i))		
							
				else: #  check for free time slots and see if it is possible to assign a free slot to the task 
					print "the deadline is not the greatest........."
					self.__freeSlots = self.getFreeTimeSlots()
					print "come back from getFreeTimeSlots\n"
					for i in range(len(self.__FreeSlots)):
						print "entered for loop"
						print "self.__taskDic[name]._MinStartTime: ",self.__taskDic[name]._MinStartTime
						condition_1 = self.__FreeSlots[i].getDuration() >= (self.__taskDic[name]._ProcessingTime+self.__transportationTime)
						condition_2 = self.__FreeSlots[i].getEndTime() -(self.__taskDic[name]._ProcessingTime+self.__transportationTime) > self.__taskDic[name]._MinStartTime
						if(condition_1 and condition_2):   
							print "the time slot is suitable for the task "
							tempFinishTime = self.__taskDic[self.__FreeSlots[i].getNextTask()]._StartTime - self.__transportationTime
							if (tempFinishTime <self.__taskDic[name]._EndTime):
								self.__taskDic[name]._WorstCaseFinishingTime = tempFinishTime
								self.__taskDic[name]._StartTime = self.__taskDic[name]._WorstCaseFinishingTime - self.__taskDic[name]._ProcessingTime
								self.__taskDic[name]._DeadlineForRelatedTasks = self.__taskDic[name]._StartTime - self.__transportationTime
								self.__taskDic[name]._Status ="Scheduled" 
								print("time slot num %d is suitalbe for the task "%(i))
								return True
							else : 
								self.__taskDic[name]._WorstCaseFinishingTime = self.__taskDic[name]._EndTime
								# need to handle if there is no pervious tasks 
								if((self.__FreeSlots[i].getPreviousTask() == '') and (self.__taskDic[name]._WorstCaseFinishingTime - self.__taskDic[name]._MinStartTime) >= (self.__taskDic[name]._ProcessingTime+self.__transportationTime)): # no previous tasks 
									self.__taskDic[name]._StartTime = self.__taskDic[name]._WorstCaseFinishingTime - self.__taskDic[name]._ProcessingTime
									self.__taskDic[name]._DeadlineForRelatedTasks = self.__taskDic[name]._StartTime - self.__transportationTime
									self.__taskDic[name]._Status ="Scheduled" 
									print("time slot num %d is suitalbe for the task "%(i))
									return True

								elif((self.__taskDic[name]._WorstCaseFinishingTime - self.__taskDic[self.__FreeSlots[i].getPreviousTask()]._EndTime) >= (self.__taskDic[name]._ProcessingTime+self.__transportationTime)):
									self.__taskDic[name]._StartTime = self.__taskDic[name]._WorstCaseFinishingTime - self.__taskDic[name]._ProcessingTime
									self.__taskDic[name]._DeadlineForRelatedTasks = self.__taskDic[name]._StartTime - self.__transportationTime
									self.__taskDic[name]._Status ="Scheduled" 
									print("time slot num %d is suitalbe for the task "%(i))
									return True
								else:
									print("time slot num %d is not suitalbe for the task form inner if condition  "%(i))
									break 
								

						else:
							print("time slot num %d is not suitalbe for the task "%(i))


##################################################
	 
	def getFreeTimeSlots(self):
		timeSlotsList =[]
		tasksEndTime ={}
		sortedtasks =[]
		
				
		for key,value in self.__taskDic.iteritems():
			tasksEndTime[key] =value._WorstCaseFinishingTime

		sortedtasks = sorted(tasksEndTime.items(),key=operator.itemgetter(1)) 
		if self.__lastArrivingTask and not (max(tasksEndTime.iteritems(),key=operator.itemgetter(1))[0] == self.__taskDic[self.__lastArrivingTask]._EndTime):
				del tasksEndTime[self.__lastArrivingTask]  # delete the new task from the list 
				print "the new task is not the biggest one , it will be deleted form sortedtasks"
				self.__lastArrivingTask = ''
				sortedtasks = sorted(tasksEndTime.items(),key=operator.itemgetter(1)) 
				print "sortedtasks: ",sortedtasks

		for i in range(len(sortedtasks)):
			tempEnd = self.__taskDic[sortedtasks[-i-1][0]]._StartTime
			timeSlotsList.append(FreeTimeSlot())
			timeSlotsList[i].setEndTime(tempEnd)
			timeSlotsList[i].setNextTask(self.__taskDic[sortedtasks[-i-1][0]]._Name)	
	
		for i in range(0,len(sortedtasks)-1):
			tempStart = self.__taskDic[sortedtasks[-i-2][0]]._WorstCaseFinishingTime
			timeSlotsList[i].setStartTime(tempStart)
			timeSlotsList[i].setPreviousTask( self.__taskDic[sortedtasks[-i-2][0]]._Name)
		if sortedtasks:
			timeSlotsList[len(sortedtasks)-1].setStartTime(self.getCurrentTimeInSeconds()) #start time for the last time slot = currenttime 
	
		for i in range(len(sortedtasks)):
			tempDuration = timeSlotsList[i].getEndTime() - timeSlotsList[i].getStartTime()
			timeSlotsList[i].setDuration(tempDuration)
	
		for i in range(len(sortedtasks)):
			print("previous task: %s , slot number: %d , next task: %s"%(timeSlotsList[i].getPreviousTask(),i,timeSlotsList[i].getNextTask()))
				
			
		self.__FreeSlots = timeSlotsList	
		return timeSlotsList	

#############################################
	def __updateFreeSlots(self):
		timeSlotsList =[]
		tasksEndTime ={}
		orderedtasks =[]
		
				
		for key,value in self.__taskDic.iteritems():
			tasksEndTime[key] =value._WorstCaseFinishingTime

		orderedtasks = sorted(tasksEndTime.items(),key=operator.itemgetter(1)) 
		for i in range(len(orderedtasks)):
			tempEnd = self.__taskDic[orderedtasks[-i-1][0]]._StartTime
			timeSlotsList.append(FreeTimeSlot())
			timeSlotsList[i].setEndTime(tempEnd)
			timeSlotsList[i].setNextTask(self.__taskDic[orderedtasks[-i-1][0]]._Name)	
	
		for i in range(0,len(orderedtasks)-1):
			tempStart = self.__taskDic[orderedtasks[-i-2][0]]._WorstCaseFinishingTime
			timeSlotsList[i].setStartTime(tempStart)
			timeSlotsList[i].setPreviousTask( self.__taskDic[orderedtasks[-i-2][0]]._Name)
		if orderedtasks:
			timeSlotsList[len(orderedtasks)-1].setStartTime(self.getCurrentTimeInSeconds()) #start time for the last time slot = currenttime 
	
		for i in range(len(orderedtasks)):
			tempDuration = timeSlotsList[i].getEndTime() - timeSlotsList[i].getStartTime()
			timeSlotsList[i].setDuration(tempDuration)
				
			
		self.__FreeSlots = timeSlotsList	
		return timeSlotsList	

############################3################

	def printSlots(self):
		print "|\tSlot num.\t|\tstart Time\t|\tDuration\t|\tEnd Time"
		print "|\t---------\t|\t----------\t|\t---------\t|\t---------"
		self.__FreeSlots = self.__updateFreeSlots()
		for i in range(len(self.__FreeSlots)):
			tempStart = self.__FreeSlots[i].getStartTime()
			tempDuration = self.__FreeSlots[i].getDuration()
			tempEnd  = self.__FreeSlots[i].getEndTime()
			print("|\t%d\t\t|\t%d:%d\t\t|\t%d:%d\t\t|\t%d:%d\t\t"%(i,tempStart/3600,(tempStart%3600)/60,tempDuration/3600,(tempDuration%3600)/60,tempEnd/3600,(tempEnd%3600)/60))

##############################################



def main():

	try:
		print os.getpid()
		print "main statrted ....."
		shutdown = [False]
		if len(sys.argv) !=3:
			print "error"
			print"Usage : filename.py <router_ip> <send_name>"
			sys.exit()
		router_ip = sys.argv[1]
		name = sys.argv[2]
		trnasTime = 5 * 60 # in seconds 
		Type = "machine"
		print "router ip is : ",router_ip
		myInterface = P2P_Interface(shutdown,name,Type,router_ip)
		myScheduler = Machine(trnasTime,myInterface.add_handler,myInterface.sendmessage,shutdown)
	 	myInterface.display_message_list() 
		status = myScheduler.addHandlerFunc('ADD', myScheduler.taskArrived)
		print "status from main", status
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
			elif input_text == 'PRINTFREESLOTS':
				myScheduler.printSlots()
			elif input_text =='SIKO':
				koko = myClass(myInterface.add_handler,myInterface.sendmessage)
			elif input_text.startswith('TIME'):
				print "current time: ",datetime.datetime.now()
	except KeyboardInterrupt:
		shutdown = [True]
		sys.exit()


if __name__ == "__main__":
	main()
