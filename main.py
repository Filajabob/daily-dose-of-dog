import json
import datetime
import os
import random
from threading import Thread
import time
import asyncio

import pytz
import discord
from discord.ext import commands

TOKEN = "OTkxMTUyODQ2NDIwNTk0Nzk5.GQfS8M.3coCLcwY90wbnSWbE2o0juv6jOhHHvO_K9bCuY"
EST = pytz.timezone("America/New_York")

subscribed_channels = [991166247616131083]

client = commands.Bot(command_prefix="d!")


async def send_to_subscribers(text=None, file=None):
    with open("assets/users/subscribers.json", 'r') as f:
        subscribers = json.load(f)

    for subscriber in subscribers:
        user = await client.fetch_user(subscriber)
        await user.send(text, file=file)

    for channel in subscribed_channels:
        channel = await client.fetch_channel(channel)
        await channel.send(text, file=file)


async def post():
    if datetime.datetime.now(EST).time() >= datetime.time(10):
        print("heelo")
        images = os.listdir("assets/images")

        if not images:
            await send_to_subscribers("we ran out of doggos, no dogs today")
            return

        image = random.choice(images)

        with open(f"assets/images/{image}", 'rb') as f:
            image = discord.File(f)

        with open("assets/misc/total_doses.txt", 'r+') as f:
            total_doses = int(f.read())
            f.seek(0)
            f.write(str(total_doses + 1))

        await send_to_subscribers(f"daily dose of dog #{total_doses + 1}", image)

        return True
    else:
        return False



async def run_posting():
    posted = False

    while not posted:
        posted = post()
        time.sleep(1)


@client.command()
async def help(ctx):
    em = discord.Embed(title="Help", description="Command prefix: d!")
    em.add_field(name="subscribe", value="Subscribe to daily dog photos")
    em.add_field(name="unsubscribe", value="Unsubscribe from daily dog photos")


@client.event
async def on_ready():
    print("Ready.")
    Thread(target=asyncio.run_coroutine_threadsafe(client.loop, run_posting)).start()


@client.command()
async def subscribe(ctx):
    with open("assets/users/subscribers.json", 'r+') as f:
        subscribers = json.load(f)

        if ctx.author.id not in subscribers:
            subscribers.append(ctx.author.id)
            await ctx.reply("You have been subscribed to Daily Dose of Dog!")
        else:
            await ctx.reply("You are already subscribed!")


@client.command()
async def next_dose(ctx):
    today = datetime.datetime.now()
    dt = datetime.datetime(today.year, today.month, today.day, POST)


client.run(TOKEN)
