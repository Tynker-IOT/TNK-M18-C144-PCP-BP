from flask import Flask, render_template, request, jsonify, redirect
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt

app = Flask(__name__)

thresholds = {
            'calories': 1500
        }

mqtt_broker_ip = "broker.emqx.io" 

sensorData = {}
burnedCalories = 0
lastStepCount = 0

def on_message(client, userdata, msg):
    global sensorData
    topic = msg.topic
    payload = msg.payload.decode('utf-8')
    sensorData[topic] = payload


mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(mqtt_broker_ip, 1883, 60)
mqtt_client.subscribe("/Temperature")
mqtt_client.subscribe("/Humidity")
mqtt_client.subscribe("/Steps")
mqtt_client.loop_start()


@app.route('/')
def index():
    global thresholds
    return render_template('index2.html', thresholds=thresholds)

@app.route("/getSensorData", methods=['POST'])
def getSensorData():
    global burnedCalories, lastStepCount

    if(sensorData):
        newStepCount = int(float(sensorData['/Steps']))
        newSteps = int(newStepCount - lastStepCount)
        if(newSteps):
            newSteps = newStepCount - lastStepCount  
            temp = float(sensorData['/Temperature'] ) 
            hum = float(sensorData['/Humidity']  )
            lux = float(sensorData['/Lux']  )
            
            calories = newSteps *(0.5 + temp/2000 + hum/2000) + (newSteps * 0.01 if lux > 2000 else newSteps * 0.005)
            burnedCalories = burnedCalories + calories
            sensorData['burnedCalories'] = int(burnedCalories)
            
            lastStepCount = newStepCount
    return jsonify(sensorData)

@app.route('/setThresholds', methods=['POST'])
def set_thresholds():
    global thresholds
    if request.method == 'POST':
        calories = request.form.get('calories')

        thresholds = {
            'calories': calories
        }
        return redirect("/")
    
if __name__ == '__main__':
    app.run(debug=True)
