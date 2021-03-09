from flask import Flask, request, send_from_directory, redirect
import psycopg2
from dotenv import load_dotenv
import requests

from urllib.parse import urlencode
import os

# load_dotenv()
db = psycopg2.connect('dbname=events host=localhost port=35432 user=docker password=docker')
app = Flask(
    __name__,
    static_folder="web/public",
    static_url_path="/",
    root_path=os.getcwd(),
)

@app.route("/", methods=("GET",))
def home():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/css/<path>", methods=("GET",))
def css(path):
    return send_from_directory(os.path.join(app.static_folder, "css"), path)

@app.route("/js/<path>", methods=("GET",))
def js(path):
    return send_from_directory(os.path.join(app.static_folder, "js"), path)

@app.route("/img/<path>", methods=("GET",))
def img(path):
    return send_from_directory(os.path.join(app.static_folder, "img"), path)

@app.route("/bot-login", methods=("GET",))
def bot_login():
    params = {
        'client_id': os.getenv("DISCORD_CLIENT_ID"),
        'permissions': '51200',
        'scope': 'identify guilds bot',
        'response_type': 'code',
        'redirect_uri': request.host_url + "api/auth/discord",
    }
    url = f'https://discord.com/api/oauth2/authorize?{urlencode(params)}'
    return redirect(url)

@app.route("/api/auth/discord", methods=("GET", "POST"))
def auth():
    error = request.args.get("error")
    err_desc = request.args.get("error_description")
    if error or err_desc:
        # TODO better error
        return """<h1>HAHA discord go bbrrrrrrrr</h1>
                  <p>no but seriously, something is broken</p>"""
    # parse query params to get 'code' and 'guild_id'.
    # This guild_id is used as a database key for events,
    # then redirect to the dashboard.
    guild_id = request.args.get("guild_id")
    code = request.args.get("code")
    permissions = request.args.get("permissions", '0')

    cur = db.cursor()
    cur.execute("""
        INSERT INTO guild (guild_id, code, permissions)
        VALUES (%s, %s, %s)""", (guild_id, code, permissions))
    db.commit()

    rresp = requests.post(
        'https://discord.com/api/oauth2/token',
        data={
            'client_id': os.getenv("DISCORD_CLIENT_ID"),
            'client_secret': os.getenv("DISCORD_SECRET"),
            'grant_type': 'authorization_code',
            'code': 'code',
            'scope': 'identity',
        },
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    )

    resp = redirect('/control-panel')
    resp.set_cookie('discord_code', code)
    resp.set_cookie('guild_id', guild_id)
    return resp

@app.route("/dashboard", methods=("GET",))
def dashboard():
    return '<h1>hello, you made it to the dashboard</h1>'

@app.route("/control-panel", methods=("GET",))
def control_panel():
    return send_from_directory(app.static_folder, 'control-panel.html')

@app.route('/api/test', methods=['GET', 'POST'])
def test_route():
    return {
        'test': 'hello from the http server',
        'app': str(app),
        'config': str(app.config)
    }

@app.route('/api/events/<guild_id>', methods=("GET",))
def list_events(guild_id):
    cur = db.cursor()
    cur.execute("""
        SELECT
            id,
            name,
            date,
            description,
            link
        FROM event
        WHERE guild_id = %s
        LIMIT %s OFFSET %s""", (
            guild_id,
            request.args.get("limit"),
            request.args.get("offset"))
    )
    events = []
    for row in cur.fetchall():
        events.append({
            'id': row[0],
            'name': row[1],
            'date': row[2],
            'description': row[3],
            'link': row[4],
        })
    cur.close()
    print(events)
    if not events:
        return {'error': "no events found"}, 404
    return { 'events': events }, 200


@app.route("/api/event", methods=("POST",))
def create_event():
    if request.json is None:
        return {"error": "bad request"}, 400

    if not request.json['name']:
        return {"error": "no name"}, 400
    elif not request.json['date']:
        return {"error": "no date"}, 400
    elif not request.json['guild_id']:
        return {"error": "no guild id"}, 400

    data = (
        request.json['name'],
        request.json['date'],
        request.json.get('description'),
        request.json.get('link'),
        request.json['guild_id'],
    )
    cur = db.cursor()
    with db.cursor() as cur:
        cur.execute("""
            INSERT INTO event (name, date, description, link, guild_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, name, date, description, link, guild_id
            """, data)
        new = cur.fetchone()
    db.commit()

    return {
        "id": new[0],
        "name": new[1],
        "date": new[2],
        "description": new[3],
        "link": new[4],
        "guild_id": new[5],
    }, 201


@app.route("/api/event/<id>", methods=("GET",))
def get_event(id):
    with db.cursor() as cur:
        cur.execute("""
            SELECT id,name,date,description,link
            FROM event WHERE id = %s""", (id,))
        res = cur.fetchone()
    return {
        "id": res[0],
        "name":res[1],
        "date": res[2],
        "description":res[3],
        "link":res[4],
    }, 200


@app.route("/api/event/<id>", methods=("DELETE",))
def delete_event(id):
    sql_query = 'DELETE FROM event WHERE id = %s'
    cur = db.cursor()
    cur.execute(sql_query, (id,))
    cur.close()
    db.commit()
    return {"status": "deleted object"}, 200


@app.route("/api/event/<id>", methods=("PUT",))
def update_event(id):
    sql_query = 'UPDATE event SET '
    data = []
    if 'name' in request.json:
        sql_query += ' name = %s'
        data.append(request.json['name'])
    if 'date' in request.json:
        sql_query += ' date = %s'
        data.append(request.json['date'])
    if 'description' in request.json:
        sql_query += ' description = %s'
        data.append(request.json['description'])
    if 'link' in request.json:
        sql_query += ' link = %s'
        data.append(request.json['link'])
    sql_query += " WHERE id = %s"
    data.append(id)

    cur = db.cursor()
    cur.execute(sql_query, data)
    new = cur.fetchone()

    db.commit()
    cur.close()
    return {
        "name": new[0],
        "date": new[1],
        "description": new[2],
        "link": new[3],
    }, 200


@app.route('/api/search')
def search_event():
    pass
