# Eventlify

Discord Events Bot

## Setup

Install packages -> `pipenv sync`

Access shell -> `pipenv shell`

Start Bot -> `python bot.py`

## API

**GET** `/api/events<guild id>`

List all events for the discord server given the discord server (guild) ID.

**GET** `/api/event/<id>`

Get a spesific event by passing its ID.

**DELETE** `/api/event/<id>`

Delete an event given its ID.

**PUT** `/api/event/<id>`

Update an event given its ID.

**POST** `/api/event`

Create a new event.

Body example:

```json
{
    "name": "Test Event",
    "date": "",
    "description": "This is just a test event for documentation.",
    "link": "https://www.google.com/",
    "guild_id": 11111
}
```
