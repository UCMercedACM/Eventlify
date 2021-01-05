from flask import Flask, send_from_directory, request
import csv
import psycopg2

db = psycopg2.connect('dbname=events host=localhost port=35432 user=docker password=docker')
app = Flask(__name__)

@app.route('/')
def home():
    return send_from_directory("static", 'index.html')

@app.route('/api/test', methods=['GET', 'POST'])
def test_route():
    return {
        'test': 'hello from the http server',
        'app': str(app),
    }

@app.route('/api/events', methods=("GET",))
def list_events():
    events = []
    with open('ACMBOT.csv', 'r') as f:
        r = csv.reader(f)
        next(r) # skip header
        for row in r:
            events.append({
                'name': row[0],
                'date': row[1],
                'description': row[2],
                'link': row[3],
            })
    return {
        'events': events,
    }
