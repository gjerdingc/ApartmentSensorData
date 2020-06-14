from flask import Flask
from flask import Response
from flask import render_template
import Adafruit_DHT
from tinydb import TinyDB, Query
from datetime import *
from dateutil import parser
from pms5003 import PMS5003


app= Flask(__name__)

class Sensordata:
    def __init__(self):

        self.temperature_now = ''
        self.humidity_now = ''
        self.pm1_now = ''
        self.pm2_5_now = ''
        self.pm10_now = ''

        self.tempvalues = []
        self.templabels = []
        self.humvalues = []
        self.humlabels = []
        self.pm1 = []
        self.pm2_5 = []
        self.pm10 = []
        self.pmlabels = []

sensordata = Sensordata()

tempdb = TinyDB('/home/pi/bin/dht22db.json')
particledb = TinyDB('/home/pi/bin/database/pms5003db.json')


DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

pms5003 = PMS5003(
    device='/dev/ttyAMA0',
    baudrate=9600
)

@app.route('/')
def index():
    try:
        sensordata.humidity_now, sensordata.temperature_now = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        sensordata.humidity_now = round(sensordata.humidity_now, 1)
        sensordata.temperature_now = round(sensordata.temperature_now, 1)
    except:
        humidity = 'Sensor offline'
        temperature = 'Sensor offline'

    try:
        data = pms5003.read()
        sensordata.pm1_now = data.pm_ug_per_m3(1)
        sensordata.pm2_5_now = data.pm_ug_per_m3(2.5)
        sensordata.pm10_now = data.pm_ug_per_m3(10)

    except:
        sensordata.pm1_now = "Sensor offline"
        sensordata.pm2_5_now = "Sensor offline"
        sensordata.pm10_now = "Sensor offline"

    for i in tempdb.all():
        datetime_object = parser.parse(i['date'])

        if datetime_object > (datetime.now() - timedelta(hours=48)):

            sensordata.tempvalues.append(i['temperature'])
            sensordata.templabels.append(datetime_object.strftime("%H:%M"))
            sensordata.humvalues.append(i['humidity'])
            sensordata.humlabels.append(datetime_object.strftime("%H:%M"))

    for i in particledb.all():
        datetime_object = parser.parse(i['date'])

        if datetime_object > (datetime.now() - timedelta(hours=48)):
            sensordata.pm1.append(i['pm1'])
            sensordata.pm2_5.append(i['pm2_5'])
            sensordata.pm10.append(i['pm10'])
            sensordata.pmlabels.append(datetime_object.strftime("%H:%M"))


    return render_template('index.html', sensordata = sensordata)