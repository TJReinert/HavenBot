from pathlib import Path

import discord
import sys
import random
from aiohttp import ClientSession
from discord.ext import commands
from requests import get

from Welcome import Welcome

bot = commands.Bot(command_prefix='$', description='A bot that greets the user back.')
client = discord.Client().user


@bot.event
async def on_ready():
    print('Version: ' + discord.__version__)
    print('User: ' + bot.user.name)
    print('id: ' + str(bot.user.id))
    print('token: ' + get_token())
    print('------')


async def is_admin(ctx):
    return ctx.message.author.guild_permissions.administrator

# WelcomeBot Accessors
welcome = Welcome()


@bot.event
async def on_member_join(member):
    if welcome.is_enabled():
        await welcome_member(member)


async def welcome_member(member):
    message = welcome.get_welcome_message()
    channel_id = welcome.get_channel_id()
    if channel_id == -1:
        channel = bot.get_channel(member.guild.channels[00].id)
    else:
        channel = bot.get_channel(channel_id)
    await channel.send(message.format(member))


@bot.event
async def on_member_remove(member):
    if welcome.is_enabled():
        await alert_member_kick(member)


async def alert_member_kick(member):
    message = '{0.mention} has been kicked from the server. Good riddance.'
    channel_id = welcome.get_channel_id()
    if channel_id == -1:
        channel = bot.get_channel(member.guild.channels[00].id)
    else:
        channel = bot.get_channel(channel_id)
    await channel.send(message.format(member))


async def alert_member_leave(member):
    message = '{0.mention} has left the server. :wave:'
    channel_id = welcome.get_channel_id()
    if channel_id == -1:
        channel = bot.get_channel(member.guild.channels[00].id)
    else:
        channel = bot.get_channel(channel_id)
    await channel.send(message.format(member))


@commands.check(is_admin)
@bot.command()
async def whatsYourIp(ctx):
    ip = get('https://api.ipify.org').text
    # isPrivateChannel = ctx.channel.is_private

    await ctx.send("Sliding into your DMs with that sweet sweet :eggplant:.")
    await ctx.message.author.send('My public IP address is: {}'.format(ip))


@commands.check(is_admin)
@bot.command()
async def flirt(ctx):
    flirts = [':eggplant:']

    await ctx.send(random.choice(flirts))


@commands.check(is_admin)
@bot.command()
async def toggleWelcome(ctx):
    new_state = 'enabled' if welcome.toggle() else 'disabled'
    await ctx.send("Welcome messeges have been {}.".format(new_state))


@commands.check(is_admin)
@bot.command()
async def setWelcome(ctx, *, arg):
    welcome.set_welcome_message(arg)
    await ctx.send("Welcome messeges have been set to {}.".format(arg)
                   + '\n'
                   + "It will look like this when someone joins."
                   + '\n')
    await welcome_member(ctx.author)


@commands.check(is_admin)
@bot.command()
async def welcomeHere(ctx):
    welcome.set_channel_id(str(ctx.channel.id))
    await ctx.send("Okay, I will welcome new members in {0.channel.mention}".format(ctx))


@commands.check(is_admin)
@bot.command()
async def shutdown(ctx):
    await ctx.send("ByeBye!")
    sys.exit("{0.message.author.name} executed shutdown command".format(ctx))


@commands.check(is_admin)
@bot.command()
async def setAvatar(ctx, arg=None):
    image_url = await determine_image_url(arg, ctx)
    if image_url is None:
        ctx.send("Did you pass in a URL or Image?")
    async with ClientSession() as session:
        async with session.get(image_url) as response:
            image = await response.read()
            await ctx.bot.user.edit(avatar=image)
            await ctx.send("I am an enigma. I have become {}".format(image_url))
    # await ctx.send("An error occurred. Status code {}".format(r.status))


async def determine_image_url(image_url, ctx):
    if image_url is None:
        image_url = ctx.message.attachments[0].url
    return image_url


@commands.check(is_admin)
@bot.command()
async def setUserName(ctx, *, arg):
    if len(arg) < 2:
        await ctx.send("Name must be longer than 2 characters")
    else:
        await ctx.bot.user.edit(username=arg[:32])
        await ctx.send("All hail {}!".format(arg))


def get_token():
    token_file = Path('token')
    if token_file.exists():
        return token_file.read_text()
    else:
        sys.exit("Token file and token must exist.")


bot.run(get_token())
