#--------------------------------- general includes ----------------------------------#
from xml.dom.minidom import parse
import xml.dom.minidom
import sys
import os
import time
import threading 
import time
import datetime

#-------------------------------- project includes ------------------------------------#
sys.path.append('../common')

from p2p_framework import P2P_Interface
from mysql_class import sqldb
from shuttle import Shuttle

def getCurrentTimeInSeconds(self):
        currenttime = datetime.datetime.now()
        currenttimeinseconds = ( currenttime.hour * 60 + currenttime.minute ) * 60
        return currenttimeinseconds

# thread to track shuttle status (busy or free) and to get data from database
 
def shuttle_status(shutdown,Interface,transportTime):
	status_busy = False
	shuttle_container = []
	while not shutdown[0]:
               print "check shuttle status ......."
	       if not status_busy :
			status_busy = True
			# data should be retreived from database
			print "getting data from database ...."
        		host = "192.168.1.54"
        		user = "Shuttle"
        		passwd = "raspberry"
                        db = "ip"
                        mydb = sqldb(host,user,passwd,db)  
                        # a request should be snt to the cmd to get  KA_Nummer
                        KA_Nummer = 1000022 # I will get this number from the cmd 
                        sql = "SELECT * FROM kundenauftrag WHERE KA_Nummer = %s " % (KA_Nummer)
                        data = mydb.sqlquery(sql)
                        contractNumber = data["rows"][0]["KA_Nummer"]
                        print"KA_Nummer : " , contractNumber
                        print "Auftrag Priority", data["rows"][0]["KA_Prio"]
                        # get arbeitsplan    
                        #process_vorgeange = [data["rows"][0]["UB"],data["rows"][0]["MO"],data["rows"][0]["LA"],data["rows"][0]["EV"],data["rows"][0]["RF"],data["rows"][0]["CH"]]
                        process_vorgeange = [data["rows"][0]["RF"],data["rows"][0]["CH"]]
                        
                        for vorgang in process_vorgeange:
                                 sql = "SELECT * FROM arbeitsplan WHERE arbeitsplan.ID = %s " % (vorgang)
                                 plan = mydb.sqlquery(sql)
                                 print ("Vorgang % d : .... %s" % (vorgang,plan)) 
                                 
                        Priority=2
                        Machines_dic ={'machine_1':{'Name':'machine_1','ProcessingTime':'002'}}
                        machine4 = {'Name':'machine_4','ProcessingTime':'001'} # mantagestation 
                        machines = {}
                        print "Machines_dic : " , Machines_dic
                        EndTime = "15:30" 
                        print " expected End Time >> ",EndTime
                        print "Got data from the database !!"
                        #myShuttle = Shuttle(shutdown,Priority,EndTime,Machines_dic,machine4,Interface.add_handler,Interface.sendmessage,Interface.get_address_book,transportTime,contractNumber)
                        # I am passing 2 to contract number (contract number should be in the range [0 - 9])
                        myShuttle = Shuttle(shutdown,Priority,EndTime,Machines_dic,machine4,Interface.add_handler,Interface.sendmessage,Interface.get_address_book,transportTime,2)
                        myShuttle.addHandlerFunc('PRINT', myShuttle.print_message)
                        
                        myShuttle.addHandlerFunc('SCHEDULED',myShuttle.get_EDF_response)
                        myShuttle.addHandlerFunc('SCHEDULEFAIL',myShuttle.schedule_fail)
                        myShuttle.addHandlerFunc('SCHEDULEDM4',myShuttle.get_machine_4_response)
                        myShuttle.addHandlerFunc('SCHEDULEFAILM4',myShuttle.schedule_fail)
               time.sleep(10)
               myShuttle.getStatus()
               print myShuttle
               #del myShuttle
               #print myShuttle
               
             


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
		

		#Priority=2
		#Machines_dic ={'machine_1':{'Name':'machine_1','ProcessingTime':'002'}}#,\
									#'machine_2':{'Name':'machine_2','ProcessingTime':'004'}}
									
		#machine4 = {'Name':'machine_4','ProcessingTime':'001'}
		myInterface = P2P_Interface(shutdown,name,Type,router_ip)
		#machines = {}
		##print "Machines_dic : " , Machines_dic
		#print "Got data from the database !!"
		
		#print ("please enter the expected End Time in the form <02:30>")
		#EndTime = raw_input('>>>')
		 
		#myShuttle = Shuttle(shutdown,Priority,EndTime,Machines_dic,machine4,myInterface.add_handler,myInterface.sendmessage,myInterface.get_address_book,transportTime)
		#myShuttle.addHandlerFunc('PRINT', myShuttle.print_message)
		#myShuttle.addHandlerFunc('SCHEDULED',myShuttle.get_EDF_response)
		#myShuttle.addHandlerFunc('SCHEDULEFAIL',myShuttle.schedule_fail)
		#myShuttle.addHandlerFunc('SCHEDULEDM4',myShuttle.get_machine_4_response)
		#myShuttle.addHandlerFunc('SCHEDULEFAILM4',myShuttle.schedule_fail)

		#start shuttle status thread   , shuttle_status(shutdown,Interface,transportTime)
		t_shuttle_status = threading.Thread(target = shuttle_status,args=(shutdown,myInterface,transportTime,))
		t_shuttle_status.start()

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
