

from freeTimeSlots import FreeTimeSlot
from machine_queue import queueElement

import datetime 
import operator

def getCurrentTimeInSeconds():
	currenttime = datetime.datetime.now()
	currenttimeinseconds = ( currenttime.hour * 60 + currenttime.minute ) * 60
	return currenttimeinseconds


def print_elements_queue(taskDic):
	print "|\tTask name\t|\tStart Time\t|\tFinish Time\t|\tProcessing Time\t|\tDeadline\t|\tStatus"
	print "|\t---------\t|\t----------\t|\t-----------\t|\t---------\t|\t------\t\t|\t-------"
	for key,value in taskDic.iteritems():
		print("|\t%s\t|\t%d:%d\t\t|\t%d:%d\t\t|\t%d:%d\t\t|\t%d:%d\t\t|\t%s\t\t"%(key,value._StartTime/3600,(value._StartTime%3600)/60,value._WorstCaseFinishingTime/3600,(value._WorstCaseFinishingTime%3600)/60,value._ProcessingRmainingTime/3600,(value._ProcessingRmainingTime%3600)/60,value._EndTime/3600,(value._EndTime%3600)/60,value._Status))

def printSlots(slotsList):
	print "|\tSlot num.\t|\tstart Time\t|\tDuration\t|\tEnd Time"
	print "|\t---------\t|\t----------\t|\t---------\t|\t---------"
	for i in range(len(slotsList)):
		tempStart = slotsList[i].getStartTime()
		tempDuration = slotsList[i].getDuration()
		tempEnd  = slotsList[i].getEndTime()
		print("|\t%d\t\t|\t%d:%d\t\t|\t%d:%d\t\t|\t%d:%d\t\t"%(i,tempStart/3600,(tempStart%3600)/60,tempDuration/3600,(tempDuration%3600)/60,tempEnd/3600,(tempEnd%3600)/60))

def getFreeTimeSlots(tasksDict):
	tasksEndTime ={}
	timeSlotsList =[]
	for key,value in tasksDict.iteritems():
		tasksEndTime[key] =value._EndTime
	sortedtasks = sorted(tasksEndTime.items(),key=operator.itemgetter(1))
	maxval = max(sortedtasks)
	print type(maxval[1]), maxval[1]	
	print "sorted tasks :" , sortedtasks 
	for i in range(len(sortedtasks)):
		tempEnd = tasksDict[sortedtasks[-i-1][0]]._StartTime
		timeSlotsList.append(FreeTimeSlot())
		timeSlotsList[i].setEndTime(tempEnd)
		

	for i in range(0,len(sortedtasks)-1):
		tempStart = tasksDict[sortedtasks[-i-2][0]]._EndTime
		timeSlotsList[i].setStartTime(tempStart)

	timeSlotsList[len(sortedtasks)-1].setStartTime(getCurrentTimeInSeconds()) #start time for the last time slot = currenttime 

	for i in range(len(sortedtasks)):
		tempDuration = timeSlotsList[i].getEndTime() - timeSlotsList[i].getStartTime()
		timeSlotsList[i].setDuration(tempDuration)

	for i in range(len(sortedtasks)):
		print("slot number %d , start time: %d ,End time: %d, duration: %d"%(i,timeSlotsList[i].getStartTime(),timeSlotsList[i].getEndTime(),timeSlotsList[i].getDuration()))

	return timeSlotsList
	



def main():
	tasks_dict ={}
	slotList = []
#__init__(self,Priority,EndTime,ProcessingTime,name):
	task1 = queueElement(1,0,600,'shuttle_1')
	task1._StartTime = getCurrentTimeInSeconds() + 1300 
	task1._EndTime = task1._StartTime + task1._ProcessingTime 
	tasks_dict[task1._Name] = task1

	task2 = queueElement(2,0,600,'shuttle_2')
	task2._StartTime = getCurrentTimeInSeconds() + 3600 
	task2._EndTime = task2._StartTime + task2._ProcessingTime
	tasks_dict[task2._Name] = task2 

	task3 = queueElement(3,0,600,'shuttle_3')
	task3._StartTime = getCurrentTimeInSeconds() + 7200 
	task3._EndTime = task3._StartTime + task3._ProcessingTime
	tasks_dict[task3._Name] = task3

	slotList = getFreeTimeSlots(tasks_dict)
	print FreeTimeSlot.slotsNumber
	print_elements_queue(tasks_dict)
	print"\n\n"
	printSlots(slotList)


if __name__ == '__main__':

	main()


