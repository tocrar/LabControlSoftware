
#--------------------------------- general includes ----------------------------------#
import datetime
import operator
import sys  
import signal 
import os
import time 
import threading
from threading import Timer
from subprocess import call 
from xml.dom.minidom import parse
import xml.dom.minidom
import xml.etree.ElementTree as ET
from Tkinter import *
import copy

#-------------------------------- project includes ------------------------------------#
#sys.path.append("../../tests")
#from gpiotest import gpio_Interface # works only for beagle bone 
from freeTimeSlots import FreeTimeSlot
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
		self.__create_row_gui = False
		self.__gui_rows_counter = 0
		self.__new_task_name = ''
		self.__backup_file = 0 
		self.__backup_file_lock = threading.Lock()
		print "current time :"+ str(datetime.datetime.now()) + '\n'
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
	
	# handler will be executed when "Ctl+C" will be pressed 
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

	# will be executed when the task finished (could be used to call some output routines to check if the machine already done)
	def timeout(self,name):
		print "task finished ......"
		#self.__gpioInterface.clearpins() # works only for beagle bone
		msg={}
		msg['sendername']= name
		self.__removeTask(msg)

	def __del__(self):
		print "machine destructor......"


	def update_backup_data(self):
		print "update backup thread started ......"
		while not self.shutdown[0]:
			print "update backup called....."

			self.__backup_file_lock.acquire()
			self.__backup_file = ET.parse('backup_machine4.xml')	
			root = self.__backup_file.getroot()	
			currentTime = root.find('current_time')
			currentTime.text = str(self.getCurrentTimeInSeconds()) 
			queue = root.find('machine_queue')
			for element in self.__taskDic:
				temp_element = queue.find(element)
				temp_Status = temp_element.find('Status')
				temp_Status.text = str(self.__taskDic[element]._Status)
				if self.__taskDic[element]._Status == 'Running':
					self.__taskDic[element]._ProcessingRmainingTime = self.__taskDic[element]._EndTime - self.getCurrentTimeInSeconds()
					#print "remaining processing time: ",self.__taskDic[element]._ProcessingRmainingTime

				temp_EndTime = temp_element.find('EndTime')
				temp_EndTime.text = str(self.__taskDic[element]._EndTime)
				temp_Priority = temp_element.find('Priority')
				temp_Priority.text = str(self.__taskDic[element]._Priority)
				temp_ProcessingTime = temp_element.find('ProcessingTime')
				temp_ProcessingTime.text = str(self.__taskDic[element]._ProcessingTime)
				temp_ProcessingRmainingTime = temp_element.find('ProcessingRmainingTime')
				temp_ProcessingRmainingTime.text = str(self.__taskDic[element]._ProcessingRmainingTime)

				#print("%s End time %d:%d saved ...."% (element,self.__taskDic[element]._EndTime/3600,((self.__taskDic[element]._EndTime%3600)/60)))

			self.__backup_file.write('backup_machine4.xml')
			self.__backup_file_lock.release()
			time.sleep(30)
 
	
	#show the shuttles in the machine queue 
	def print_elements_queue(self):
		print "|\tTask name\t|\tStart Time\t|\tFinish Time\t|\tProcessing Time\t|\tDeadline\t|\tStatus"
		print "|\t---------\t|\t----------\t|\t-----------\t|\t---------\t|\t------\t\t|\t-------"
		for key,value in self.__taskDic.iteritems():
			print("|\t%s\t|\t%d:%d\t\t|\t%d:%d\t\t|\t%d:%d\t\t|\t%d:%d\t\t|\t%s\t\t"%(key,value._StartTime/3600,(value._StartTime%3600)/60,value._WorstCaseFinishingTime/3600,(value._WorstCaseFinishingTime%3600)/60,value._ProcessingRmainingTime/3600,(value._ProcessingRmainingTime%3600)/60,value._EndTime/3600,(value._EndTime%3600)/60,value._Status))



####################################################
	#Remove specific shuttle from machine queue
	def __removeTask(self,msg):
		if msg['sendername'] in self.__taskDic:
			print "Removing..... ",self.__taskDic[msg['sendername']]._Name

			#acquire lock before using xml file 
			self.__backup_file_lock.acquire()
			# remove task from the Backup file 
			self.__backup_file = ET.parse('backup_machine4.xml')	
			root = self.__backup_file.getroot()	
			queue = root.find('machine_queue')
			temp_task = queue.find(msg['sendername'])
			queue.remove(temp_task)
			self.__backup_file.write('backup_machine4.xml')
			self.__backup_file_lock.release()
			# remove task from tasks dictionary 
			del self.__taskDic[msg['sendername']]
			print "Task removed ......" 
		else:
			print ("%s: you are trying to remove a not existing task"% self.__removeTask.__name__)


#handler to cancel task scheduling and remove it from the task queue of the machine 
	def cancelRequest(self,msg):
		print "I got cancel request from: ",msg['sendername']
		self.__removeTask(msg)
 

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


							

		#handler for arriving tasks  
	def taskArrived(self,message): # cannot make it private because it is called outside the class in addhandler
		print message
		tmpmsg = message['data']
		tempint = list(tmpmsg)
		taskNum = int(tempint[0])
		print "task number: ", taskNum 
		priority = int(tempint[1])
		processingTime =int(tempint[2]+tempint[3]+tempint[4]) * 60 # converted to seconds
		endTime = tempint[5]+tempint[6]+tempint[7]+tempint[8]
		minStartTime = tempint[9]+tempint[10]+tempint[11]
		print "minStartTime: " , minStartTime
		minStartTime = int(minStartTime) * 60 + self.getCurrentTimeInSeconds()
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
			# add new entry to xml backup file 
			self.__backup_file = ET.parse('backup_machine4.xml')	
			root = self.__backup_file.getroot()	
			queue = root.find('machine_queue')
			task_element = ET.SubElement(queue,message['sendername'])
			ET.SubElement(task_element,'EndTime')
			ET.SubElement(task_element,'Priority')
			ET.SubElement(task_element,'ProcessingTime')
			ET.SubElement(task_element,'ProcessingRmainingTime') 
			ET.SubElement(task_element,'Status')
			self.__backup_file.write('backup_machine4.xml')

			# set this flag to true to create new row in the gui 
			self.__create_row_gui = True
			self.__new_task_name = message['sendername']
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

	# Apply the scheduling algorithm 
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
				print "the largest deadline is ..",sortdtasks[-1] # 
				
				if(self.__taskDic[name]._EndTime > self.__taskDic[sortdtasks[-1][0]]._EndTime): #compare the new task deadline with the biggest one in the list 								     
					print "yes greater than the largest deadline ........."
					
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
					print "the deadline is not the largest........."
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

############################################

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
	def set_create_row_gui_flag(self):
		count = 0 
		while True:
			element = queueElement(2,3456,34,'shuttle_'+str(count),3,2)
			self.__taskDic[element._Name]= element 
			self.__new_task_name = element._Name
			self.__create_row_gui = True 
			print "flag set right ......."
			print "task dict: ",self.__taskDic
			count = count + 1 
			time.sleep(10)

	def gui_funtion(self):
		root = Tk()

		machine_name_frame = Frame(root)
		machine_name_frame.pack(side=TOP, fill=X, padx=1, pady=1)
		machine_name= StringVar()
		machine_name_label = Label( machine_name_frame, textvariable=machine_name,font = 80, relief=RAISED,height = 5 ,width = 20 )
		machine_name.set("FREASEMACHINE")
		machine_name_label.pack(side=LEFT)

		Aktuelle_Zeit = StringVar()
		
		Aktuelle_Zeit_label = Label( machine_name_frame, textvariable=Aktuelle_Zeit, relief=RAISED,height = 5 ,width = 40 )
		Aktuelle_Zeit.set("Zeit")
		Aktuelle_Zeit_label.pack(side=LEFT)

		rows_list = []
		status_dic ={}
		# function responsible for updating the GUI after (1000 msec)
		def outer_update(root,task_dic):
			def update():

				if (self.__create_row_gui): # need to check for the count of rows 
					print "creating new row for: ",self.__taskDic[self.__new_task_name]

					self.__gui_rows_counter = self.__gui_rows_counter + 1 
					print "gui rows counter: " ,self.__gui_rows_counter
					self.__create_row_gui = False 
					row = Frame(root)
					row.pack(side=TOP, fill=X, padx=1, pady=1)

					number = StringVar()
					label1 = Label( row, textvariable=number, relief=RAISED,height = 5 ,width = 20 )
					number.set(self.__gui_rows_counter)
					label1.pack(side=LEFT)

					Auftrag = StringVar()
					label2 = Label( row, textvariable=Auftrag, relief=RAISED,height = 5 ,width = 40 )
					Auftrag.set(task_dic[self.__new_task_name]._ContractNumber)
					label2.pack(side=LEFT)

					Zeit = StringVar()
					label2 = Label( row, textvariable=Zeit, relief=RAISED,height = 5 ,width = 40 )
					Zeit.set(str(task_dic[self.__new_task_name]._StartTime) + ' - ' + str(task_dic[self.__new_task_name]._EndTime))
					label2.pack(side=LEFT)

					Status = StringVar()
					label2 = Label( row, textvariable=Status, relief=RAISED,height = 5 ,width = 40 )
					Status.set(task_dic[self.__new_task_name]._Status)
					label2.pack(side=LEFT)
   					
					status_dic[self.__new_task_name]= Status
					rows_list.append(row)
					print rows_list		
				for st in status_dic:
					print " staus name: ",st
					print status_dic
					status_dic[st].set(self.__taskDic[st]._Status) 
				Aktuelle_Zeit.set( datetime.datetime.now())
				root.update_idletasks()
				print task_dic
				root.after(1000,update)
			update()

	#-----------------------------------  the frame for the header of the table ----------------------------------

		header = Frame(root)
		header.pack(side=TOP, fill=X, padx=1, pady=1)

		number = StringVar()
		label1 = Label( header, textvariable=number, relief=RAISED,height = 5 ,width = 20 )
		number.set("ID")
		label1.pack(side=LEFT)

		Auftrag = StringVar()
		label2 = Label( header, textvariable=Auftrag, relief=RAISED,height = 5 ,width = 40 )
		Auftrag.set("Auftrag")
		label2.pack(side=LEFT)

		Zeit = StringVar()
		label2 = Label( header, textvariable=Zeit, relief=RAISED,height = 5 ,width = 40 )
		Zeit.set("Zeit")
		label2.pack(side=LEFT)

		Status = StringVar()
		label2 = Label( header, textvariable=Status, relief=RAISED,height = 5 ,width = 40 )
		Status.set("Status")
		label2.pack(side=LEFT)
	#----------------------------------- END the frame for the header of the table ----------------------------------
 		dict2 = copy.deepcopy(self.__taskDic)
		outer_update(root,self.__taskDic)
		root.mainloop()
