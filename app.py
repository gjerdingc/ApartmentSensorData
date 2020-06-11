from flask import Flask
from flask import Response
from flask import render_template
import Adafruit_DHT
from tinydb import TinyDB, Query
from datetime import *
from dateutil import parser
from pms5003 import PMS5003


app= Flask(__name__)


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
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    tempvalues = []
    templabels = []
    humvalues = []
    humlabels = []

    datadict = {'pm1':[], 'pm2_5':[], 'pm10':[], 'pmlabels':[]}

    data = pms5003.read()
    pm1 = data.pm_ug_per_m3(1)
    pm2_5 = data.pm_ug_per_m3(2.5)
    pm10 = data.pm_ug_per_m3(10)

    pmlist_now = [pm1, pm2_5, pm10]


    for i in tempdb.all():
        datetime_object = parser.parse(i['date'])

        if datetime_object > (datetime.now() - timedelta(hours=48)):

            tempvalues.append(i['temperature'])
            templabels.append(datetime_object.strftime("%H:%M"))
            humvalues.append(i['humidity'])
            humlabels.append(datetime_object.strftime("%H:%M"))

    for i in particledb.all():
        datetime_object = parser.parse(i['date'])

        if datetime_object > (datetime.now() - timedelta(hours=48)):
            datadict['pm1'].append(i['pm1'])
            datadict['pm2_5'].append(i['pm2_5'])
            datadict['pm10'].append(i['pm10'])
            datadict['pmlabels'].append(datetime_object.strftime("%H:%M"))


    return render_template('index.html', temperature=round(temperature,1), 
                                        humidity=round(humidity,1), 
                                        tempvalues=tempvalues, 
                                        templabels=templabels, 
                                        humvalues=humvalues, 
                                        humlabels=humlabels,
                                        pmlist_now = pmlist_now,
                                        datadict = datadict)