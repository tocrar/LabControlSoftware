#--------------------------------- general includes ----------------------------------#
import signal 
import os
from subprocess import call
import datetime
from threading import Timer
import operator
import datetime
import sys 

#-------------------------------- project includes ------------------------------------#
import machine_task


# user defined method to print the address book
def print_address_book( address_book ):
	
	print '###############################################################'
	print 'Address book:  (name : type)'
	print '---------------------------------------------------------------'
	for address in address_book:
		print address[0], ':', address[1]
	print '###############################################################'



class Shuttle:

	def __init__(self,shutdown,Priority,EndTime,MachinesDic,machine4,addHandler,sendMessage,address_book,transportTime,contractNumber):
		try:
			print "initializing shuttle ........"
			print "current time :",  datetime.datetime.now()
			self.shutdown = shutdown
			self.sendMessageFunc = sendMessage 
			self.addHandlerFunc = addHandler
			self.__getAddressBookFunc = address_book   # list is given as a list of tuples (name, type): [['Alice', 'shuttle'],['Bob', 'machine']
			self.__TransportTime = transportTime
			self.__got_machine_4_response = False
			self.Type = "shuttle"
			#signal.signal(signal.SIGINT,self.kill_signal_handler) # signals works only in main thread 
			self.Priority = Priority
			self.ContractNumber = contractNumber
			self.EndTime = EndTime
			self.EndTime = self.EndTime.split(":")
			self.EndTime = (''.join(self.EndTime))
			#signal.signal(signal.SIGINT,self.kill_signal_handler)
			self.__machines ={}
			# getting tasks information 
			self.__machine_4 = machine_task.TaskForMachine(machine4['Name'],machine4['ProcessingTime'],self.Priority)
			for task in MachinesDic:
				print "task : ",task 
				self.__machines[task] = machine_task.TaskForMachine(MachinesDic[task]['Name'],MachinesDic[task]['ProcessingTime'],self.Priority)
			print "initializing shuttle done "
			# check for the correct format of the input data 
			if (self.ContractNumber > 9 or type(self.ContractNumber) != int):
				print "Error : contract number should be in the range [0 - 9]"
				self.shutdown[0] = True
				sys.exit()

			if (self.Priority > 9 or type(self.Priority) != int): 
				print "Error : priority should be in the range [0 - 9]"
				self.shutdown[0] = True 
				sys.exit()
			# check if machine 4 in address book befor sending it a message  
			address_book = self.__getAddressBookFunc()
			print "address book : ",address_book
			#msg =  str(self.ContractNumber)+str(self.Priority)+str(machine4['ProcessingTime'])+str(self.EndTime)+self.get_machine_4_min_start_time()
			#self.sendMessageFunc('TCP',machine4['Name'],'','ADD', msg)
		except:
			print "ERROR whlie initializing shuttle.......  !!!"
			return 

	def kill_signal_handler(self,signal,frame):
		print "you pressed ctrl+c !!"
		call(["kill","-9",str(os.getpid())])


	def getCurrentTimeInSeconds(self):
		currenttime = datetime.datetime.now()
		currenttimeinseconds = ( currenttime.hour * 60 + currenttime.minute ) * 60
		return currenttimeinseconds
                
        def getStatus(self):
                temp_finished = True
                for machine in self.__machines:
                      print machine
                      temp_finished =  temp_finished and self.__machines[machine]._Status_Finished
                print"getStatus temp_finished Success: ",temp_finished
                print "montage station status ",self.__machine_4._Status_Finished
                temp_finished =  temp_finished and self.__machine_4._Status_Finished
                print " status for all ",temp_finished
                if temp_finished:
                        return True
                else:
                        return False 
               
                         
                                          


	def schedule_fail(self,message):
		if message['sendername'] in self.__machines:
			self.__machines[message['sendername']]._ScheduleSuccess = False
			print("schedule on %s fail "%(message['sendername']))
		else:
			print("%s: this sender is not in my machine tasks"% self.schedule_fail.__name__)

	def has_machine(self,machine_name):
		if type(machine_name) != type('text') :
			print ("Error in Function(%s): false data type given" % (self.has_machine.__name__))
			return False
		if machine_name in self.__machines:
			return True
		else:
			return False

	def get_required_machines_list(self):
		machineslist = []
		for machine in self.__machines:
			machineslist.append(machine)
		return machineslist

	def get_machine_processing_time(self,machine_name):
		if type(machine_name) != type('text') :
			print ("Error in Function(%s): false data type given"% self.get_machine_processing_time.__name__ )
			return False
		if machine_name in self.__machines:
			return self.__machines[machine_name].GetRequiredProcessingTime()
		else:
			print ("Error in Function(%s): machine doesn't exist in my dictionary" % (self.get_machine_processing_time.__name__))
			return False	
		
	def got_machine_4_response(self):
		return self.__got_machine_4_response 

	def get_machine_4_min_start_time(self):
		tempTime = 0
		for machine in self.__machines:
			if machine != 'machine_4':
				tempTime = tempTime +  int(self.__machines[machine]._RequiredProcessingTime)  
		temStr = str(tempTime)
		dif = 3 - len(temStr)
		temZero = ''
		for i in range(dif):
			temZero  = temZero + str(0)
		temStr = temZero + temStr 
		print "temStr: ", temStr
		return temStr

	def __check_ScheduleSuccess_123(self):
		print self.__check_ScheduleSuccess_123.__name__
		tempSuccess = True
		for machine in self.__machines:
			if machine != self.__machine_4._Name:
				tempSuccess = tempSuccess and self.__machines[machine]._ScheduleSuccess
		print"temp Success: ",tempSuccess
		if tempSuccess and self.__check_pickup_time():
			print "success for all machines , and pickup time ,sending confirmation.........."
			msg = 'confirm'
			for machine in self.__machines:
				self.sendMessageFunc('TCP',machine,'','CONFIRM', msg)
		else:
			print "schedule fails by one of the machines ,or pickup time ,sending cancel request........"
			msg = 'cancel'
			for machine in self.__machines:
				self.sendMessageFunc('TCP',machine,'','CANCEL', msg)
	# still need to handle check pickup time 	
	def __check_pickup_time(self):
		tasksEndTime ={}
		for key,value in self.__machines.iteritems():
			tasksEndTime[key] =value._EndTime 
		sortdtasks = sorted(tasksEndTime.items(),key=operator.itemgetter(1))
		print "sorted tasks: ",sortdtasks
		for i in range(len(sortdtasks)-1):
			if self.__machines[sortdtasks[i][0]]._EndTime + self.__TransportTime <= self.__machines[sortdtasks[i+1][0]]._EndTime :
				print "yes greater for i: ",i
				check = True
			else:
				check = False
				return check
		return True

	def get_machine_4_response(self,message):
		if(message['sendername'] == self.__machine_4._Name):
			timeList = message['data'].split()
			tempStartTime = int(timeList[0])
			tempFinishTime = int(timeList[1])
			print('I got my time slot on machine_4 from %d:%d ,to %d:%d'%(tempStartTime/3600,(tempStartTime%3600)/60,tempFinishTime/3600,(tempFinishTime%3600)/60))
			self.__got_machine_4_response = True
			t=Timer(4,self.__check_ScheduleSuccess_123) # check to send confirmation message for the machines with the time slots 
			t.start() 
			self.__machine_4._StartTime = tempStartTime
			self.__machine_4._EndTime  = tempFinishTime
			self.__machine_4._DeadLine = tempFinishTime
			for machine in self.__machines:
				if machine != self.__machine_4._Name:
					self.__machines[machine]._DeadLine = tempStartTime - self.__TransportTime
					#print('%s deadline is  %d:%d'%(machine,self.__machines[machine]._DeadLine/3600,(self.__machines[machine]._DeadLine%3600)/60))
			self.send_machine_1_2_3_request()
		else:
			print("%s: the sender has sent 'SCHEDULEDM4' but the sender is not machine_4")

	def send_machine_1_2_3_request(self):
		# need to check for the machine in address book befor sending messages
		peers = self.__getAddressBookFunc()
		peersList = []
		for i in range(len(peers)):
			peersList.append(peers[i][0])
		# print "address book: ", peersList
		# for agent in peers:
		# 	print"agent : ", agent   
		for machine in self.__machines :
			if machine != self.__machine_4._Name and machine in peersList:
				#print "machine in list ",machine
				msg = str(self.ContractNumber)+str(self.Priority)+str(self.get_machine_processing_time(machine))+str(self.__machines[machine]._DeadLine)
				# print("msg , %s: "% self.send_machine_1_2_3_request.__name__)
				# print msg
				self.sendMessageFunc('TCP',machine,'','ADD', msg)			

	def get_EDF_response(self,message):
		if message['sendername'] in self.__machines:
			timeList = message['data'].split()
			tempStartTime = int(timeList[0])
			tempFinishTime = int(timeList[1])
			self.__machines[message['sendername']]._StartTime = tempStartTime
			self.__machines[message['sendername']]._EndTime = tempFinishTime
			self.__machines[message['sendername']]._ScheduleSuccess = True
			print('I got my time slot on %s from %d:%d ,to %d:%d'%(message['sendername'],tempStartTime/3600,(tempStartTime%3600)/60,tempFinishTime/3600,(tempFinishTime%3600)/60))
		else:
			print("%s: the sender has sent a 'SCHEDULED' but the sender is not in my machine tasks")

# user defined method to print the data of a received message
	def print_message( self,message ):
		print message['sendername'], ':', message['data']
    
	
	# user defined method to print the address book
	def print_address_book( self,address_book ):
		
		print '###############################################################'
		print 'Address book:  (name : type)'
		print '---------------------------------------------------------------'
		for address in address_book:
			print address[0], ':', address[1]
		print '###############################################################'


	# return the next station to go to and the supposed time  
	def get_target_list(self): 
		tasksStartTime ={}
		#put task name , start time in a separate dic. to sort them 
		for key,value in self.__machines.iteritems():
			tasksStartTime[key] =value._StartTime

		sortdtasks = sorted(tasksStartTime.items(),key=operator.itemgetter(1)) 
		print "sorted tasks according to start time  " , sortdtasks
		# it returns an ordered list of tuppled in the form [(sttion_name,start_time)] ------>>  [('machine1',1),('machine2',2),('machine3',3)]
		return sortdtasks 



