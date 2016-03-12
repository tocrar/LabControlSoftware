# This is an example for a program using the p2p_framework.

# import the p2p_framework library
import p2p_framework
import sys
# define global variable to terminate the program

shutdown = [False]
sendname = ""
sendtype = "Switch"
Station = "F3"
router_ip ="" 
#router_ip = '172.16.1.1'
router_connected = False


# create a definition for the shuttle speed
Station = "F3"

# user defined method to print the address book
def print_address_book( address_book ):
	
	print '###############################################################'
	print 'Address book:  (name : type)'
	print '---------------------------------------------------------------'
	for address in address_book:
		print address[0], ':', address[1]
	print '###############################################################'

# user defined method to print the data of a received message
def print_message( message ):
	
	print message['sendername'], ':', message['data']
	
# user defined method to stop the shuttle

def pass_switch(message):

    if message['data'] != "Error":

        Message_Station = message['data']

        if Message_Station == Station:
            print('Einfahrt')
        else:
            print('Durchfahrt')

#user defined function 
def request_message(message):
	print message['sendername'],"sent request number",message['data']
	tmpmsg = message['data']
	print "koko toto",type(tmpmsg)
	tempint = list(tmpmsg)
	print tempint
	contractNum =int(tempint[0])
	priority =int(tempint[1])
	processTime =int(tempint[2]+tempint[3]+tempint[4])
	endTime = int(tempint[5]+tempint[6]+tempint[7]+tempint[8])
	print "cotract number =",contractNum  , " ,priority = ",priority,", processTime =",processTime," ,endTime =",endTime
	print endTime+1
	
	
 
def main():
	global router_ip ,sendname 
	print "router ip is : ",router_ip," sendname ",sendname
	if len(sys.argv) !=3:
		print "error"
		print"Usage : filename.py <router_ip> <send_name>"
		sys.exit()

	router_ip = sys.argv[1]
	sendname = sys.argv[2]
	
	print "router ip is : ",router_ip
	# create an P2P_Interface object from the p2p_framework
	print("ana hena ya roo7 omak :%d" %shutdown[0])
	p2p = p2p_framework.P2P_Interface(shutdown, sendname, sendtype, router_ip)

	# add a message handler to the p2p object
	# --> whenever a message with the command 'PRINT' is received the user 
	#	  defined method 'print_message()' is being executed
	p2p.add_handler('PRINT', print_message)
	p2p.add_handler('PASS', pass_switch)
	p2p.add_handler('REQUEST',request_message)

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
			address_book = p2p.get_address_book()
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
			p2p.sendmessage('TCP', recvname,'','PRINT', data)


		

	
		# the user can send message to other clients by entering:
		# SEND <receiver name> <message data>
		# e.g.: SEND Bob Hi Bob, how are you?
		elif input_text.startswith('PASS'):
			tmp = input_text.partition(' ')
			tmp = tmp[2].partition(' ')
			recvname = tmp[0]
			data = tmp[2]
		
			# send the message using the 'sendmessage()' method of the p2p object
			p2p.sendmessage('TCP', recvname,'', 'PASS', data)


if __name__ == "__main__":
	main()
