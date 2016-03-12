
import MySQLdb





db = MySQLdb.connect(host='localhost', user='Shuttle', passwd='raspberry', db='ip')
cur = db.cursor()
            # get the Job data
           
sql = "SELECT * FROM kundenauftrag WHERE KA_Nummer = %s" % (KA_Nummer)

cur.execute(sql)

rows = cur.fetchall()
print rows
