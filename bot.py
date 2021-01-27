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
from discord.ext.commands.context import Context
import DiscordUtils

from bot_storage import EventlifyEvent, event_table, list_events, read_all_events


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# client = discord.Client()

bot = commands.Bot(command_prefix='e!')
session = None # initialized on bot ready
API_HOST = 'http://localhost:5000'

class EventChecker(commands.Cog):
    def __init__(self):
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=30.0)
    async def printer(self):
        # read all events and store in list events
        return


# On load of the Bot
@bot.event
async def on_ready():
    global session
    session = aiohttp.ClientSession()
    print(f'{bot.user.name} has connected to Discord!')

#List events
@bot.command(name='list', help='List all the events')
async def list_events_cmd(ctx: Context, arg=None):
    print(f'listing events to "{ctx.guild}"')

    resp = await session.get(f"{API_HOST}/api/events/{ctx.message.guild.id}")
    if resp.status != 200:
        await ctx.send("something is broken, silly developers")
        return
    eventresp = await resp.json()
    events = [
        EventlifyEvent(e['name'], e['date'], e['description'], e['link'])
        for e in eventresp['events']
    ]

    if arg == '--ascii':
        return await ctx.send(f'```\n{event_table(events)}\n```')

    embeds = []
    embedded = None
    page_size = 5

    for i, e in enumerate(events):
        if i % page_size == 0:
            embedded = discord.Embed(
                title='Events',
                description='',
                color=0x00ff00,
                type='rich'
            )
        embedded.add_field(name="Event", value = f'[{e.name}]({e.link})', inline=True)
        embedded.add_field(name="Date", value = e.dateprintable, inline=True)
        embedded.add_field(name="Description", value = e.description, inline=True)
        if i < (len(events)-1):
            embedded.add_field(name="\u200B", value = "\u200B", inline=False)

        if i % page_size == 0:
            embeds.append(embedded)

    #msg = await ctx.send(embed=embedded)
    paginator = DiscordUtils.Pagination.AutoEmbedPaginator(ctx, timeout=120, auto_footer=True, remove_reactions=True)
    await paginator.run(embeds)
    #await msg.add_reaction('\U00002B05')
    #await msg.add_reaction('\U000027A1')


# Add event
@bot.command(name='add', help='Add an event. Format: Year-Month-Day Hour:Minute AM/PM')
async def add_event_cmd(ctx, name, date, description, link):
    print('adding event')
    #date = datetime.strptime(arg2, '%Y-%m-%d')
    date = datetime.strptime(date, '%Y-%m-%d %I:%M %p')
    resp = await session.post(
        f"{API_HOST}/api/event",
        headers={'Content-Type': "application/json"},
        json={
            'name': name,
            'date': str(date),
            'description': description,
            'link': link,
            'guild_id': ctx.message.guild.id,
        },
    )
    if resp.status == 201:
        msg = discord.Embed(
            title='Events',
            description='',
            color=0x00ff00,
            type='rich'
        )
        msg.add_field(name="Success", value='Event added successfully')
        await ctx.send(embed=msg)
    elif resp.status >= 300:
        print('error:', await resp.json())
        await ctx.send("Something has gone terribly wrong :(")


# Remove event
@bot.command(name='remove', help='Remove an event, must use exact name')
async def remove_event_cmd(ctx, name):
    # TODO do this
    # ctx.send("not implemented")
    # resp = await session.delete(API_HOST + f'/api/event/',)
    await ctx.send("You are not allowed to do this >:(")


# Convert Parameters Automatically
@bot.command(name='roll_dice', help='Simulates rolling dice.')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

@bot.command(name="test")
async def test(ctx: Context):
    print(type(ctx.guild))
    print(dir(ctx.guild))
    print(ctx.guild.id)
    await ctx.send(ctx.message.guild.id)


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
        # Prints out the error traceback
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
