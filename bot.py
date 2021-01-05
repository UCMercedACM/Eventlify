import os
import random
import csv
from datetime import datetime
import traceback

import aiohttp
from aiohttp import web
import discord
from dotenv import load_dotenv
from discord.ext import commands, tasks

from bot_storage import EventlifyEvent, event_table, list_events, read_all_events

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

bot = commands.Bot(command_prefix='e!')

session = None

# Detecting when someone joins the server
# Utility Functions running on boot up
@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

# Welcoming new members
@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to ACM UCM server!'
    )

# Responding to Messages
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    if message.content == '99!':
        response = random.choice(brooklyn_99_quotes)
        await message.channel.send(response)
    elif message.content == 'print events':
        print('sending all events')
        list_events(message)
    elif 'happy birthday' in message.content.lower():
        await message.channel.send('Happy Birthday! 🎈🎉')
    elif message.content == 'raise-exception':
        raise discord.DiscordException


class EventChecker(commands.Cog):
    def __init__(self):
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=15.0)
    async def printer(self):
        # read all events and store in list events
        return
        events = read_all_events('ACMBOT.csv')
        # check event dates
        for event in events:
            if event.date < datetime.now():
                # TODO send notification
                print("Removed event " + event.name)
                events.remove(event)
        # write events back to the file
        with open('ACMBOT.csv', 'w') as f:
            w = csv.writer(f)
            for e in events:
                w.writerows([e.name, e.date.isoformat(), e.description, e.link])


# Error handling
@client.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise Exception

# On load of the Bot
@bot.event
async def on_ready():
    global session
    session = aiohttp.ClientSession()
    print(f'{bot.user.name} has connected to Discord!')

    resp = await session.get("http://localhost:5000/api/test")
    j = await resp.json()
    print(j)

# Bot prefix + command
@bot.command(name='99', help='Responds with a random quote from Brooklyn 99')
async def nine_nine(ctx):
    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    response = random.choice(brooklyn_99_quotes)
    await ctx.send(response)


@bot.command(name='list', help='List all the events')
async def list_events_cmd(ctx, arg=None):
    print('listing events')

    resp = await session.get("http://localhost:5000/api/events")
    eventresp = await resp.json()
    events = [
        EventlifyEvent(e['name'], e['date'], e['description'], e['link'])
        for e in eventresp['events']
    ]

    if arg == '--ascii':
        return await ctx.send(f'```\n{event_table(events)}\n```')

    embedded = discord.Embed(
        title='Events',
        description='',
        color=0x00ff00,
        type='rich'
    )
    for i, e in enumerate(events):
        embedded.add_field(name="Event", value = f'[{e.name}]({e.link})', inline=True)
        embedded.add_field(name="Date", value = e.dateprintable, inline=True)
        embedded.add_field(name="Description", value = e.description, inline=True)
        if i < (len(events)-1):
            embedded.add_field(name="\u200B", value = "\u200B", inline=False)
    await ctx.send(embed=embedded)

# Add event
@bot.command(name='add', help='Add an event. Format: #Year-#Month-#Day Hour:Minute AM/PM')
async def add_event_cmd(ctx, arg1, arg2, arg3, arg4, arg5):
    name = arg1
    date = datetime.datetime.strptime(arg2, '%Y-%m-%d %I:%M%p')
    description = arg3
    link = arg4
    row = [name, date, description, link]
    with open('ACMBOT.csv', 'a') as f:
            w = csv.writer(f)
            w.writerows(row)

# Remove event
@bot.command(name='remove', help='Remove an event, must use exact name')
async def remove_event_cmd(ctx, args):
    name = args
    with open('ACMBOT.csv', 'rb') as read, open('ACMBOT_edit.csv', 'wb') as write:
        r = csv.reader(read)
        w = csv.writer(write)
        for e in r:
            if e.name != args:
                w.writerow(e)




# Convert Parameters Automatically
@bot.command(name='roll_dice', help='Simulates rolling dice.')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))


# Create Channel Command
@bot.command(name='create-channel')
@commands.has_role('admin')
async def create_channel(ctx, channel_name='real-python'):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)


# Bot Errors
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
    else:
        tb = traceback.extract_tb(error.original.__traceback__)
        if len(tb) == 0:
            print('Error:', error, error.original)
        else:
            trace = traceback.format_tb(error.original.__traceback__)
            print('\n'.join(trace))
            print(error.original)


if __name__ == '__main__':
    bot.add_cog(EventChecker())
    bot.run(TOKEN)
