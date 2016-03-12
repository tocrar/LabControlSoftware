#!/usr/bin/python

# p2p_framework.py by Marcel Wellpott

# import standard libraries
import threading
import struct
import socket
import time

import sys
import signal 
import os

# import user defined libraries
import tcp_framework
import udp_framework
import ip_module
#==============================================================================
class P2P_Interface:
	"""
	This class provides an interface for creating a Peer-to-Peer network and 
	sending and receiving messages using TCP/IP and UDP network communication.
	
	For using this interface, an object of this class must be created for each 
	client. There are three parameters: the shutdown-parameter must be provided
	as call-by-reference and is used for terminating all threads which are 
	started within this object instance. The name-parameter and the type-
	parameter are used for discribing the client within the network. Please 
	make sure the name-parameter is unique within its network!
	
	There are three methods within this class which provide the functionality 
	needed for a Peer-to-Peer communication:
	- sendmessage (send a specified message to a/all member(s) of the network)
	- get_address_book (get an overview of all known members of the network)
	- add_handler (specify which method is meant to be called when a certain 
				   command is received as a message)

	"""

	#--------------------------------------------------------------------------
	def __init__( self, shutdown, name, type, router_address ):
	#--------------------------------------------------------------------------
		"""
		Initialize an object of P2P_Interface
		
		shutdown		:	A parameter used for stopping the infinite loop of
							the different threads which are started within this
							object
		name			:	The name of the client. The name is used for 
							addressing a member within the network. Please make
							sure the name is unique within its network!
		type			:	The type of the client.	
		router_address	:	IP address of the router
		"""
	

		
		# initialize object variables
		self.name = name
		self.type = type
											 
		# The shutdown-parameter is used for stopping the infinite loop of the
		# different threads which is necessary for terminating the program
		self.shutdown = shutdown
				
		
		# The client needs to know its own IP address. To determine this 
		# address, the client connects to the router using a TCP/IP connection.
		# From this connection the own IP address is read.
		self.__own_address = ''
		#s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		#s.connect( ( router_address, 80 ) )
		#self.__own_address = s.getsockname()[0]
		#s.close()
		self.__own_address = ip_module.get_lan_ip()
	
	
		# All messages received by this client (whether TCP or UDP) are added
		# to a common message list. Messages within this list are sorted by
		# their priority.
		self.__msg_list = []
		# The message list is protected by a semaphore to make sure only one 
		# thread at a time is reading/writing from/to the list.
		self.__msg_lock = threading.Lock()
		# There is an event object which is set whenever a message is being
		# added to the message list. 
		self.__msg_event = threading.Event()
		self.__msg_event.clear()
		# There is a locale message id number which is increased by one every
		# time a message is send by this client.
		self.__msg_id = 0
		# Whenever the client fails to send a message, the message is added to
		# the '__failed_to_send_list'.
		self.__failed_to_send_list = []
		
		
		# Initialize the Peer object which is used for sending and receiving 
		# messages using TCP/IP
		self.__tcp_peer = tcp_framework.Peer(54545, 
											 self.add_message_to_list,
										     self.shutdown)
							
							
		# Initialize the Peer object which is used for sending and receiving 
		# messages using UPD		   
		self.__udp_peer = udp_framework.Peer(56565, 
											 self.add_message_to_list,
										     self.shutdown)
						
						
		# The P2P_Interface object maintainces an address book which contains
		# all known members of the network. The address book is initialized 
		# with the address for broadcasting. This address distinguishes between
		# operating systems:
		#		For Linux(Raspbian) use '<broadcast>'
		#		For Windows use '192.168.1.255'
		#
		# The address book is build using a hashmap. Every clilents name is
		# mapped to a triple:	1. the IP address
		#						2. the type
		#						3. the timeout counter
		#
		self.__address_book = {'Broadcast' : ['<broadcast>', None, 100]}
		#self.__address_book = {'Broadcast' : ['192.168.1.255', None, 100]}
		#
		# The thread 't_address_book' runs an instance of the method 
		# '__update_address_book()' which continuously updates the address book
		t_address_book = threading.Thread( target = self.__update_address_book,
										 args=[6,6])
		t_address_book.start()
		
		
		# The hashmap '__handlers' concatenates commands with methods. Every
		# message contains a command which is specified by the user 
		# (e.g. 'PRINT'). According to the command, the message will be handled
		# by calling the method which is referenced by the command
		# (e.g. 'PRINT' --> print_message()). New handlers can be added using
		# the public method 'add_handler()'
		self.__handlers = {}
	    # The thread 't_handlemessages' runs an instance of the method 
		# '__handlemessages()' which continuously handles all messages within
		# the message list.
		t_handlemessages = threading.Thread( target = self.__handlemessages)
		t_handlemessages.start()
		
	def mysignal_handler(self,signal,frame):
		print "you pressed ctrl+c !!"
		self.shutdown[0] = 0
		sys.exit(0)



	def display_message_list(self):
		print self.__msg_list

		
	#--------------------------------------------------------------------------
	def __handlemessages( self ):
	#--------------------------------------------------------------------------
		"""
		This method is called once during init and must be run in a seperated 
		thread. It continously handles all messages within the message list.
		"""
		
		# infinte loop
		while not self.shutdown[0]:
			# wait until a message is added to the message list
			# maximum waiting time is set to one second
			self.__msg_event.wait(1)
			# check if there really is a message in the list
			if self.__msg_list:
				# set the semaphore so no other thread can read/write from/to
				# the message list
				self.__msg_lock.acquire()
				# get the very top message from the list and call the handler
				self.__handlemessage(self.__msg_list.pop())
				#reset event
				self.__msg_event.clear()
				# reset the semaphore
				self.__msg_lock.release()
		
		
	#--------------------------------------------------------------------------
	def __update_address_book( self, cycle_time, timeout ):
	#--------------------------------------------------------------------------
		"""
		This method is called once during init and must be run in a seperated 
		thread. It continously updates the address book. Therefore it 
		broadcast a message with the command 'introduction'. Every client which
		receives this message will add this client to their own address book. 
		After introducing itself to all network members it will iterate over 
		all clients within its own address book and increase their timeout 
		counter by one. Every client that exceeds the given timeout maximum
		will be deleted from the address book.
		
		cycle_time	:	defines the duration of an update cycle
		timeout		:	defines the maximum number of cycles at which a client
						will be removed from the address book		
		"""
		
		# infinte loop
		while not self.shutdown[0]:
		
			# broadcast message to introduce itself to all network members
			self.sendmessage('UDP', 'Broadcast', '', 'introduction', '')
			
			# create a list of all clients which will be deleted during this
			# cycle
			blacklist = []
			
			# iterate over all clients within the address book
			for name in self.__address_book:
				# add the client to the blacklist if it has reached the timeout
				# maximum
				if self.__address_book[name][2] == timeout:
					blacklist.append(name)
				# if the client has not reached the timeout maximum, increase
				# the timeout counter by one
				else:
					self.__address_book[name][2] += 1
			
			# remove all clients within the blacklist from the address book
			for name in blacklist:
				del self.__address_book[name]
				print 'Removed', name, 'from the adrress book.'
			
			# wait the cycle time
			time.sleep(cycle_time)
		
				
	#--------------------------------------------------------------------------
	def __handlemessage( self, msg ):
	#--------------------------------------------------------------------------
		"""
		This method is called for handling a message. For choosing the method
		to handle the given message the command of the message is evaluated.
		If the message is an introduction message (command = 'introduction')
		the sender of the message will be added to the address book. If the
		sender is already inside the address book, its timeout counter will be
		resettet.
		
		msg		:	contains the complete decoded message as a hashmap
		"""
		
		# if the message is an introduction message
		if msg['command'] == 'introduction':
			#print "Introduction from ",msg['sendername'] for debugging 
			# print a prompt if the sender is new to the address book
			if not msg['sendername'] in self.__address_book:
				print 'Added', msg['sendername'], 'to the address book.'
			# add/update sender to the address book
			self.__address_book[msg['sendername']] = \
									[msg['senderaddr'], msg['sendertype'], 0]
									
		# check if there is a proper handler for the given command in the 
		# handler list							
		elif msg['command'] in self.__handlers:
			# execute the handler and provide the message as a parameter
			#print "handler called for message : ",msg
			self.__handlers[msg['command']](msg)
			
		# if there is no proper handler for the given command, print an error
		# message
		else:
			print "Error: No event handler given for command '", \
															msg['command'], "'"
				
				
	#--------------------------------------------------------------------------
	def __encodemsg( self, recvaddr, recvtype, command, data, prio, ack):
	#--------------------------------------------------------------------------
		"""
		All message are being encoded by this methode before they are send.
		For encoding the message the standard library 'struct' is used. Learn
		more about 'struct' at: https://docs.python.org/2/library/struct.html
		
		recvaddr	:	IP address of the receiver
		recvtype	:	type of the receiver(s) of the message
		command		:	command of the message which defines which method is
						called by the message handler of the receiver to handle
						this message
		data		:	data of this message
		prio		:	priority of this message (highest priority = 0)
		ack			:	set a flag to make the receiver confirm the receipt by
						sending an acknowledgement
		
		
		Actually every message is encoded twice: The outer layer consists of
		a 48 sign header followed by the inner layer of the message. The header
		contains the format for decoding the actual message within the inner 
		layer.
		
		content of outer message layer:
		[48 sign format header],[content of the inner layer ...]
		
		content of inner message layer:
		[message ID],[priority],[acknowledgement],[receiver address],
			[receiver address],[receiver type],[sender address],[sender name],
				[sender type],[command],[data]
							
		message ID		:	unique message ID
							--> unsigned long long (8 Bytes)
		priority		:	priority of message
							--> unsigned short (2 Bytes)
		acknowledgement	:	if != 0 --> send acknowledgement
							--> unsigned short (2 Bytes)
		receiver address:	IP address of receiver
							--> string of any length
										example: '192.168.1.45'
							for broadcast use '<broadcast>' or '192.168.1.255'
		receiver type	:	type of receiver
							--> string of any length
		sender address	:	IP address of sender
							--> string of any length
		sender name		:	name of sender
							--> string of any length
		sender type		:	type of sender
							--> string of any length
		command			:	determines the method to handle this message
							--> string of any length
		data			:	the actual content of the message
							--> string of any length
		"""
		
		# define the format for the inner message layer
		fmt_msg = "Qhh%ds%ds%ds%ds%ds%ds%ds" % (len(recvaddr),
												len(recvtype),
												len(self.__own_address),
												len(self.name), 
												len(self.type), 
												len(command), 
												len(data)
												)
		
		# encode the inner message layer
		msg_encoded = struct.pack(fmt_msg,
								  self.__msg_id, 		# message ID
								  prio,					# priority
								  ack,					# acknowledgement
								  recvaddr,				# receiver address
								  recvtype,				# receiver type
								  self.__own_address,	# sender address
								  self.name,			# sender name
								  self.type,			# sender type
								  command,				# command
								  data)					# data
		
		# define the format for the outer message layer
		fmt_wrapper = "48s%ds" % len(msg_encoded)
		
		# encode the complete message
		msg_wrapped = struct.pack(fmt_wrapper, fmt_msg, msg_encoded)
	
		return msg_wrapped
		
		
	#--------------------------------------------------------------------------
	def __decodemsg( self, encoded_msg ):
	#--------------------------------------------------------------------------
		"""
		Every message needs to be decoded before it handled by the message 
		handler. This method takes the encoded message and converts it into a
		python dictionary (a hashmap). Refer to the discription of the method
		'__encodemsg()' for concrete information about the message format.
		"""
		
		# declare a python dictionary for storing the message content
		msg_dict = {}
		
		try:
		
			# decode the message using the format information within the header
			# of the outer layer of the message
			msg = struct.unpack(encoded_msg[:48], encoded_msg[48:])
			
			# add the content from the decoded message to the message hashmap
			msg_dict['message_id'] 		= msg[0]
			msg_dict['priority'] 		= msg[1]
			msg_dict['acknowledgement'] = msg[2]
			msg_dict['recvaddr'] 		= msg[3]
			msg_dict['recvtype'] 		= msg[4]
			msg_dict['senderaddr']		= msg[5]
			msg_dict['sendername'] 		= msg[6]
			msg_dict['sendertype'] 		= msg[7]
			msg_dict['command'] 		= msg[8]
			msg_dict['data'] 			= msg[9]
			
		except:
			# if any error occures while encoding the message print an error
			# prompt in the console
			print 'Error: Message could not be decoded.'
			return None
		
		return msg_dict
		
	
	#--------------------------------------------------------------------------
	def add_message_to_list( self, encoded_msg ):
	#--------------------------------------------------------------------------
		"""
		This method is used by the TCP and UDP Peer objects for adding messages
		to the message list.
		
		encoded_msg		:	complete encoded message as it was received from
							the TCP or UDP peer
		"""
		
		# decode the message
		msg = self.__decodemsg(encoded_msg)
		# set the semaphore so no other thread can read/write from/to the 
		# message list
		self.__msg_lock.acquire()
		# add the message to the message list
		self.__msg_list.append( msg )
		# sort the complete message list by priority
		# highest priority (=0) at the very top of the list
		self.__msg_list.sort(key=lambda msg: msg['priority'])
		# reset the semaphore
		self.__msg_lock.release()
		# set the message event so the message handler will continoue its work
		self.__msg_event.set()
					
		


	#--------------------------------------------------------------------------
	def add_handler( self, command, handler ):
	#--------------------------------------------------------------------------
		"""
		This method is used for adding handlers for messages to the list of
		handlers.
		
		command		:	the command which indicates the method to be called
		handler		:	the method which is meant to be executed when the 
						corresponding command is received as a message
		"""
			
		self.__handlers[command] = handler
		
	
	#--------------------------------------------------------------------------
	def get_address_book( self ):
	#--------------------------------------------------------------------------
		"""
		This method returns a list of all clients within the address book. The
		list is given as a list of tuples (name, type):
		[['Alice', 'shuttle'],['Bob', 'machine'], ...
		"""
		
		address_book = []
	
		# iterate over all clients within the address book
		for name in self.__address_book:
			address_book.append([name, self.__address_book[name][1]])
			
		return address_book
		
		
	#--------------------------------------------------------------------------
	def sendmessage( self,contype, recvname, recvtype, command, data, prio=1,
					 ack=0):
	#--------------------------------------------------------------------------
		"""
		This method is used for sending messages to any client within the 
		Peer-to-Peer network.
		
		contype		:	defines type of connection: either TCP or UDP
		recvname	:	name of the receiver of the message
						(names according to the names in the address book)
		recvtype	:	type of the receiver(s) of the message
		command		:	command of the message which defines which method is
						called by the message handler of the receiver to handle
						this message
		data		:	data of this message
		prio		:	priority of this message (highest priority = 0)
						(optional parameter)
		ack			:	set a flag to make the receiver confirm the receipt by
						sending an acknowledgement
						(optional parameter)
		"""
		
		# define an unspecified error message
		error_text = 'No specific error information.'
		
		# declare a variable to contain the encoded message
		encoded_msg = None
		
		try:
			# broadcasting is only possible using UDP
			if contype == 'TCP' and recvname == 'Broadcast':
				contype = 'UDP'
			
			# Get the IP address of the receiver from the address book.
			# If the receivers name is not found, an error is raised
			recvaddr = ''
			if recvname in self.__address_book:
				recvaddr = self.__address_book[recvname][0]
			else:
				error_text = 'Name of receiver is unknown!'
				raise
				
			# encode the message
			encoded_msg = \
				self.__encodemsg(recvaddr, recvtype, command, data, prio, ack)
		
			# declare a variable to check whether sending the message was 
			# successfull or not
			success = False
			
			# send the encoded message according to the defined connection type
			if contype == 'TCP':
				success = self.__tcp_peer.connectandsend(recvaddr, encoded_msg)
			elif contype == 'UDP':
				success = self.__udp_peer.send(recvaddr, encoded_msg)
			else:
				error_text = \
					'No valid connection type given! Choose either TCP or UDP.'
				raise
				
			# if sending the message failed, raise an error
			if success == False:
				error_text = 'Error during transmission of message!'
				raise
		
		except:
			# if any error occures while sending the message, print the error
			# prompt in the console and add the message to the 'failed_to_send_
			# list'
			print 'An error occured while sending a message:', error_text
			self.__failed_to_send_list.append(encoded_msg)
		
		# increase the message id counter by one
		self.__msg_id += 1
		
# *****************************************************************************
