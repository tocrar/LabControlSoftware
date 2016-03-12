import timeTest
from timeTest import myTime
import datetime
import operator



def converttoseconds(strtime):

	temp =timeTest.getendtimestr(strtime)
	#print temp 
	temp = myTime(temp)
	seconds = (temp.hours * 60 + temp.minutes) * 60
	return seconds



def main():

	task1={"processingtime":30,"endtime":"1430"}
	task2={"processingtime":30,"endtime":"1500"}
	task3={"processingtime":20,"endtime":"2355"}

	mytasks= {}
          
	tasks ={} # dic to order the tasks according to their endtime (earliest deadline first) 

	# convert end time to secnds in order to compare them 

	task1['endtime'] = converttoseconds(task1['endtime'])
	task1['processingtime'] = task1['processingtime'] * 60   # convert to seconds 
	print task1
	tasks['task1'] = task1['endtime'] # add task1 to tasks dic

	mytasks['task1'] = task1

	task2['endtime'] = converttoseconds(task2['endtime'])
	task2['processingtime'] = task2['processingtime'] * 60 
	print task2
	tasks['task2'] = task2['endtime']
	mytasks['task2'] = task2

	task3['endtime'] = converttoseconds(task3['endtime'])
	task3['processingtime'] = task3['processingtime'] * 60 
	print task3
	tasks['task3'] = task3['endtime']
	mytasks['task3'] = task3

	print "unsorted tasks " , tasks

	# sort the tasks according to their endtime (earliest deadline first) 
	sortdtasks = sorted(tasks.items(),key=operator.itemgetter(1)) 
	print "sorted tasks " , sortdtasks
	print mytasks[(sortdtasks[0][0])]


	currenttime = datetime.datetime.now()
	currenttimeinseconds = ( currenttime.hour * 60 + currenttime.minute ) * 60
	print "current time in seconds : ",currenttimeinseconds

	
	mytasks[(sortdtasks[0][0])]['wft'] = currenttimeinseconds + mytasks[(sortdtasks[0][0])]['processingtime']
	print mytasks[(sortdtasks[0][0])]

	for i in range(1,len(mytasks)):	
		#print mytasks[(sortdtasks[i][0])]
		currenttask = mytasks[(sortdtasks[i][0])]
		lasttask = mytasks[(sortdtasks[i-1][0])]
		currenttask ['wft'] = lasttask['wft']+ currenttask ['processingtime']	

	for i in range(len(mytasks)):
		print ("task number %d : %s "% (i, mytasks[(sortdtasks[i][0])]))


if __name__ == "__main__":
	main()
