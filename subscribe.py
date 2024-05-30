from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time
import json
import mysql.connector
from mysql.connector import errorcode
import threading

# Define ENDPOINT, CLIENT_ID, PATH_TO_CERT, PATH_TO_KEY, PATH_TO_ROOT, TOPIC
ENDPOINT = "a1yldaxrwpo5ar-ats.iot.us-east-1.amazonaws.com"  # Replace with your AWS IoT endpoint
CLIENT_ID = "EC2_PotRandy"  # Replace with your unique client ID
PATH_TO_CERT = "/home/ubuntu/swe30011/cert/device-cert.crt"  # Replace with the actual path
PATH_TO_KEY = "/home/ubuntu/swe30011/cert/private.pem.key"  # Replace with the actual path
PATH_TO_ROOT = "/home/ubuntu/swe30011/cert/rootcert.pem"  # Replace with the actual path
TOPICS = ["randy/data", "jeff/data", "armann/data"]

# Configure MySQL connection
DB_HOST = "localhost"
DB_USER = "root"  # Replace with your MySQL username
DB_PASSWORD = "123"  # Replace with your MySQL password
DB_NAME = "RPI_DB"

def connect_to_db():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return None

def insert_data(data, table):
    conn = connect_to_db()
    if conn is None:
        return
    cursor = conn.cursor()
    add_reading = (f"INSERT INTO {table} "
                   "(potName, temperature, humidity, light_intensity, moisture_level) "
                   "VALUES (%s, %s, %s, %s, %s)")
    reading_data = (data['potName'], data['temperature'], data['humidity'], data['light_intensity'], data['moisture_level'])
    try:
        cursor.execute(add_reading, reading_data)
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Failed inserting data: {err}")
    cursor.close()
    conn.close()

# Configure the MQTT client
mqtt_client = AWSIoTMQTTClient(CLIENT_ID)
mqtt_client.configureEndpoint(ENDPOINT, 8883)
mqtt_client.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)

# Callback function when a message is received
def on_message(message):
    print(f"Received message from topic {message.topic}: {message.payload}")
    data = json.loads(message.payload)
    table_mapping = {
        "randy/data": "Pot_R",
        "jeff/data": "Pot_J",
        "armann/data": "Pot_A"
    }
    if message.topic in table_mapping:
        insert_data(data, table_mapping[message.topic])

# Configure the MQTT client to call on_message when a message is received
for topic in TOPICS:
    mqtt_client.subscribe(topic, 1, on_message)

mqtt_client.connect()
for topic in TOPICS:
    print(f"Connected to {ENDPOINT} and subscribed to {topic}")
while True:
    time.sleep(1)