#!/usr/bin/python
# coding=utf-8
# mysql_class.py
#----------------

import MySQLdb
import threading


class sqldb():

	def __init__(self,host,user,passwd,db):
		self.host = host
		self.user = user
		self.passwd = passwd
		self.db = db
		self.__mysqldb = None
		self.__cur = None
		self.rlock = threading.RLock()
		
	def __open(self,curtype="list"):
		self.__mysqldb = MySQLdb.connect(self.host, self.user, self.passwd, self.db)
                if curtype == "list":
                        self.__cur = self.__mysqldb.cursor()
                elif curtype == "dict":
                        self.__cur = self.__mysqldb.cursor(MySQLdb.cursors.DictCursor)
		
	def __close(self):
		self.__cur.close()
		self.__mysqldb.close()
		
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
				
	def request(self, sql, curtype="dict"):
		with self.rlock:
				if sql[0:6] == "SELECT":
					return self.select(sql, curtype)
					
				elif sql[0:6] == "UPDATE" or sql[0:6] == "INSERT":
					tmp = self.update(sql)
					if tmp is True:
						return True
					else:
						pass
				