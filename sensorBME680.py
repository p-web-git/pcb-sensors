import logging, time, bme680
from sensor import Sensor

class BME680(Sensor):
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
		self.updateDateTime()
		self.sensor.get_sensor_data()
		if self.enableGas:
			time.sleep(1)
			if self.sensor.data.heat_stable and self.skipNGasSamples > 0:
					self.skipNGasSamples = self.skipNGasSamples - 1
	@property
	def temperature(self):
		return self.sensor.data.temperature

	@property
	def humidity(self):
		return self.sensor.data.humidity

	@property
	def pressure(self):
		return self.sensor.data.pressure

	@property
	def gasResistance(self):
		if self.enableGas and self.sensor.data.heat_stable and self.skipNGasSamples == 0:
			return round(self.sensor.data.gas_resistance, 1)
		else:
			return None

	def getSummaryInJson(self):
		j = {'measurement': self.name, 'time': self.getDateTimeStr(), 'fields': { }}

		if self.temperature != None:
			j['fields'].update({'temperature': self.temperature})

		if self.humidity != None:
			j['fields'].update({'humidity': self.humidity})

		if self.pressure != None:
			j['fields'].update({'pressure': self.pressure})

		if self.gasResistance != None:
			j['fields'].update({'gasResistance': self.gasResistance})

		return j

	def close(self):
		logging.debug("Reseting sensor")
		self.sensor.soft_reset()

def _main():
	import time
	logging.basicConfig(level=logging.DEBUG)

	sensor = BME680(enableGas=False)

	try:
		while True:
			sensor.read()
			logging.info(sensor.getSummaryInJson())
			time.sleep(5)
	except KeyboardInterrupt:
		pass

	sensor.close()
	logging.info("Exit")

if __name__ == '__main__':
	_main()





