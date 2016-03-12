#!/usr/bin/python

# udp_framework.py by Marcel Wellpott

# import standard libraries
import socket
import threading
import traceback

#==============================================================================
class Peer:
	"""
	This class is used for receiving and sending messages using UDP. Therefore
	a seperated thread is started which will be listening for incoming messages
	at the specified port. Any message received will be added to a list.
	"""

	#--------------------------------------------------------------------------
	def __init__( self, serverport, add_message_to_list, shutdown ):
	#--------------------------------------------------------------------------
		"""
		Initializing of an object of the class Peer.
		
		serverport	:			Port number which is used for listening and 
								sending messages using UDP. Any port number can
								be chosen but make sure all clients are using 
								the same port number for UDP communication.
		add_message_to_list	:	A function adding a received message to the 
								list of messages.
		shutdown	:			A parameter used for stopping the infinite loop
								of the main thread which is listening for 
								incoming messages.
		"""
		
		# initialize object variables
		self.__serverport = int(serverport)
		self.shutdown = shutdown
		
		# create a seperated thread for listening for incoming messages
		t = threading.Thread( target = self.__mainloop, 
							  args=[add_message_to_list])
		t.start()

		
	#--------------------------------------------------------------------------
	def __mainloop( self, add_message_to_list ):
	#--------------------------------------------------------------------------
		"""
		This method creates a socket at the specified port. An infinite loop is
		used for listening for incoming messages. If a message is received it 
		will be added to a list and the loop continues listening for new 
		messages.
		
		This method is private.
		
		add_message_to_list	:	A function adding a received message to the 
								list of messages.
		"""
		
		# create a socket for UDP communication
		s = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
		# set options of the socket
		s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
		# bind socket to the defined port
		s.bind( ( '', self.__serverport ) )
		# set socket timeout to 2 seconds
		s.settimeout(2)
		
		# infinte loop
		while not self.shutdown[0]:
			try:
				# if a message is received ...
				msg, addr = s.recvfrom(2048)
				# msg contains the actual message
				# addr contains the address of the sender
				
				# ... add it to the list
				add_message_to_list(msg)
				
			except:
				# If the listening socket times out (happens every 2 seconds) 
				# an error is raised which will be caught by this block.
				# The command 'continue' will return to the while loop and 
				# check whether the shutdown parameter has changed. If the 
				# shutdown parameter has turned to True the while loop 
				# terminates. Otherwise it will continue listening.
				continue

		# close the socket
		s.close()

	
	#--------------------------------------------------------------------------
	def send( self, host, msg ):
	#--------------------------------------------------------------------------
		"""
		This method is used for sending messages using UDP. The method returns
		True after successfully sending a message. If an error occures during
		sending the message, the method returns False and an error message is
		printed within the console.
		
		This method is public.
		
		host	:	contains the address of the receiver
		msg		:	contains the content of the message
		"""
	
		try:
			# create a socket for UDP communication
			s = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
			
			# if the sending operation is a broadcast, set the options for
			# broadcasting
			if host == '<broadcast>':
				s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			
			# concatenate the address of the receiver with the port number
			addr = (host, self.__serverport)
			
			# send the message to the address
			s.sendto(msg, addr)
			
			# close the socket
			s.close()
			
		except:
			# if any error occures, print the error message in the console
			# and return False
			traceback.print_exc()
			return False
		
		# return True after successfully sending the message
		return True
