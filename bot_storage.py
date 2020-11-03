import csv
from datetime import datetime


class EventlyEvent:
    def __init__(self, name: str, date: str, description: str, link: str):
        self.name = name
        # this parses the same time format returned my str(date)
        print(date)
        self.date = datetime.fromisoformat(date)
        self.description = description
        self.link = link

    @staticmethod
    def from_csv_reader(reader):
        row = next(reader) 
        return EventlyEvent(row[0], row[1], row[2], row[3])

    def has_passed(self):
        return self.date < datetime.now()


def read_all_events() -> list:
    events = []
    with open('ACMBOT.csv', 'r') as f:
        r = csv.reader(f)
        for row in r:
            events.append(EventlyEvent(row[0], row[1], row[2], row[3]))
    return events


async def list_events(ctx):
    with open('ACMBOT.csv', 'r') as f:
        print(f.read())
    with open('ACMBOT.csv', 'r') as f:
        csv_reader = csv.reader(f)
        s = ''
        for row in csv_reader:
            print(row)
            s += "EVENT NAME: " + row[0] + \
                "\nEVENT DATE & TIME: " + row[1] + \
                "\nEVENT DESCRIPTION: " + row[2] + \
                "\nEVENT LINK: " + row[3]

        await ctx.send(s)
