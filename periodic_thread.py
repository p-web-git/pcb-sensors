from threading import Thread, Timer
from datetime import datetime, timedelta
import signal, os, sys, logging
import time

class RepeatTimer(Timer):
	def run(self):
		nextRunTime = datetime.utcnow() + timedelta(seconds=self.interval)
		wait_s = self.interval
		while not self.finished.wait(wait_s):
			try:
				self.function(*self.args, **self.kwargs)
			except:
				os.kill(os.getpid(), signal.SIGUSR1)
				raise
			nextRunTime = nextRunTime + timedelta(seconds=self.interval)
			wait_s = (nextRunTime - datetime.utcnow()).total_seconds()
			if (wait_s <= 0):
				logging.critical("Next thread execution was in the past")
				os.kill(os.getpid(), signal.SIGUSR1)
				return
				# nextRunTime = datetime.utcnow() + timedelta(seconds=self.interval)
				# wait_s = seconds=self.interval
				

def _testThread():
	logging.info("Test code")
	#a=1/0

def terminate(signum, frame):
	logging.info("\nSignal captured...")

def _main():
	logging.basicConfig(level=logging.INFO)
	exit_code = 0

	tt = RepeatTimer(0.05, _testThread)
	tt.start()

	for sig in [signal.SIGUSR1]:
		signal.signal(sig, terminate)

	time.sleep(2)
	tt.cancel()
	tt.join()

	logging.info("Exit %d" % (exit_code))

if __name__ == '__main__':
	_main()

