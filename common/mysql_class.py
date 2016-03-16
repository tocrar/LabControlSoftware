#!/usr/bin/python
# coding=utf-8
# mysql_class.py
#----------------------------------------------------------------------------------------------------------------

#standart library:
import threading

#extra library:
import MySQLdb

#----------------------------------------------------------------------------------------------------------------
'''
this class uses the MySQLdb library.
You can get it on linux with:
sudo apt-get install python-mysqldb
Other source is (untested):
https://github.com/farcepest/MySQLdb1
'''
#----------------------------------------------------------------------------------------------------------------

class sqldb():

	def __init__(self,host,user,passwd,db):
		self.host = host
		self.user = user
		self.passwd = passwd
		self.db = db
		self.__mysqldb = None
		self.__cur = None
		self.rlock = threading.RLock()
		
	#---------------------------
	
	def __open(self,curtype="list"):
		self.__mysqldb = MySQLdb.connect(self.host, self.user, self.passwd, self.db)
                if curtype == "list":
                        self.__cur = self.__mysqldb.cursor()
                elif curtype == "dict":
                        self.__cur = self.__mysqldb.cursor(MySQLdb.cursors.DictCursor)
		
	def __close(self):
		self.__cur.close()
		self.__mysqldb.close()
		
	#---------------------------
		
	def select(self,sql,curtype="dict"):
		with self.rlock:
			try:
				self.__open(curtype)
				self.__cur.execute(sql)
				rows = self.__cur.fetchall()
				self.__close()
				return rows
			except:
				return False

	#---------------------------
				
	def select_desc(self,sql,curtype="dict"):
		with self.rlock:
			try:
				self.__open(curtype)
				self.__cur.execute(sql)
				rows = self.__cur.fetchall()
				desc = self.__cur.description
				self.__close()
				return rows, desc
			except:
				return False, False
	
	#---------------------------
	
	def update(self,sql):
		with self.rlock:
			try:
				self.__open()
				self.__cur.execute(sql)
				self.__mysqldb.commit()
				self.__close()
				return True
			except:
				return False
	
	#---------------------------
	
	def sqlquery(self, sql, curtype="dict", desc=False):
		with self.rlock:
				if sql[0:6] == "SELECT" and desc==False:
					return self.select(sql, curtype)
					
				elif sql[0:6] == "SELECT" and desc==True:
					return self.select_desc(sql, curtype)
					
				elif sql[0:6] == "UPDATE" or sql[0:6] == "INSERT":
					tmp = self.update(sql)
					if tmp is True:
						return True
					else:
						pass

#----------------------------------------------------------------------------------------------------------------
'''
Examplecodes:


#---------------------------

SELECT (result as list of dictionaries):

	database:
		
		testdb:
		
			testtable:
				
				id		column1		column2		column3
				1		test				test2				test3
				2		test				test2				test3				
				3		test				test2				test3			

				
	code:
	
		import mysql_class

		host = "192.168.1.1"
		user = "testuser"
		passwd = "testpasswd"
		db = "testdb"
		mydb = mysql_class.sqldb(host,user,passwd,db)

		sql = "SELECT * FROM testtable'"
		rows = mydb.sqlquery(sql)
		for dict in row:
			print dict["id"]
			print dict
		
		
	output:
		
		'1'
		{'column1': 'test', 'id': '1', 'column3': 'test3', 'column2': 'test2'}
		'2'
		{'column1': 'test', 'id': '2', 'column3': 'test3', 'column2': 'test2'}
		'3'
		{'column1': 'test', 'id': '3', 'column3': 'test3', 'column2': 'test2'}

		
#---------------------------
		
SELECT (result as list of lists):

	database:
		
		testdb:
		
			testtable:
				
				id		column1		column2		column3
				1		test				test2				test3
				2		test				test2				test3				
				3		test				test2				test3			

				
	code:
	
		import mysql_class

		host = "192.168.1.1"
		user = "testuser"
		passwd = "testpasswd"
		db = "testdb"
		mydb = mysql_class.sqldb(host,user,passwd,db)

		sql = "SELECT * FROM testtable'"
		rows = mydb.sqlquery(sql, curtype="list")
		for list in row:
			print list[0]
			print list

			
	output:
		
		'1'
		('1', 'test', 'test2', 'test3')
		'2'
		('2', 'test', 'test2', 'test3')
		'3'
		('3', 'test', 'test2', 'test3')

'''
#----------------------------------------------------------------------------------------------------------------
