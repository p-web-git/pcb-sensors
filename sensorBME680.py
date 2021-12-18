import bme680
from datetime import datetime
import logging, time

class BME680:
	def __init__(self, enableGas=False, skipNGasSamples=0, i2c_device=None):
		self.enableGas = enableGas
		self.skipNGasSamples = skipNGasSamples

		sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY, i2c_device)
		sensor.set_humidity_oversample(bme680.OS_8X)
		sensor.set_pressure_oversample(bme680.OS_4X)
		sensor.set_temperature_oversample(bme680.OS_8X)
		sensor.set_filter(bme680.FILTER_SIZE_0)
		if self.enableGas:
			sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
			sensor.set_gas_heater_profile(320, 1000, nb_profile=0)
			sensor.select_gas_heater_profile(0)
		else:
			sensor.set_gas_status(bme680.DISABLE_GAS_MEAS)
		self.sensor=sensor

	def read(self, dynamic=False):
		self.date = datetime.utcnow()
		self.sensor.get_sensor_data()
		if self.enableGas:
			time.sleep(1)
			if self.sensor.data.heat_stable and self.skipNGasSamples > 0:
					self.skipNGasSamples = self.skipNGasSamples - 1

	def getDateTime(self):
		return self.date

	def getDateTimeStr(self):
		return self.getDateTime().isoformat(timespec='seconds').split('+')[0]

	def getTemperature(self):
		return self.sensor.data.temperature

	def getHumidity(self):
		return self.sensor.data.humidity

	def getPressure(self):
		return self.sensor.data.pressure

	def getGasResistance(self):
		if self.enableGas and self.sensor.data.heat_stable and self.skipNGasSamples == 0:
			return round(self.sensor.data.gas_resistance, 1)
		else:
			return None

	def getSummaryInJson(self):
		j = {'measurement': 'bme680',  'time': self.getDateTimeStr(), 'fields': { }}

		if self.getTemperature() != None:
			j['fields'].update({'temperature': self.getTemperature()})

		if self.getHumidity() != None:
			j['fields'].update({'humidity': self.getHumidity()})

		if self.getPressure() != None:
			j['fields'].update({'pressure': self.getPressure()})

		if self.getGasResistance() != None:
			j['fields'].update({'gasResistance': self.getGasResistance()})

		return j

	def close(self):
		logging.debug("Reseting sensor")
		self.sensor.soft_reset()

def _main():
	logging.basicConfig(level=logging.DEBUG)

	sensor = BME680(enableGas=False)
	sensor.read()
	logging.info(sensor.getSummaryInJson())
	time.sleep(5)
	sensor.read()
	logging.info(sensor.getSummaryInJson())
	sensor.close()
	logging.info("Exit")

if __name__ == '__main__':
	_main()





