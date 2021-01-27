from flask import Flask, request, send_from_directory
import psycopg2

db = psycopg2.connect('dbname=events host=localhost port=35432 user=docker password=docker')
app = Flask(__name__)


@app.route('/', methods=("GET",), defaults={'path': None})
@app.route('/<path>', methods=("GET",))
def home(path):
    if not path:
        path = "./index.html"
    return send_from_directory(".", "index.html")


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
