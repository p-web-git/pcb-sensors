import logging, sys, signal, smbus, os
import sentry_sdk
from dotenv import find_dotenv, load_dotenv
from periodic_thread import RepeatTimer
from sensorBME680 import BME680
from sensorLTR559 import LTR559
from mqttClient import mqttClient

TIME_PERIOD_S = 60
LIGHT_PERIOD_S = 20

load_dotenv(find_dotenv())

def sensorThread(sensor, client):
	sensor.read(dynamic=True)
	dt = sensor.getSummaryInJson()
	client.sendObj(obj=dt['fields'])


def terminate(signum, frame):
	logging.debug('\nSignal captured...')
	tt.cancel()
	lt.cancel()

## Main Starts Here ##

sentry_sdk.init(
    os.getenv('SENTRY_SENSORS'),
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)

logging.basicConfig(format='%(levelname)-8s %(message)s', level=logging.INFO)
logging.info('Starting')

mqttBME = mqttClient('sensor/room/BME680')
mqttLTR = mqttClient('sensor/room/LTR559')

i2c = smbus.SMBus(1)
bme = BME680(enableGas=True, skipNGasSamples=5, i2c_device=i2c)
ltr = LTR559(i2c_device=i2c)

bme.read()
ltr.read()

tt = RepeatTimer(TIME_PERIOD_S, sensorThread, args=(bme, mqttBME))
lt = RepeatTimer(LIGHT_PERIOD_S, sensorThread, args=(ltr, mqttLTR))

for sig in [signal.SIGTERM, signal.SIGINT]:
        signal.signal(sig, terminate)

tt.start()
lt.start()

tt.join()
lt.join()

bme.close()
ltr.close()
i2c.close()
mqttBME.close()
mqttLTR.close()

logging.info('Exit')
