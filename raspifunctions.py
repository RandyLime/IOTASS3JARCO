import serial
import mysql.connector
import time  #Import time library
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json

#change to your database!!!    IMPORTANT
DATABASE_HOST = "localhost"
DATABASE_NAME = "sensor_db"
DATABASE_USER = "pi"
DATABASE_PASS = "raspberrypiosha11"

# AWS IoT certificate based connection
myMQTTClient = AWSIoTMQTTClient("myClientID")
# myMQTTClient.configureEndpoint("YOUR.ENDPOINT", 8883)
myMQTTClient.configureEndpoint("a1yldaxrwpo5ar-ats.iot.us-east-1.amazonaws.com", 8883)
myMQTTClient.configureCredentials("/home/pi/cert/rootcert.pem", "/home/pi/cert/private.pem.key", "/home/pi/cert/device-cert.crt")
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

mydb = mysql.connector.connect(host=DATABASE_HOST, user=DATABASE_USER, password=DATABASE_PASS, database=DATABASE_NAME)

#connect and publish
myMQTTClient.connect()

mqtt_override = False

def customCallback(client, userdata, message):
    global mqtt_override
    mqtt_override = True
    print("Received a new message: ")
    print(message.payload)
    try:
        data = json.loads(message.payload)
        cursor = mydb.cursor()
        if 'Led' in data:
            led_status = data['Led']
            sql = "UPDATE Settings SET led_status = %s WHERE id = 1"
            update_status(led_status, None)
            cursor.execute(sql, (led_status,))
        
        if 'Servo Angle' in data:
            servo_status = data['Servo Angle']
            sql = "UPDATE Settings SET servo_status = %s WHERE id = 1"
            update_status(None, servo_status)
            cursor.execute(sql, (servo_status,))

        if 'Reset' in data:
            mqtt_override = False


        arduino.write(send_status())
        mydb.commit()
        cursor.close()

    except json.JSONDecodeError:
        print("Error decoding JSON")

# Subscribe to topics
myMQTTClient.subscribe("randy/control", 1, customCallback)



def publish_to_aws(pot_name, humidity, temperature, light_intensity, moisture_level):
    
    payload = '{\n"potName":'+ pot_name,' + '\n"temperature":' + str(temperature) + ',\n"humidity":' + str(humidity) + ',\n"light_intensity":' + str(light_intensity) + ',\n"moisture_level":' + str(moisture_level) +'\n}'
    print (payload)
    myMQTTClient.publish("randy/data", payload, 0) #change to yourname/data   IMPORANT



arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Adjust the port and baud rate as needed

# Function to parse and insert data into the database
def insert_sensor_data(humidity, temperature, light_intensity, moisture_level):
    cursor = mydb.cursor()

    # Insert the data into the database
    sql = "INSERT INTO sensor_data (humidity, temperature, light_intensity, moisture_level) VALUES (%s, %s, %s, %s)"
    val = (humidity, temperature, light_intensity, moisture_level)
    cursor.execute(sql, val)

    # Commit the transaction
    mydb.commit()
        
    # Close the cursor
    cursor.close()

def send_status():
    cursor = mydb.cursor()
    sql = "SELECT * FROM Settings WHERE id = 1"
    cursor.execute(sql)
    settings = cursor.fetchone()
    status_str = "Led: {}\nServo Angle: {}\n".format(settings[2], settings[3])
    result = status_str.encode('utf-8')
    cursor.close()
    print(result)
    return result

def update_status(led_status=None, servo_status=None):
    cursor = mydb.cursor()
    if led_status is not None:
        sql = "UPDATE Settings SET led_status = %s WHERE id = 1"
        cursor.execute(sql, (led_status,))
    if servo_status is not None:
        sql = "UPDATE Settings SET servo_status = %s WHERE id = 1"
        cursor.execute(sql, (servo_status,))
    mydb.commit()
    cursor.close()

def process_sensor_data(humidity, temperature, light_intensity, moisture_level):
    warnings = 0

    # DHT Sensor
    if temperature < 20:
        warnings += 1
    elif temperature > 28:
        warnings += 1

    if humidity < 50:
        warnings += 1
    elif humidity > 70:
        warnings += 1

    # Soil Moisture Sensor Module
    if moisture_level > 65:
        warnings += 1
    elif moisture_level < 50:
        warnings += 1

    # Light Sensor
    if light_intensity <= 500:
        warnings += 1

    # Traffic light
    if warnings == 0:
        led_status = "Green"
    elif 1 <= warnings <= 3:
        led_status = "Yellow"
    else:
        led_status = "Red"

    # Servo
    if temperature > 28 and moisture_level < 50:
        servo_status = 180
    elif temperature > 28:
        servo_status = 90
    elif moisture_level < 50:
        servo_status = 45
    else:
        servo_status = 0

    update_status(led_status, servo_status)
    arduino.write(send_status())

# Read data from the Arduino and insert into the database
while True:
    data = arduino.readline().decode("utf-8").strip()
    if data:
        print("Received data:", data)  # Print the received data to debug
    

    values = data.split(",")  # Split the data by newline
    if len(values) == 4:
        ahumidity, atemperature, alight_intensity, amoisture_level = values
        print("Humidity:", ahumidity)
        print("Temperature:", atemperature)
        print("Light Intensity:", alight_intensity)
        print("Moisture Level:", amoisture_level) 
        insert_sensor_data(ahumidity, atemperature, alight_intensity, amoisture_level)
        publish_to_aws("R", ahumidity, atemperature, alight_intensity, amoisture_level)
        if not mqtt_override:
            process_sensor_data(float(ahumidity), float(atemperature), int(alight_intensity), int(amoisture_level))
        
    

    time.sleep(3)
