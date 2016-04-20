# This class for the machines (milling chine,Lathe, ....) , but not for assembly station


#--------------------------------- general includes ----------------------------------#
import datetime
import operator 
import signal 
import os
import sys
import time
import threading 
from threading import Timer
from subprocess import call
import xml.etree.ElementTree as ET
import copy

from Tkinter import *

#-------------------------------- project includes ------------------------------------#
sys.path.append('../includes')
import machine_queue
from machine_queue import queueElement
import timeTest
from timeTest import myTime
#sys.path.append("../../../tests")
#from gpiotest import gpio_Interface # works only for beagle bone 


class MachineScheduler():

	def __init__(self,trnsportTime,addHandler,sendMessage,shutdown,machine_gui_name):
		self.sendMessageFunc = sendMessage 
		self.addHandlerFunc = addHandler
		self.shutdown = shutdown 
		self.__machine_gui_name = machine_gui_name
		self.__backup_file = 0
		self.__backup_file_lock = threading.Lock()
		self.__scheduleFail = False
		self.__newTask = {}
		self.__taskDic={}
		self.__create_row_gui = False
		self.__gui_rows_counter = 0 
		self.__new_task_name = ''
		self.__task_to_delete = ''
		print "current time :"+ str(datetime.datetime.now())+"\n" 
		#self.__gpioInterface = gpio_Interface()
		#self.__gpioInterface.clearpins()# works only for beagle bone 
		self.__transportationTime = trnsportTime # works only for beagle bone 
		signal.signal(signal.SIGINT,self.kill_signal_handler)
	
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
			time.sleep(5)

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
			print "update backup called "
			self.__backup_file_lock.acquire()
			self.__backup_file = ET.parse('backup_machine.xml')	
			root = self.__backup_file.getroot()	
			currentTime = root.find('current_time')
			currentTime.text = str(self.getCurrentTimeInSeconds()) 
			queue = root.find('machine_queue')
			for element in self.__taskDic:
				temp_element = queue.find(element)
				temp_Status = temp_element.find('Status')
				temp_Status.text = str(self.__taskDic[element]._Status)
				if self.__taskDic[element]._Status == 'Running':
					self.__taskDic[element]._ProcessingRmainingTime = self.__taskDic[element]._WorstCaseFinishingTime - self.getCurrentTimeInSeconds()
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

			self.__backup_file.write('backup_machine.xml')
			self.__backup_file_lock.release()
			time.sleep(30)
 
	
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
	 
	def __removeTask(self,msg):
		if msg['sendername'] in self.__taskDic:
			print "Removing..... ",self.__taskDic[msg['sendername']]._Name
			#acquire lock before using xml file 
			self.__backup_file_lock.acquire()
			# remove task from the Backup file 
			self.__backup_file = ET.parse('backup_machine.xml')	
			root = self.__backup_file.getroot()	
			queue = root.find('machine_queue')
			temp_task = queue.find(msg['sendername'])
			queue.remove(temp_task)
			self.__backup_file.write('backup_machine.xml')
			self.__backup_file_lock.release()

			# set the name to remove the task from the GUI 
			self.__task_to_delete = msg['sendername']

			# remove task from tasks dictionary
			del self.__taskDic[msg['sendername']]
			print "Task removed ......" 
		else:
			print ("%s: you are trying to remove a non existing task"% self.__removeTask.__name__)

#############################################################
#handler to cancel task scheduling and remove it from the task queue of the machine
	def cancelRequest(self,msg):
		print "I got cancel request from: ",msg['sendername']
		self.__removeTask(msg)
 
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
			t=Timer(6,self.__check_confirmation,[message['sendername']]) # argument has to passed as an array 
			t.start()
			print "Confirmation Timer started" 
			# add new entry to xml backup file 
			self.__backup_file = ET.parse('backup_machine.xml')	
			root = self.__backup_file.getroot()	
			queue = root.find('machine_queue')
			task_element = ET.SubElement(queue,message['sendername'])
			ET.SubElement(task_element,'EndTime')
			ET.SubElement(task_element,'Priority')
			ET.SubElement(task_element,'ProcessingTime')
			ET.SubElement(task_element,'ProcessingRmainingTime') 
			ET.SubElement(task_element,'Status')
			self.__backup_file.write('backup_machine.xml')

			# set this flag to true to create new row in the gui 
			self.__create_row_gui = True
			self.__new_task_name = message['sendername']

		#test fails
		if(not taskScheduled):
			del self.__taskDic[message['sendername']]
			response = '00'
			self.sendMessageFunc('TCP', message['sendername'],'', 'SCHEDULEFAIL', response)
		self.print_elements_queue()
		

	# after time our of check timer , check for getting confirmation from shuttle 
	def __check_confirmation(self,name):
		if name in self.__taskDic:
			if self.__taskDic[name]._confirm:
				print("I got confirmation from %s "%name)
			else:
				print("I didn't got confirmation from %s "%name)
				msg = {'sendername':name}
				self.__removeTask(msg)
		else:
			print("%s: error task is not in task dic "%self.__check_confirmation.__name__)

	def confirmation_received(self,msg):
		if msg['sendername'] in self.__taskDic:
			print("%s from %s "%(self.confirmation_received.__name__,msg['sendername']))
			self.__taskDic[msg['sendername']]._confirm = True

		else:
			print("%s: error ,sender name is not in task_dic"%self.confirmation_received.__name__)




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
		machine_name.set(self.__machine_gui_name)
		machine_name_label.pack(side=LEFT)

		Aktuelle_Zeit = StringVar()
		
		Aktuelle_Zeit_label = Label( machine_name_frame, textvariable=Aktuelle_Zeit, relief=RAISED,height = 5 ,width = 40 )
		Aktuelle_Zeit.set("Zeit")
		Aktuelle_Zeit_label.pack(side=LEFT)
		
		rows_dict={}
		status_label_bgcolor = {}
		status_dic ={}

		# callback function for GUI destry event 
		def gui_close():
			self.shutdown[0] = True 
			root.destroy()
			sys.exit()
		root.protocol("WM_DELETE_WINDOW",gui_close)

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
					temp_start_time = str(task_dic[self.__new_task_name]._StartTime /3600)+':'+str((task_dic[self.__new_task_name]._StartTime%3600)/60)
					temp_end_time = str(task_dic[self.__new_task_name]._WorstCaseFinishingTime/3600)+':'+str((task_dic[self.__new_task_name]._WorstCaseFinishingTime%3600)/60)
					label2 = Label( row, textvariable=Zeit, relief=RAISED,height = 5 ,width = 40 )
					Zeit.set(temp_start_time + ' - ' + temp_end_time)
					label2.pack(side=LEFT)
	
					Status = StringVar()
					label2 = Label( row, textvariable=Status,bg = "yellow", relief=RAISED,height = 5 ,width = 40 )
					Status.set(task_dic[self.__new_task_name]._Status)
					label2.pack(side=LEFT)
	   					
					status_dic[self.__new_task_name]= Status
					status_label_bgcolor[self.__new_task_name] = label2
					rows_dict[self.__new_task_name]= row
					print rows_dict	
				# check if a task removed from taskDic, to dele it also from GUI 	
				if(self.__task_to_delete != ''):
						rows_dict[self.__task_to_delete].pack_forget()
						rows_dict[self.__task_to_delete].destroy()
						del status_dic[self.__task_to_delete]
						del status_label_bgcolor[self.__task_to_delete]	
						del rows_dict[self.__task_to_delete]
						self.__task_to_delete = ''
				for st in status_dic:
					print " staus name: ",st
					print status_dic
					status_dic[st].set(self.__taskDic[st]._Status) 
					if(self.__taskDic[st]._Status == "Running"):
						status_label_bgcolor[self.__taskDic[st]._Name].configure(bg = 'green')
						print "status bg color of ",self.__taskDic[st]._Name
				Aktuelle_Zeit.set( datetime.datetime.now())
				root.update_idletasks()
				print task_dic
				root.after(500,update)
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
		label2 = Label( header,textvariable=Zeit, relief=RAISED,height = 5 ,width = 40 )
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
