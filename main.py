import json
import datetime
import os
import random
import time
import asyncio

from app import run

import pause
import pytz
import discord
from discord.ext import commands, tasks

TOKEN = os.getenv("TOKEN")  # For Replit only

EST = pytz.timezone("America/New_York")
POST_TIME = (7, 0, 0)

subscribed_channels = [991166247616131083]
client = commands.Bot(command_prefix="d!")

admin = None


async def send_to_subscribers(text=None, filepath=None, plug_subscription=False, *, embed=None):
    await client.wait_until_ready()

    with open("assets/users/subscribers.json", 'r') as f:
        subscribers = json.load(f)

    if text:
        for subscriber in subscribers:
            file = discord.File(filepath)

            user = await client.fetch_user(subscriber)
            await user.send(text, file=file)

        for channel in subscribed_channels:
            file = discord.File(filepath)

            channel = await client.fetch_channel(channel)
            await channel.send(text, file=file)

            if plug_subscription and random.randint(1, 4) == 1:
                await channel.send("Want doggos in your DMs? Subscribe for FREE by using the d!subscribe command. "
                                   "Unsubscribe anytime the doggos get too cute. (d!unsubscribe)")

    elif embed:
        for subscriber in subscribers:
            user = await client.fetch_user(subscriber)
            await user.send(embed=embed)

        for channel in subscribed_channels:
            channel = await client.fetch_channel(channel)
            await channel.send(embed=embed)

            if plug_subscription and random.randint(1, 4) == 1:
                await channel.send("Want doggos in your DMs? Subscribe for FREE by using the d!subscribe command. "
                                   "Unsubscribe anytime the doggos get too cute. (d!unsubscribe)")


async def post():
    if datetime.time(POST_TIME[0], POST_TIME[1], POST_TIME[2] + 5) >= \
            datetime.datetime.now(EST).time() >= datetime.time(*POST_TIME):
        images = os.listdir("assets/images")

        if len(images) < 3 and len(images) != 0:
            await admin.send(f"We have {len(images)} images left. TAKE MORE PICTURES")

        if not images:
            await send_to_subscribers("we ran out of doggos, no dogs today")
            await admin.send("WE ARE OUT OF IMAGES")

            return True

        with open("assets/misc/total_doses.txt", 'r+') as f:
            total_doses = int(f.read())
            f.seek(0)
            f.write(str(total_doses + 1))

        image_name = random.choice(images)

        await send_to_subscribers(f"daily dose of dog #{total_doses + 1}",
                                  filepath=f"assets/images/{image_name}")

        await asyncio.sleep(7)

        os.remove(f"assets/images/{image_name}")

        return True
    else:
        return False


async def run_posting():
    posted = False

    while True:
        while not posted:
            posted = await post()
            await asyncio.sleep(1)

        pause.until(datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1),
                                              datetime.datetime.min.time()))


@client.event
async def on_ready():
    print("Ready.")

    global admin
    admin = await client.fetch_user(813548110193754134)

    await update_next_dosage_time.start()
    await run_posting()


@tasks.loop(minutes=10)
async def update_next_dosage_time():
    # Daily dosage already happened today
    if datetime.datetime.now(tz=EST).time() > datetime.time(7, tzinfo=EST):
        now = datetime.datetime.now(tz=EST)

        dt = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1),
                                       datetime.time(7, tzinfo=EST), tzinfo=EST) - \
             datetime.datetime.combine(datetime.date.today(), now.time(), tzinfo=EST)

        await client.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching,
                                      name=f"the next dosage in {round(dt.days * 24 + dt.seconds / 3600)} hours"))

    # Daily dosage will happen today
    else:
        now = datetime.time(tzinfo=EST)
        dt = datetime.datetime.combine(datetime.date.today(), datetime.time(7, tzinfo=EST), tzinfo=EST) - \
             datetime.datetime.combine(datetime.date.today(), now.time(), tzinfo=EST)

        await client.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching,
                                      name=f"the next dosage in {round(dt.days * 24 + dt.seconds / 3600)} hours"))


@client.command()
async def subscribe(ctx):
    with open("assets/users/subscribers.json", 'r+') as f:
        subscribers = json.load(f)

        if ctx.author.id not in subscribers:
            subscribers.append(ctx.author.id)
            await ctx.reply("You have been subscribed to Daily Dose of Dog!")
        else:
            await ctx.reply("You are already subscribed!")

        f.seek(0)
        json.dump(subscribers, f)
        f.truncate()


@client.command()
async def unsubscribe(ctx):
    with open("assets/users/subscribers.json", 'r+') as f:
        subscribers = json.load(f)

        if ctx.author.id in subscribers:
            subscribers.remove(ctx.author.id)
            await ctx.reply("You have been unsubscribed from the Daily Dose of Dog.")
        else:
            await ctx.reply("You are not subscribed!")

        f.seek(0)
        json.dump(subscribers, f)
        f.truncate()


@client.command()
async def upload(ctx):
    if ctx.author.id not in (813548110193754134, 813544462831190026):
        await ctx.reply("You can't do that!")
        return

    if not ctx.message.attachments:
        await ctx.reply("Images not detected: attach image(s) to the message when running the command.")
        return

    i = 0

    for attachment in ctx.message.attachments:
        await attachment.save(f"assets/images/{time.strftime('%m_%d_%Y %H_%M_%S')} {i}.png")
        i += 1

    await ctx.reply("Image(s) saved successfully.")


run()
client.run(TOKEN)
