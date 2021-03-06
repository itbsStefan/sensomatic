import json
from   flask import Flask
from   flask import request
from   flask import Response
from   flask import jsonify
import paho.mqtt.client as mqtt

app = Flask(__name__)

devices = [
           {"id":"ansiroom-mainlight",
            "name":"Ansiroom Mainlight",
            "description":"Mainlight ansiroom",
            "actions":["turnOn",
                       "turnOff",
                      ]
           },
           {"id": "kitchen-mainlight",
            "name": "Kitchen Mainlight",
            "description": "Mainlight Kitchen",
            "actions": ["turnOn",
                        "turnOff",
                        ]
            },
           {"id": "table-mainlight",
            "name": "Hackingtable Mainlight",
            "description": "Mainlight Hackingtable",
            "actions": ["turnOn",
                        "turnOff",
                       ]
           },
           {"id": "livingroom-mainlight",
            "name": "Livingroom Mainlight",
            "description": "Mainlight livingroom",
            "actions": ["turnOn",
                        "turnOff",
                        ]
           },
]

actions = ["setTargetTemperature",
           "incrementTargetTemperature",
           "decrementTargetTemperature",
           "setPercentage",
           "incrementPercentage",
           "decrementPercentage",
           "turnOff",
           "turnOn"
          ]

@app.route('/', methods=['GET'])
def Homepage():
    return "Hallo Welt"

@app.route('/api/v1.0/ifttt', methods=['POST'])
def Ifttt():
    with open('passwd.txt', 'r') as myfile:
        passwd = myfile.read().replace('\n', '')
        data = request.get_json(force=True)
        if data['pass'] == passwd:
            if data['command'] == "ansilight":
                mqclient.publish("ansiroom/light/main", "TOGGLE")
            if data['command'] == "tiffylight":
                mqclient.publish("tiffyroom/light/main", "TOGGLE")
        else:
            print "Wrong passwd"
    return "OK"

@app.route('/api/v1.0/discovery', methods=['POST'])
def Discovery():
    with open('passwd.txt', 'r') as myfile:
        passwd = myfile.read().replace('\n', '')
        if passwd == request.form['pass']:
            return Response(json.dumps(devices), mimetype='application/json')
        else:
            return "Wrong Passwd"

@app.route('/api/v1.0/action', methods=['POST'])
def Action():
    with open('passwd.txt', 'r') as myfile:
        passwd = myfile.read().replace('\n', '')
        if passwd == request.form['pass']:
            j = json.loads(request.form['event'])
            #print json.dumps(j, sort_keys=True, indent=4, separators=(',', ': '))
            id = j['payload']['appliance']['applianceId']

            if id == "ansiroom-mainlight":
                print "Ansiraumlich"
                mqclient.publish("ansiroom/light/main", "TOGGLE")

            if id == "kitchen-mainlight":
                print "Kitchenlicht"
                mqclient.publish("kitchen/light/main", "TOGGLE")

            if id == "table-mainlight":
                print "Tablelicht"
                mqclient.publish("hackingroom/light/main", "TOGGLE")

            if id == "livingroom-mainlight":
                print "livingroomlicht"
                mqclient.publish("livingroom/light/main", "TOGGLE")

            return "OK"
        else:
            print "passwd errror"

if __name__ == '__main__':
    mqclient = mqtt.Client("alexa", clean_session = True)
    mqclient.connect("cortex", 1883, 60)
    mqclient.loop_start()
    app.run(debug = False, port = 9001)

