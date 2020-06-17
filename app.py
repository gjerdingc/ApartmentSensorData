from flask import Flask
from flask import Response
from flask import render_template
import Adafruit_DHT
from tinydb import TinyDB, Query
from datetime import datetime
from datetime import timedelta
from dateutil import parser
from pms5003 import PMS5003
import requests


app= Flask(__name__)

#Class for passing data into view
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


DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

pms5003 = PMS5003(
    device='/dev/ttyAMA0',
    baudrate=9600
)

#Prometheus timeseries database
db_url = "http://localhost:9090/api/v1"

@app.route('/')
def index():

    sensordata = Sensordata()

    endTime = datetime.timestamp(datetime.now())
    startTime = datetime.timestamp(datetime.now() - timedelta(hours=48))

    #Query temperaturedata and add it to sensordata object
    data = dbRangeQuery('Temperature', startTime, endTime, 1000)
    sensordata.tempvalues = data['values']
    sensordata.templabels = data['labels']


    #Query humiditydata and add it to sensordata object
    data = dbRangeQuery('Humidity', startTime, endTime, 1000)
    sensordata.humvalues = data['values']
    sensordata.humlabels = data['labels']


    #Query particledata and add it to sensordata object
    #PM1
    data = dbRangeQuery('PM1', startTime, endTime, 1000)
    sensordata.pm1 = data['values']
    sensordata.pmlabels = data['labels']

    #PM2.5
    data = dbRangeQuery('PM2_5', startTime, endTime, 1000)
    sensordata.pm2_5 = data['values']

    #PM10
    data = dbRangeQuery('PM10', startTime, endTime, 1000)
    sensordata.pm10 = data['values']






    #Return view with data
    return render_template('index.html', sensordata = sensordata)



#Returns timestamps and values
def dbRangeQuery(query, startTime, endTime, step):
    queryString = f"{db_url}/query_range?query={query}&start={startTime}&end={endTime}&step={step}s"
    r = requests.get(queryString)
    data = r.json()

    values = []
    labels = []

    for i in data['data']['result'][0]['values']:
        values.append(i[1])
        labels.append(datetime.fromtimestamp(i[0]).strftime("%H:%M"))


    return {'values': values, 'labels': labels}
