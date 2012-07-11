#!/usr/bin/env python
import MySQLdb

class dbc(object):
        def __init__(self):
                self.db_host = "localhost"
                self.db_username = "puppetreg"
                self.db_password = "puppetreg"
                self.db_name = "puppetreg"
        def insert(self, statement):
                conn = MySQLdb.Connection(host=self.db_host, user=self.db_username, passwd=self.db_password, db=self.db_name)
                curs = conn.cursor()
                curs.execute(statement)
                conn.commit()
                conn.close()
	def select(self, statement):
                conn = MySQLdb.Connection(host=self.db_host, user=self.db_username, passwd=self.db_password, db=self.db_name)
                curs = conn.cursor()
		curs.execute(statement)
		conn.commit()
		result = curs.fetchall()
		return result
        def close(self):
                conn.close()
