import Queue
import threading
import time
import sys
import keyword
exitFlag = 0
queueLock = threading.Lock()
workQueue = Queue.Queue()
threads = []
threadID = 1
maxNumberOfThreads = 2
class myThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        print "Starting " + self.name
        process_data(self.name, self.q)
        print "Exiting " + self.name

def process_data(threadName, q):
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            dataOne = q.get()
            dataTwo = q.get()
            queueLock.release()
            oneTuple(dataOne,dataTwo)
            print "%s processing %s" % (threadName, dataOne)
        else:
            queueLock.release()
            return
        time.sleep(1)

def oneTuple(firstRelay,secondRelay):
	# have to call ting here
	print "In oneTuple"
	print "FirstRelay   " + firstRelay + " secondRelay " + secondRelay

def find(inputDictionary):
	threadID = 1
	print "In find"
	queueLock.acquire()
	for word in inputDictionary.keys():
		workQueue.put(word)
		workQueue.put(inputDictionary.get(word))
	queueLock.release()

	mycopy = []
	while True:
		try:
			elem = workQueue.get(block = False)
			if not elem:
				break
			mycopy.append(elem)
		except Exception, e:
			break

	for elem in mycopy:
		workQueue.put(elem)
	# for elem in mycopy:
	# 	print elem

	while threadID <= maxNumberOfThreads:
		thread = myThread(threadID,"Thread"+str(threadID),workQueue)
		thread.start()
		threads.append(thread)
		threadID+=1
		
	# Wait for queue to empty
	while  not workQueue.empty():
		pass
	print "done"
	# while not workQueue.empty():
 #    		pass
	# Notify threads it's time to exit
	exitFlag = 1

	# Wait for all threads to complete
	for t in threads:
    		t.join()
	print "Exiting Main Thread"



mydict = {'one1': 'one2', 'two1': 'two2', 'three1': 'three2','four1':'four2'};

find(mydict)


