from flask import Flask
from flask import Response
from flask import render_template
from datetime import datetime
from datetime import timedelta
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


#Prometheus timeseries database
db_url = "http://localhost:9090/api/v1"

@app.route('/')
def index():

    sensordata = Sensordata()

    endTime = datetime.timestamp(datetime.now())
    startTime = datetime.timestamp(datetime.now() - timedelta(days=7))

    #Query temperaturedata and add it to sensordata object
    #data for graph
    data = dbRangeQuery('Temperature', startTime, endTime, 1000)
    sensordata.tempvalues = data['values']
    sensordata.templabels = data['labels']
    #Current value
    sensordata.temperature_now = dbInstantQuery('Temperature')


    #Query humiditydata and add it to sensordata object
    #data for graph
    data = dbRangeQuery('Humidity', startTime, endTime, 1000)
    sensordata.humvalues = data['values']
    sensordata.humlabels = data['labels']
    #Current value
    sensordata.humidity_now = dbInstantQuery('Humidity')


    #Query particledata and add it to sensordata object
    #PM1 data for graph
    data = dbRangeQuery('PM1', startTime, endTime, 1000)
    sensordata.pm1 = data['values']
    sensordata.pmlabels = data['labels']
    #Current value
    sensordata.pm1_now = dbInstantQuery('PM1')

    #PM2.5 data for graph
    data = dbRangeQuery('PM2_5', startTime, endTime, 1000)
    sensordata.pm2_5 = data['values']
    #Current value
    sensordata.pm2_5_now = dbInstantQuery('PM2_5')

    #PM10 data for graph
    data = dbRangeQuery('PM10', startTime, endTime, 1000)
    sensordata.pm10 = data['values']
    #Current value
    sensordata.pm10_now = dbInstantQuery('PM10')
    

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
        labels.append(datetime.fromtimestamp(i[0]).strftime("%d %b %H:%M"))


    return {'values': values, 'labels': labels}


def dbInstantQuery(query):
    queryString = f"{db_url}/query?query={query}"
    r = requests.get(queryString)
    data = r.json()

    value = data['data']['result'][0]['value'][1]

    return value

