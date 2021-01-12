import sys
import os
sys.path.insert(0, os.getcwd())

import pytest
from flask.wrappers import Response
from flask.testing import FlaskClient
from web.app import app, db

# https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages

# Request
"""
POST /api/events HTTP/1.1 \r\n
Content-Type: application/json \r\n
Date: Mon Jan 11 18:07:46 PST 2021 \r\n
Content-Length: 800 \r\n
\r\n
{
    "name":"test event",
    "date": "1903-12-04T11:00:00.000000",
    "description":"this is a test event",
    "link": "https://www.google.com"
}
"""

# Response
"""
HTTP/1.1 200 Ok \r\n
Accept: application/json \r\n
Content-Length: 23
\r\n
{"this": "is the body"}
"""


@pytest.fixture
def client() -> FlaskClient:
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_list_events(client: FlaskClient):
    resp: Response = client.get("/api/events")
    assert resp.status_code == 200
    assert len(resp.json) != 0
    assert 'events' in resp.json
    for e in resp.json['events']:
        assert e is not None
        assert 'name' in e
        assert 'date' in e
        assert 'description' in e
        assert 'link' in e


def test_add_and_delete_events(client: FlaskClient):
    resp: Response = client.post(
        "/api/event",
        json={
            "name":"test event",
            "date": "1903-12-04T11:00:00.000000",
            "description":"this is a test event",
            "link": "https://www.google.com"
        },
        headers={'Content-Type': "application/json"},
    )
    assert resp.headers['content-type'] == 'application/json'
    assert resp.status_code == 201
    assert resp.json
    assert 'id' in resp.json
    event_id = resp.json['id']

    resp: Response = client.delete('/api/event/{}'.format(event_id))

    assert resp.status_code == 200
    assert resp.json['status'] == "deleted object"

    with db.cursor() as cur:
        cur.execute('SELECT id from event where id = %s', (event_id,))
        row = cur.fetchone()
        assert row is None or len(row) == 0
