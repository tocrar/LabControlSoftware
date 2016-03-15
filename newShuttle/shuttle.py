
import sys
import signal 
import os
from subprocess import call
import datetime
from threading import Timer

sys.path.append('../common')
import machine_task
from p2p_framework import P2P_Interface

 

# user defined method to print the address book
def print_address_book( address_book ):
	
	print '###############################################################'
	print 'Address book:  (name : type)'
	print '---------------------------------------------------------------'
	for address in address_book:
		print address[0], ':', address[1]
	print '###############################################################'



class Shuttle:

	def __init__(self,shutdown,Priority,EndTime,MachinesList,addHandler,sendMessage,transportTime):
		print "initializing shuttle ........"
		print "current time :",  datetime.datetime.now()
		self.shutdown = shutdown
		self.sendMessageFunc = sendMessage 
		self.addHandlerFunc = addHandler
		self.__TransportTime = transportTime
		self.__got_machine_4_response = False
		self.Type = "shuttle"
		signal.signal(signal.SIGINT,self.kill_signal_handler)
		print "pid is : ",os.getpid()
		print ("please enter the contract Priority" )
		self.Priority = raw_input('>>>')
		self.Priority = int(self.Priority)

		print ("please enter the contract Number" )
		self.ContractNumber = raw_input('>>>')
		self.ContractNumber = int(self.ContractNumber)
		
		print ("please enter the expected End Time in the form <02:30>")
		self.EndTime = raw_input('>>>')
		self.EndTime = self.EndTime.split(":")
		print "end time :", self.EndTime
		self.EndTime = (''.join(self.EndTime))
		print "end time :", self.EndTime , type(self.EndTime)
		print "length of end time : ",len(self.EndTime)
		signal.signal(signal.SIGINT,self.kill_signal_handler)
		self.__machines ={}
		# getting tasks information 
		print "Enter tasks information "
		print ("please enter the list of machines in the order in which the workpiece should be proccesd as in address book ")
		input_text = raw_input('>>>')
		print input_text
		MachinesList = input_text.split(",")
		print "MachinesList : " , MachinesList
		for task in MachinesList:	
			print ("please enter processing time for machine %s in the form of minutes <020>:"% task)
			RequiredProcessingTime = raw_input('>>>')
			RequiredProcessingTime = RequiredProcessingTime

			#print RequiredProcessingTime ,type(RequiredProcessingTime)
			self.__machines[task] = machine_task.TaskForMachine(task,RequiredProcessingTime,self.Priority)
		print "initializing shuttle done "


	def kill_signal_handler(self,signal,frame):
		print "you pressed ctrl+c !!"
		call(["kill","-9",str(os.getpid())])



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
			if machine != 'machine_4':
				tempSuccess = tempSuccess and self.__machines[machine]._ScheduleSuccess
		print"temp Success: ",tempSuccess
		if tempSuccess:
			print "success for all machines , I should send confimation message"
		else:
			print "schedule fails by one of the machines , I should send cancel request"
		
	def get_machine_4_response(self,message):
		if(message['sendername'] == 'machine_4'):
			timeList = message['data'].split()
			tempStartTime = int(timeList[0])
			tempFinishTime = int(timeList[1])
			print('I got my time slot on machine_4 from %d:%d ,to %d:%d'%(tempStartTime/3600,(tempStartTime%3600)/60,tempFinishTime/3600,(tempFinishTime%3600)/60))
			self.__got_machine_4_response = True
			t=Timer(20,self.__check_ScheduleSuccess_123) # check to send confirmation message for the machines with the time slots 
			t.start() 
			self.__machines['machine_4']._StartTime = tempStartTime
			self.__machines['machine_4']._EndTime  = tempFinishTime
			self.__machines['machine_4']._DeadLine = tempFinishTime
			for machine in self.__machines:
				if machine != 'machine_4':
					self.__machines[machine]._DeadLine = tempStartTime - self.__TransportTime
					print('%s deadline is  %d:%d'%(machine,self.__machines[machine]._DeadLine/3600,(self.__machines[machine]._DeadLine%3600)/60))
			self.send_machine_1_2_3_request()
		else:
			print("%s: the sender has sent 'SCHEDULEDM4' but the sender is not machine_4")

	def send_machine_1_2_3_request(self):
		for machine in self.__machines:
			if machine != 'machine_4':
				msg = str(self.ContractNumber)+str(self.Priority)+str(self.get_machine_processing_time(machine))+str(self.__machines[machine]._DeadLine)
				print("msg , %s: "% self.send_machine_1_2_3_request.__name__)
				print msg
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


	
def main():

	try:
		print "main statrted ....."
		shutdown = [False]
		if len(sys.argv) !=3:
			print "error"
			print"Usage : filename.py <router_ip> <send_name>"
			sys.exit()
		router_ip = sys.argv[1]
		name = sys.argv[2]
		#ContractNumber= 1
		Priority=2
		EndTime= 1230
		shutdown = [False]
		Type = "shuttle"
		transportTime = 5 * 60 # in seconds 
		MachinesList =4
		print "router ip is : ",router_ip
		myInterface = P2P_Interface(shutdown,name,Type,router_ip)
		 
		myShuttle = Shuttle(shutdown,Priority,EndTime,MachinesList,myInterface.add_handler,myInterface.sendmessage,transportTime)
		myShuttle.addHandlerFunc('PRINT', myShuttle.print_message)
		myShuttle.addHandlerFunc('SCHEDULED',myShuttle.get_EDF_response)
		myShuttle.addHandlerFunc('SCHEDULEFAIL',myShuttle.schedule_fail)
		myShuttle.addHandlerFunc('SCHEDULEDM4',myShuttle.get_machine_4_response)
		myShuttle.addHandlerFunc('SCHEDULEFAILM4',myShuttle.schedule_fail)
		if(myShuttle.has_machine('machine_4')):
			print "machin_4 min start time :",myShuttle.get_machine_4_min_start_time()
			msg =  str(myShuttle.ContractNumber)+str(myShuttle.Priority)+str(myShuttle.get_machine_processing_time('machine_4'))+str(myShuttle.EndTime)+myShuttle.get_machine_4_min_start_time()
			print "message: ", msg
			myShuttle.sendMessageFunc('TCP','machine_4','','ADD', msg)
		# messages ={}
		# for k in myShuttle.machines:
		# 	print myShuttle.machines[k]
		# 	messages[k] = str(myShuttle.ContractNumber) + str(myShuttle.Priority)+ str(myShuttle.machines[k].GetRequiredProcessingTime())+ str(myShuttle.EndTime)
		# print "messages : ",messages
		# address_book =myInterface.get_address_book()
		# print "address book :" ,address_book[1][0]
		# for element in enumerate(address_book):
		# 	print"element is: ",element[1][0]
		# 	if "mach" in  element[1][0]:
		# 		print "found a machine..." , element
		# 		print "message of messages[ address_book[1][0]] :",messages[element[1][0]]
		# 		# send the message using the 'sendmessage()' method of the p2p object
		# 		myShuttle.sendMessageFunc('TCP', element[1][0],'','ADD', messages[element[1][0]])




		# use a infinite loop for the user prompting 
		while not shutdown[0]:
	
			# save the users input in a variable
			input_text = raw_input('>>>')
	
			# if the user enters 'EXIT', the inifinte while-loop quits and the
			# program can terminate
			if input_text == 'EXIT':
				shutdown[0] = True
		
			# if the user enters 'ADDR', the address book will be printed in the
			# console
			elif input_text == 'ADDR':
				address_book = myInterface.get_address_book()
				print_address_book(address_book)
	
			# the user can send message to other clients by entering:
			# SEND <receiver name> <message data>
			# e.g.: SEND Bob Hi Bob, how are you?
			elif input_text.startswith('SEND'):
				tmp = input_text.partition(' ')
				tmp = tmp[2].partition(' ')
				recvname = tmp[0]
				data = tmp[2]
		
				# send the message using the 'sendmessage()' method of the p2p object
				myShuttle.sendMessageFunc('TCP', recvname,'','ADD', data)

			elif input_text.startswith('CANCEL'):
				machineslist = myShuttle.get_required_machines_list()
				for machine in machineslist:
					myShuttle.sendMessageFunc('TCP',machine,'','CANCEL','hello')

			elif input_text.startswith('TIME'):
				print "current time: ",datetime.datetime.now()

	except KeyboardInterrupt:
		sys.exit()

	



if __name__ == "__main__":
	main()
