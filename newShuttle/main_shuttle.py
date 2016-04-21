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
#--------------------------------------------------------------------------------------#
#---------------------------------------- global variables ----------------------------#

global_shuttle_container = []
# lock the shuttle container list  in order not to access it at the same time form different threads 
shuttle_container_lock = threading.Lock()

#--------------------------------------------------------------------------------------#

def getCurrentTimeInSeconds(self):
        currenttime = datetime.datetime.now()
        currenttimeinseconds = ( currenttime.hour * 60 + currenttime.minute ) * 60
        return currenttimeinseconds

# thread to track shuttle status (busy or free) and to get data from database
 
def shuttle_status(shutdown,interface,transportTime):
	status_busy = False
	got_job_status = False
	shuttle_created = False
	global global_shuttle_container
	Interface = interface
	# initialization data for the database
        host = "192.168.1.54"
        user = "Shuttle"
        passwd = "raspberry"
        db = "ip"
        mydb = sqldb(host,user,passwd,db) 
			
        def get_job_from_db(message):
        	print "got response from commander \n"
        	if message['data'] != "Error":
			try:
				print "getting data from database server ....\n"   		
				KA_Nummer = message['data']
				#KA_Nummer = 1000022 # I will get this number from the cmd 
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
		                	print ("Vorgang % d : .... %s\n" % (vorgang,plan))
		                print "Got data from the database !!\n"
		                got_job_status = True
			except:
			    #currentJob = 0
			    got_job_status = False 
			    errormsg = KA_Nummer+" reset"
			    p2p.sendmessage('TCP', "cmd", "Raspberry", "Error", errormsg)
			    print "db Connection Error"
        	else:
			time.sleep(10)
			got_job_status = False 
			
	Interface.add_handler("newJob", get_job_from_db)
	Interface.add_handler("retry", get_job_from_db)
	
	myShuttle = 0
			
	while not shutdown[0]:
               time.sleep(10)
	       if not status_busy :
			# I have to check if the commander in address book or not 
			print "sending request to the cmd ..!!\n"
			Interface.sendmessage('TCP', "cmd", "Raspberry", "getJob", "0")
			
                        # a request should be sent to the cmd to get  KA_Nummer 
                                 
                        Priority=2
                        Machines_dic ={'machine_1':{'Name':'machine_1','ProcessingTime':'002'}}
                        machine4 = {'Name':'machine_4','ProcessingTime':'001'} # montagestation 
                        machines = {}
                       # print "Machines_dic : " , Machines_dic
                        EndTime = "15:30" 
                        #print " expected End Time >> ",EndTime
                        # I am passing 2 to contract number (contract number should be in the range [0 - 9])
                        myShuttle = Shuttle(shutdown,Priority,EndTime,Machines_dic,machine4,Interface.add_handler,Interface.sendmessage,Interface.get_address_book,transportTime,2)
                        print "myShuttle: "+str(myShuttle)+"\n"
                        if myShuttle:
		                myShuttle.addHandlerFunc('PRINT', myShuttle.print_message)
		                
		                myShuttle.addHandlerFunc('SCHEDULED',myShuttle.get_EDF_response)
		                myShuttle.addHandlerFunc('SCHEDULEFAIL',myShuttle.schedule_fail)
		                myShuttle.addHandlerFunc('SCHEDULEDM4',myShuttle.get_machine_4_response)
		                myShuttle.addHandlerFunc('SCHEDULEFAILM4',myShuttle.schedule_fail)
		                shuttle_container_lock.acquire()
		                global_shuttle_container.append(myShuttle)
		                shuttle_container_lock.release()
		               # print "shuttle container: " ,global_shuttle_container
		               # print "shuttle added to the container ...!! "
		                status_busy = True
               print" --------------------------------------------------------------"
               if(myShuttle.getStatus()):
                       print "the  current Contract finished .....\n"
                       print "deleting the current shuttle object \n"
                       shuttle_container_lock.acquire()
                       del global_shuttle_container[0]
                       shuttle_container_lock.release()
                       del myShuttle
                       print " getting new Contract from database \n"
                       status_busy = False 
              
               print "shuttle container: " ,global_shuttle_container
             


def main():

	try:
#------------------------------------ INITIALIZATIONS ----------------------------------# 
		global global_shuttle_container 	
					
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
		
		myInterface = P2P_Interface(shutdown,name,Type,router_ip)

		#start shuttle status thread  (to track the status of the shuttle [busy or free])_
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
				global_shuttle_container[0].get_target_list()

	except :
		print ("Error happened in the main function")
		sys.exit()

	



if __name__ == "__main__":
	main()
