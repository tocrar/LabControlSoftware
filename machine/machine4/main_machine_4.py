#--------------------------------- general includes ----------------------------------#
import os
import sys
import threading
import xml.etree.ElementTree as ET



#-------------------------------- project includes ------------------------------------#
from machine_4 import Machine
sys.path.append('../../common')
from p2p_framework import P2P_Interface 



def main():

	try:
		#------------------------------------ INITIALIZATIONS ----------------------------------# 
		print "main statrted ....."
		print "process ID: ", os.getpid()
		shutdown = [False]
		
		# Open XML document using minidom parser
		# getting Configuration data from config.xml file 
		configs_file = ET.parse("../../config.xml")	
		configs = configs_file.getroot()
		# general configs
		common_configs = configs.find('common_configs')
		router_ip = common_configs.find('router_ip').text
		trnasportTime = int(common_configs.find('transport_time').text) * 60 # in seconds
		# machine specific configs 
		machine_configs = configs.find('machine_configs')
		name = machine_configs.find('name').text
		Type = machine_configs.find('type').text
		print "Configuration data:"
		print "\t router_ip: ",	router_ip
		print "\t transport Time: ",trnasportTime							
		print "\t name: ",	name						 
		print "\t type: "	,Type

		myInterface = P2P_Interface(shutdown,name,Type,router_ip)
		myScheduler = Machine(trnasportTime,myInterface.add_handler,myInterface.sendmessage,shutdown)
	 	#adding hanlder to the requests 
		myScheduler.addHandlerFunc('ADD', myScheduler.taskArrived)
		myScheduler.addHandlerFunc('CANCEL', myScheduler.cancelRequest)

		#thread to keep track of the time to start the next task 
		t_handleTasks = threading.Thread( target = myScheduler.tasksHandler)
		t_handleTasks.start()

		#start update backup data thread 
		t_updateData = threading.Thread(target = myScheduler.update_backup_data)
		t_updateData.start()

		#------------------------------------ END OF INITIALIZATIONS ----------------------------------#

		#-------------------------------------- START THE MAIN LOOP  --------------------------------# 
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
			elif input_text.startswith('TIME'):
				print "current time: ",datetime.datetime.now()
	except KeyboardInterrupt:
		shutdown = [True]
		sys.exit()


if __name__ == "__main__":
	main()
