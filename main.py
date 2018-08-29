from flask import Flask
app = Flask(__name__)

import mysql.connector
import threading
import requests
import json
from datetime import datetime, timedelta
import dateutil.parser
import mysql.connector


class ThreadJob(threading.Thread):
    def __init__(self,callback,event,interval):
        '''runs the callback function after interval seconds

        :param callback:  callback function to invoke
        :param event: external event for controlling the update operation
        :param interval: time in seconds after which are required to fire the callback
        :type callback: function
        :type interval: int
        '''
        self.callback = callback
        self.event = event
        self.interval = interval
        super(ThreadJob,self).__init__()

    def run(self):
        while not self.event.wait(self.interval):
            self.callback()


event = threading.Event()

import mysql.connector

mydb = mysql.connector.connect(
  host="grp-epaps.mysql.database.azure.com",
  user="admin-epaps@grp-epaps",
  passwd="MaquetteWeb2017",
  database="recuperationparking"
)
mycursor = mydb.cursor()

url="https://opendata.saemes.fr/api/records/1.0/search/?dataset=places-disponibles-parkings-saemes&sort=nom_parking&facet=date&facet=nom_parking&facet=type_de_parc&facet=horaires_d_acces_au_public_pour_les_usagers_non_abonnes&facet=countertype&facet=counterfreeplaces&refine.nom_parking=Parking+Maubert+Collège+des+Bernardins"
def getLatestValue():
    responseBytes = requests.get(url).content
    responseString = responseBytes.decode('utf-8')
    responseJSON= json.loads(responseString)
    counterfreeplaces = responseJSON["records"][0]["fields"]["counterfreeplaces"]
    date = responseJSON["records"][0]["fields"]["date"]
    date = dateutil.parser.parse(date)
    date= date + timedelta(hours=2)
    message=str(date)+";"+str(counterfreeplaces)+"\n"
    sql = "INSERT INTO parkingsvalues (date, valeur) VALUES (%s, %s)"
    val = (date, counterfreeplaces)
    mycursor.execute(sql, val)
    mydb.commit()
    print(message)
    
k = ThreadJob(getLatestValue,event,5*60)
k.start()



@app.route('/')
def hello_world():
  return "ça marche!"

if __name__ == '__main__':
  app.run()

  
