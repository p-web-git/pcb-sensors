from ltr559 import LTR559 as ltr559
from sensor import Sensor

als_gain_option = [1, 2, 4, 8, 48, 96]


class LTR559(Sensor):
    def __init__(self, i2c_device=None):
        sensor = ltr559(i2c_device)
        sensor.set_light_options(active=True, gain=4)
        sensor.set_light_integration_time_ms(time_ms = 400)
        sensor.set_proximity_active(active=False)
        self.sensor = sensor
        self.tsh_n = 0

    def read(self, dynamic=False):
        self.updateDateTime()
        self.sensor.update_sensor()
        if dynamic:
                (ch0, ch1) = self.rawLight
                if (ch0 > 0xEFFF) or (ch1 > 0xEFFF):
                        if self.tsh_n > 6 or (ch0 == 0xFFFF) or (ch1 == 0xFFFF):
                                if self.sensor.get_gain() != 4:
                                        self.sensor.set_light_options(active=True, gain=4)
                                        self.tsh_n = 0
                        else:
                                self.tsh_n = self.tsh_n + 1
                elif (ch0 < 0x0FFF) and (ch1 < 0x0FFF):
                        if self.tsh_n < -6:
                                if self.sensor.get_gain() != 48:
                                        self.sensor.set_light_options(active=True, gain=48)
                                        self.tsh_n = 0
                        else:
                                self.tsh_n = self.tsh_n - 1
                else:
                        self.tsh_n = round(self.tsh_n / 2, 0)

    @property
    def rawLight(self):
        return self.sensor.get_raw_als(passive=True)

    @property
    def ligth(self):
        return round(self.sensor.get_lux(passive=True), 2)

    def getSummaryInJson(self):
        j = {'measurement': self.name, 'time': self.getDateTimeStr(), 'fields': { }}

        if self.ligth != None:
            j['fields'].update({'lux': self.ligth})

        if self.rawLight != None:
            j['fields'].update({'raw.ch0': self.rawLight[0]})
            j['fields'].update({'raw.ch1': self.rawLight[1]})
            j['fields'].update({'raw.int_time': self.sensor.get_integration_time()})
            j['fields'].update({'raw.gain': self.sensor.get_gain()})

        return j

    def close(self):
        pass

def _main():
	import logging, time
	logging.basicConfig(level=logging.DEBUG)
	sensor = LTR559()

	try:
		while True:
			sensor.read(dynamic=True)
			logging.info(sensor.getSummaryInJson())
			time.sleep(1)
	except KeyboardInterrupt:
		pass

	sensor.close()

if __name__ == '__main__':
	_main()
