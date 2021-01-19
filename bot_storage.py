import io
import csv
from datetime import datetime

from typing import List


class EventlifyEvent:
    def __init__(self, name: str, date: str, description: str, link: str):
        self.name = name
        # this parses the same time format returned my str(date)
        # self.date = datetime.fromisoformat(date)
        self.date = date
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
        csv_reader = csv.reader(f)
        s = ''
        for row in csv_reader:
            s += "EVENT NAME: " + row[0] + \
                "\nEVENT DATE & TIME: " + row[1] + \
                "\nEVENT DESCRIPTION: " + row[2] + \
                "\nEVENT LINK: " + row[3]

        await ctx.send(s)

import textwrap


def event_table(events: List[EventlifyEvent]) -> str:
    return table(
        [(e.name, e.description, str(e.date)) for e in events],
        ('name', 'description', 'date'),
    )

# TODO handle text wrapping
def table(tabledata: list, header: list, max_cell_width=21) -> str:
    chars = '─│┴┬┌┐└┘┼├┤'
    buf = io.StringIO()
    items = [header] + tabledata
    widths = [len(a) for a in items[0]]
    for row in items:
        for i, col in enumerate(row):
            widths[i] = min(max(widths[i], len(col)), max_cell_width)

    total, n, nblanks = len(items), 0, 0
    buf.write('┌' + '┬'.join(('─' * (w + 2)) for w in widths) + '┐\n')
    while items:
        row = items.pop(0)
        for i, col in enumerate(row):
            buf.write('| ')
            if len(col) > widths[i] + 1:
                lines = textwrap.wrap(col, widths[i])
                buf.write(lines.pop(0).ljust(widths[i] + 1))
                while lines:
                    if not items:
                        nblanks += 1
                        n -= 1
                        newrow = [''.ljust(w) for w in widths]
                        newrow[i] = lines.pop(0)
                        items.insert(0, newrow)
                        continue
                    for j in range(i):
                        # if they are all zeros then replace it
                        if all(x == ' ' for x in items[0][j]):
                            items[0][i] = lines.pop(0)
                            break # dont go to the next else
                    else:
                        nblanks += 1
                        n -= 1
                        newrow = [''.ljust(w) for w in widths]
                        newrow[i] = lines.pop(0)
                        items.insert(0, newrow)
            else:
                buf.write(col.ljust(widths[i] + 1))

        buf.write('|\n')
        if nblanks == 0 and n < total - 1:
            buf.write('├' + '┼'.join(('─' * (w + 2)) for w in widths) + '┤\n')
        else:
            nblanks -= 1
        n += 1
    buf.write('└' + '┴'.join(('─' * (w + 2)) for w in widths) + '┘\n')
    return buf.getvalue()


def _table(tabledata: list, header: list, max_cell_width=20) -> str:
    chars = '─│┴┬┌┐└┘┼├┤'
    buf = io.StringIO()
    items = [header] + tabledata

    widths = [len(a) for a in items[0]]
    for row in items:
        for i, col in enumerate(row):
            widths[i] = max(widths[i], len(col))

    buf.write('┌' + '┬'.join(('─' * (w + 2)) for w in widths) + '┐\n')
    for row in items:
        for i, col in enumerate(row):
            buf.write('| ')
            buf.write(col.ljust(widths[i] + 1))
        buf.write('|\n')
    buf.write('└' + '┴'.join(('─' * (w + 2)) for w in widths) + '┘\n')
    return buf.getvalue()
