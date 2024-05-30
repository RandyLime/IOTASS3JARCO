from flask import Flask, render_template
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import mysql.connector
import json

app = Flask(__name__)

# Database connection details (replace with your actual values)
DATABASE_HOST = "localhost"
DATABASE_NAME = "RPI_DB"
DATABASE_USER = "root"
DATABASE_PASSWORD = "123"

ENDPOINT = "a1yldaxrwpo5ar-ats.iot.us-east-1.amazonaws.com"  # Replace with your AWS IoT endpoint
CLIENT_ID = "EC2_PotRandy"  # Replace with your unique client ID
PATH_TO_CERT = "/home/ubuntu/swe30011/cert/device-cert.crt"  # Replace with the actual path
PATH_TO_KEY = "/home/ubuntu/swe30011/cert/private.pem.key"  # Replace with the actual path
PATH_TO_ROOT = "/home/ubuntu/swe30011/cert/rootcert.pem"  # Replace with the actual path



@app.route('/')
def index():
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host=DATABASE_HOST,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            database=DATABASE_NAME
        )

        if connection.is_connected():
            cursor = connection.cursor()
            # Fetch data from all tables (modify for specific table selection)
            sql = "(SELECT * FROM Pot_A ORDER BY id DESC LIMIT 6) UNION ALL (SELECT * FROM Pot_J ORDER BY id DESC LIMIT 6) UNION ALL (SELECT * FROM Pot_R ORDER BY id DESC LIMIT 6)"
            cursor.execute(sql)
            data = cursor.fetchall()
            cursor.close()
            connection.close()
            
            return render_template('index.html', data=data)
            
        else:
            return "Failed to connect to database"

    except Exception as e:
        error_message = "Error while connecting to MySQL: {}".format(e)
        print(error_message)
        return error_message

@app.route('/<action>')
def act(action):

    mqtt_client = AWSIoTMQTTClient(CLIENT_ID)
    mqtt_client.configureEndpoint(ENDPOINT, 8883)
    mqtt_client.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)



    def publish_to_aws(topic, status_type, status_value):
        payload_str = json.dumps({status_type: status_value})
        myMQTTClient.connect()
        myMQTTClient.publish(topic, payload_str, 0)
    
    topic_mapping = {
        'Aaction1': ('armann/control', 'Servo Angle', '90'),
        'Aaction2': ('armann/control', 'Servo Angle', '45'),
        'Aaction3': ('armann/control', 'Servo Angle', '180'),
        'Aaction4': ('armann/control', 'Servo Angle', '0'),
        'Aledgreen': ('armann/control', 'Led', 'Green'),
        'Aledyellow': ('armann/control', 'Led', 'Yellow'),
        'Aledred': ('armann/control', 'Led', 'Red'),
        'Areset': ('armann/control', 'Reset', 'reset'),
        'Jaction1': ('jeff/control', 'Servo Angle', '90'),
        'Jaction2': ('jeff/control', 'Servo Angle', '45'),
        'Jaction3': ('jeff/control', 'Servo Angle', '180'),
        'Jaction4': ('jeff/control', 'Servo Angle', '0'),
        'Jledgreen': ('jeff/control', 'Led', 'Green'),
        'Jledyellow': ('jeff/control', 'Led', 'Yellow'),
        'Jledred': ('jeff/control', 'Led', 'Red'),
        'Jreset': ('jeff/control', 'Reset', 'reset'),
        'Raction1': ('randy/control', 'Servo Angle', '90'),
        'Raction2': ('randy/control', 'Servo Angle', '45'),
        'Raction3': ('randy/control', 'Servo Angle', '180'),
        'Raction4': ('randy/control', 'Servo Angle', '0'),
        'Rledgreen': ('randy/control', 'Led', 'Green'),
        'Rledyellow': ('randy/control', 'Led', 'Yellow'),
        'Rledred': ('randy/control', 'Led', 'Red'),
        'Rreset': ('randy/control', 'Reset', 'reset')
    }

    if action in topic_mapping:
        topic, status_type, status_value = topic_mapping[action]
        publish_to_aws(topic, status_type, status_value)
    
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host=DATABASE_HOST,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            database=DATABASE_NAME
        )

        if connection.is_connected():
            cursor = connection.cursor()
            # Fetch data from all tables (modify for specific table selection)
            sql = "(SELECT * FROM Pot_A ORDER BY id DESC LIMIT 6) UNION ALL (SELECT * FROM Pot_J ORDER BY id DESC LIMIT 6) UNION ALL (SELECT * FROM Pot_R ORDER BY id DESC LIMIT 6)"
            cursor.execute(sql)
            data = cursor.fetchall()
            cursor.close()
            connection.close()
            
            return render_template('index.html', data=data)
            
        else:
            return "Failed to connect to database"

    except Exception as e:
        error_message = "Error while connecting to MySQL: {}".format(e)
        print(error_message)
        return error_message


if __name__ == "__main__":
    app.run()
