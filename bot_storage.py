import io
import csv
from datetime import datetime

from typing import List


class EventlifyEvent:
    def __init__(self, name: str, date: str, description: str, link: str):
        self.name = name
        # this parses the same time format returned my str(date)
        self.date = datetime.fromisoformat(date)
        #self.dateprintable = self.date.strftime('%Y-%m-%d %H:%M')
        self.dateprintable = str(self.date)
        self.description = description
        self.link = link

    @staticmethod
    def from_csv_reader(reader):
        row = next(reader)
        return EventlifyEvent(row[0], row[1], row[2], row[3])

    def has_passed(self):
        return self.date < datetime.now()


def read_all_events(filename) -> list:
    events = []
    with open(filename, 'r') as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            events.append(EventlifyEvent(row[0], row[1], row[2], row[3]))
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


def event_table(events: List[EventlifyEvent]) -> str:
    buf = io.StringIO()
    namelen = max(len(e.name) for e in events)
    buf.write('┌')
    buf.write('─' * (namelen+2))
    buf.write('┬')
    desclen = max(len(e.description) for e in events)
    buf.write('─' * (desclen+2))
    buf.write('┬')
    # TODO Get max length of dates
    datelen = max(len(str(e.date)) for e in events)
    buf.write('─' * (datelen+2))
    buf.write('┐\n')

    buf.write('| ')
    buf.write('name'.ljust(namelen))
    buf.write(' | ')
    buf.write('description'.ljust(desclen))
    buf.write(' | ')
    buf.write('date'.ljust(datelen))
    buf.write(' |\n')

    for e in events:
        buf.write('| ' + e.name.ljust(namelen) + ' | ')
        buf.write(e.description.ljust(desclen) + ' | ')
        buf.write(str(e.date).ljust(datelen) + ' |\n')
    buf.write('└')
    buf.write('─' * (namelen+2))
    buf.write('┴')
    buf.write('─' * (desclen+2))
    buf.write('┴')
    buf.write('─' * (datelen+2))
    buf.write('┘\n')
    return buf.getvalue()

