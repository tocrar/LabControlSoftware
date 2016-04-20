#--------------------------------- general includes ----------------------------------#
from xml.dom.minidom import parse
import xml.dom.minidom
import sys
import os
import time

#-------------------------------- project includes ------------------------------------#
sys.path.append('../common')
from p2p_framework import P2P_Interface
from shuttle import Shuttle



def main():

	try:
#------------------------------------ INITIALIZATIONS ----------------------------------# 
		
		print "main statrted ....."
		print "Process ID : ",os.getpid()
		shutdown = [False]
		# data retreived from config.xml file 
		DOMTree = xml.dom.minidom.parse("../config.xml")
		config = DOMTree.documentElement
		# general configs 
		common_configs = config.getElementsByTagName("common_configs")[0]
		router_ip = common_configs.getElementsByTagName("router_ip")[0]
		router_ip = str(router_ip.childNodes[0].data)

		transportTime = common_configs.getElementsByTagName("transport_time")[0] 
		transportTime = int(transportTime.childNodes[0].data) * 60 # convert to seconds
	
		# configs specefic for shuttles
		shuttle_configs = config.getElementsByTagName("shuttle_configs")[0]
		Type =  shuttle_configs.getElementsByTagName("type")[0]
		Type = str(Type.childNodes[0].data)
		name = shuttle_configs.getElementsByTagName("name")[0]
		name = str(name.childNodes[0].data)
		print "Configuration data:"
		print "\t router_ip: ",	router_ip
		print "\t transport Time: ",transportTime							
		print "\t name: ",	name						 
		print "\t type: "	,Type
		
		# data should be retreived from database 
		print "getting data from database ...."
		Priority=2
		Machines_dic ={'machine_1':{'Name':'machine_1','ProcessingTime':'002'}}#,\
									#'machine_2':{'Name':'machine_2','ProcessingTime':'004'}}
									
		machine4 = {'Name':'machine_4','ProcessingTime':'001'}
		myInterface = P2P_Interface(shutdown,name,Type,router_ip)
		machines = {}
		#print "Machines_dic : " , Machines_dic
		print "Got data from the database !!"
		
		print ("please enter the expected End Time in the form <02:30>")
		EndTime = raw_input('>>>')
		 
		myShuttle = Shuttle(shutdown,Priority,EndTime,Machines_dic,machine4,myInterface.add_handler,myInterface.sendmessage,myInterface.get_address_book,transportTime)
		myShuttle.addHandlerFunc('PRINT', myShuttle.print_message)
		myShuttle.addHandlerFunc('SCHEDULED',myShuttle.get_EDF_response)
		myShuttle.addHandlerFunc('SCHEDULEFAIL',myShuttle.schedule_fail)
		myShuttle.addHandlerFunc('SCHEDULEDM4',myShuttle.get_machine_4_response)
		myShuttle.addHandlerFunc('SCHEDULEFAILM4',myShuttle.schedule_fail)

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
	

			elif input_text.startswith('CANCEL'):
				machineslist = myShuttle.get_required_machines_list()
				for machine in machineslist:
					myShuttle.sendMessageFunc('TCP',machine,'','CANCEL','hello')
					myShuttle.sendMessageFunc('TCP',machine4['Name'],'','CANCEL','hello')
			elif input_text.startswith('TIME'):
				print "current time: ",datetime.datetime.now()

			elif input_text.startswith('TARGET'):
				myShuttle.get_target_list()

	except :
		print ("Error happened in the main function")
		sys.exit()

	



if __name__ == "__main__":
	main()