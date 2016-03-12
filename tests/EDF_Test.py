import sys
sys.path.insert(0,'/home/bedo/workspace/masterArbeit/abdallah')

from machine_queue import queueElement
import timeTest
from timeTest import myTime

import datetime
import operator
import sys 
import os

def converttoseconds(strtime):

	temp =timeTest.getendtimestr(strtime)
	#print temp 
	temp = myTime(temp)
	seconds = (temp.hours * 60 + temp.minutes) * 60
	return seconds

def interpreteTask(data):
	tempint = list(data)
	priority = int(tempint[1])
	processingTime =int(tempint[2]+tempint[3]+tempint[4]) * 60 # converted to seconds
	endTime = tempint[5]+tempint[6]+tempint[7]+tempint[8]
	endTime = converttoseconds(endTime)
	newTask= {'priority':priority,'processingTime':processingTime,'endTime':endTime}
	return newTask

def getCurrentTimeInSeconds():
	currenttime = datetime.datetime.now()
	currenttimeinseconds = ( currenttime.hour * 60 + currenttime.minute ) * 60
	return currenttimeinseconds


def scheduleTasks(tasksDic):
		scheduleFail = False
		tasksEndTime ={}
		currenttimeinseconds = getCurrentTimeInSeconds()
		# stop running task and calculate remainng time  
		for key,value in tasksDic.iteritems():
			if value._Status == 'Running':
				value._Status = 'Stopped'
				value._ProcessingRmainingTime = currenttimeinseconds - value._StartTime
				
				print ("Running task %s started at %d , remaining time : %d  stopped..."% (value._Name,value._StartTime,value._ProcessingRmainingTime))
				
				

		for key,value in tasksDic.iteritems():
			tasksEndTime[key] =value._EndTime 
		print "unsorted task Queue of the machine :",tasksEndTime
		# sort the tasks according to their endtime (earliest deadline first) 
		sortdtasks = sorted(tasksEndTime.items(),key=operator.itemgetter(1)) 
		print "sorted tasks according to Ealiest Deadline First " , sortdtasks
		print "current time in seconds : ",currenttimeinseconds
		firstelement = (sortdtasks[0][0])
		tasksDic[firstelement]._TempStartTime = currenttimeinseconds
		tasksDic[firstelement]._TempWorstCaseFinishingTime = currenttimeinseconds + tasksDic[firstelement]._ProcessingRmainingTime
		# calculat the worst case finishing time for each task  Priority,EndTime,ProcessingTime,name)
		for i in range(1,len(tasksDic)):
			currenttask = tasksDic[(sortdtasks[i][0])]
			lasttask = tasksDic[(sortdtasks[i-1][0])]
			currenttask._TempStartTime = lasttask._TempWorstCaseFinishingTime
			currenttask._TempWorstCaseFinishingTime = lasttask._TempWorstCaseFinishingTime + currenttask._ProcessingRmainingTime
		for i in range(len(tasksDic)):
			print (" %s Start Time :%f, EndTime: %f , WorstCaseFinishingTime: %f " %(tasksDic[(sortdtasks[i][0])]._Name,tasksDic[(sortdtasks[i][0])]._TempStartTime/3600.0,tasksDic[(sortdtasks[i][0])]._EndTime/3600.0,tasksDic[(sortdtasks[i][0])]._TempWorstCaseFinishingTime/3600.0))
			
		# compare worst case finishing time with end time for each task
		for i in range(len(tasksDic)):
			if (tasksDic[(sortdtasks[i][0])]._TempWorstCaseFinishingTime) < (tasksDic[(sortdtasks[i][0])]._EndTime): 
				print (" %s pass guarantee test "% tasksDic[(sortdtasks[i][0])]._Name)
			elif(tasksDic[(sortdtasks[i][0])]._TempWorstCaseFinishingTime) > (tasksDic[(sortdtasks[i][0])]._EndTime): 
				print (" %s fail in  guarantee test "% tasksDic[(sortdtasks[i][0])]._Name)
				scheduleFail = True

		if (scheduleFail == False):
			print "no fails scheduling ......"
			for i in range(len(tasksDic)):
				tasksDic[(sortdtasks[i][0])]._StartTime = tasksDic[(sortdtasks[i][0])]._TempStartTime
				tasksDic[(sortdtasks[i][0])]._WorstCaseFinishingTime = tasksDic[(sortdtasks[i][0])]._TempWorstCaseFinishingTime
			# respond to comming task for impossible scheduling 



def main():
	taskDic = {}

	data1 = '110300700'
	task = interpreteTask(data1)
	task1 = queueElement(task['priority'],task['endTime'],task['processingTime'],'task1')
	task1._Status = 'Scheduled'
	taskDic['task1'] = task1

	data2 = '130300645'
	task = interpreteTask(data2)
	task2 = queueElement(task['priority'],task['endTime'],task['processingTime'],'task2')
	task2._Status = 'Scheduled'
	task2._StartTime = getCurrentTimeInSeconds() - 900
	taskDic['task2'] = task2

	data3 = '130200645'
	task = interpreteTask(data3)
	task3 = queueElement(task['priority'],task['endTime'],task['processingTime'],'task3')
	task3._Status = 'Scheduled'
	taskDic['task3'] = task3
	testdata = '12345 67891'
	print testdata.split()

	scheduleTasks(taskDic)
	print taskDic	

	a=[1,2,3,4,5]
	del a[0]
	print a




if __name__ == "__main__":
	main()