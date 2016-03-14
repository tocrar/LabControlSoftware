import time
from datetime import datetime
import operator 

class Machine:
	

	def __init__(self):
		self.contractList = {"shuttle1":{'contNum':1,"periority":2,"EndTime":12,"processingTime":10},"shuttle2":{"contNum":2,"periority":1,"EndTime":15,"processingTime":20}}
		#contractList={}



# step 1 -->> reorder according to deadline
def OrderAccordingToDeadline(contracts):
	mydic = {}
	for key,value in contracts.items():
		mydic[key] = contracts[key]['EndTime']
		print key , mydic[key]
	sorted_mydic = sorted(mydic.items(),key=operator.itemgetter(1))
	#print sorted_mydic
	return sorted_mydic # [('shuttle1', 12), ('shuttle3', 14), ('shuttle2', 15)]

# calculate worst case execution time for each task
def worstCaseTime(contracts):
	orderedlisttuple = OrderAccordingToDeadline(contracts) # ordered according to endTime
	worstCaseTimeDic={}
	prevtime =0
	print orderedlisttuple
	fmt = '%H:%M:%S'
	for element in orderedlisttuple:
		worstCaseTimeDic[element[0]] = time.gmtime(contracts[element[0]]['processingTime']+time.time()) 
		prevtime = worstCaseTimeDic[element[0]]
		print element
	print worstCaseTimeDic

	for val in worstCaseTimeDic.itervalues():
		print "value : ",val

def main():
	mymachine =Machine()
	print time.gmtime(0)
	print mymachine.contractList
	mymachine.contractList['shuttle3'] = {'contNum':3,"periority":3,"EndTime":14,"processingTime":30}
	print mymachine.contractList
	#mysortedtupple = OrderAccordingToDeadline(mymachine.contractList)
	worstCaseTime(mymachine.contractList)
	
	start = time.time()
	print "start : " ,start
	time.sleep(2)
	done = time.time()
	print "END   : ",done
	elapsed = done - start
	print elapsed
	print "utc time : ",time.time()

	s1 ='10:33'
	s2= '11:33'
	fmt = '%H:%M'
	tdelta = datetime.strptime(s2,fmt) - datetime.strptime(s1,fmt)
	print "delta  " ,tdelta

if __name__ == "__main__":
	main()
