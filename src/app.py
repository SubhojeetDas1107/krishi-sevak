import sys
sys.path.append('../')

from flask import Flask, request, render_template
import json
import requests
import datetime
import pickle
import numpy as np
from funcs import location

app = Flask(__name__)

# GLOBALS: ########################################################################################
MODEL = None

LATITUDE = ''
LONGITUDE = ''
SOIL_TYPE = ''
SOIL_CATEGORY = ''
STATE = ''
PH = 0.0
TEMPERATURE = 0.0
PRECIPITATION = 0.0
HUMIDITY = 0.0
###################################################################################################

def get_soil(state):
    index = {
        ''
    }
    soils = {
        "Andhra Pradesh": ['red', 'alluvial', ],
        "Arunachal Pradesh": ['red', 'mountain', ],
        "Assam": ['laterite', 'alluvial', 'mountain', ],
        "Bihar": ['alluvial', ],
        "Chhattisgarh": ['red', ],
        "Goa": ['alluvial', 'laterite', ],
        "Gujarat": ['alluvial', 'black'],
        "Haryana": ['alluvial', ],
        "Himachal Pradesh": ['mountain', ],
        "Jharkhand": ['alluvial', ],
        "Karnataka": ['red', 'laterite', ],
        "Kerala": ['laterite', ],
        "Madhya Pradesh": ['laterite', ],
        "Maharashtra": ['black'],
        "Manipur": ['red', 'laterite', ],
        "Meghalaya": ['laterite', 'red', ],
        "Mizoram": ['red', ],
        "Nagaland": ['red', ],
        "Odisha": ['laterite', 'red'],
        "Punjab": ['alluvial', ],
        "Rajasthan": ['desert', ],
        "Sikkim": ['mountain', ],
        "Tamil Nadu": ['red', 'laterite', ],
        "Telangana": ['red', 'black'],
        "Tripura": ['red', ],
        "Uttar Pradesh": ['alluvial', ],
        "Uttarakhand": ['mountain', ],
        "West Bengal": ['alluvial', ]
    }
    pH = {
        'Andhra Pradesh': 6.4,
        'Arunachal Pradesh': 5.5,
        'Assam': 5.8,
        'Bihar': 6.5,
        'Chhattisgarh': 6.2,
        'Goa': 6.5,
        'Gujarat': 7.0,
        'Haryana': 8.0,
        'Himachal Pradesh': 6.0,
        'Jharkhand': 6.2,
        'Karnataka': 6.5,
        'Kerala': 6.2,
        'Madhya Pradesh': 6.8,
        'Maharashtra': 6.5,
        'Manipur': 5.8,
        'Meghalaya': 6.5,
        'Mizoram': 6.0,
        'Nagaland': 6.2,
        'Odisha': 6.5,
        'Punjab': 7.0,
        'Rajasthan': 8.5,
        'Sikkim': 5.8,
        'Tamil Nadu': 6.5,
        'Telangana': 6.2,
        'Tripura': 6.5,
        'Uttar Pradesh': 7.0,
        'Uttarakhand': 6.5,
        'West Bengal': 6.2
    }

    return soils[STATE], pH[STATE]



def get_weather():
    start_date = datetime.datetime.now().strftime('%Y-%m-%d')
    end_date = (datetime.datetime.now() + datetime.timedelta(days=16)).strftime('%Y-%m-%d')
    end_pt = f'https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&hourly=temperature_2m,relativehumidity_2m,precipitation&timezone=auto&start_date={start_date}&end_date={end_date}'
    return json.loads(requests.get(end_pt).text)
    


@app.route('/', methods=['GET'])
def main():
    return render_template('index.html')



@app.route('/get_loc/<string:loc>', methods=['POST'])
def get_loc(loc):
    global MODEL, LATITUDE, LONGITUDE, SOIL_TYPE, SOIL_CATEGORY, STATE, PH, TEMPERATURE, PRECIPITATION, HUMIDITY 
    MODEL = pickle.load(open('./machine-learning/model', 'rb'))
    locs = json.loads(loc)
    LATITUDE = locs['latitude']
    LONGITUDE = locs['longitude']
    STATE = location.get_location(LATITUDE, LONGITUDE)[-3].strip()
    weather = get_weather()

    def avg(num):
        num = [item for item in num if item != None and item != 0]
        sum_num = 0
        for t in num:
            sum_num = sum_num + t           
        avg = sum_num / len(num)
        return avg

    TEMPERATURE = avg(weather['hourly']['temperature_2m'])
    HUMIDITY = avg(weather['hourly']['relativehumidity_2m'])
    PRECIPITATION = avg(weather['hourly']['precipitation'])
    SOIL_TYPE, PH = get_soil(STATE)

    print(LATITUDE, LONGITUDE, SOIL_TYPE, SOIL_CATEGORY, STATE, PH, TEMPERATURE, PRECIPITATION, HUMIDITY, datetime.date.today().month)

    print(MODEL.predict([[PH, TEMPERATURE, PRECIPITATION, HUMIDITY, datetime.date.today().month,
                                     0,
                                     1,
                                     0,
                                     0,
                                     0,
                                     1,
                                     0]]))

    return('/')



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, ssl_context='adhoc')