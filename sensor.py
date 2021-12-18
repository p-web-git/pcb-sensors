from datetime import datetime

class Sensor:
	_date = datetime.utcnow()

	def __init__(self):
		pass

	def __str__(self):
        	return self.__class__.__name__

	@property
	def name(self):
		return self.__str__().lower()

	def read(self):
		pass

	def updateDateTime(self):
		self._date = datetime.utcnow()

	def getDateTimeStr(self):
		return self._date.isoformat('T','seconds')

	def getSummaryInJson(self):
		pass

	def close(self):
		pass

def _main():
	import logging, time

	logging.basicConfig(level=logging.DEBUG)

	class MySensor(Sensor):
		def __init__(self, value=0):
			self.updateDateTime()
			self._value = value

		def read(self):
			self.updateDateTime()
			self._value += 1

		def getValue(self):
			return f"Sample from {self.getDateTimeStr()} with value {self._value}"

	sensor = MySensor(10)
	logging.info(sensor.name)

	sensor.read()
	logging.info(sensor.getValue())

	time.sleep(2)

	sensor.read()
	logging.info(sensor.getValue())

	sensor.close()
	logging.info("Exit")

if __name__ == '__main__':
	_main()





