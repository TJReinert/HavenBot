import traceback
from pathlib import Path

import discord
import sys
import random
from aiohttp import ClientSession
from discord.ext import commands
from requests import get
from os import listdir
from os.path import isfile, join


bot = commands.Bot(command_prefix='$', description='A bot that greets the user back.')
client = discord.Client().user


def get_cogs_extensions_list():
    cogs_dir = 'cogs'
    return ['.'.join([cogs_dir, f.replace('.py', '')]) for f in listdir(cogs_dir) if isfile(join(cogs_dir, f))]


if __name__ == '__main__':
    for extension in get_cogs_extensions_list():
        print(extension)
        try:
            bot.load_extension(extension)
        except (discord.ClientException, ModuleNotFoundError) as e:
            print('Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()


@bot.event
async def on_ready():
    print('Version: ' + discord.__version__)
    print('User: ' + bot.user.name)
    print('id: ' + str(bot.user.id))
    print('token: ' + get_token())
    print('------')


async def is_admin(ctx):
    return ctx.message.author.guild_permissions.administrator




@commands.check(is_admin)
@bot.command()
async def whatsYourIp(ctx):
    ip = get('https://api.ipify.org').text
    # isPrivateChannel = ctx.channel.is_private

    await ctx.send("Sliding into your DMs with that sweet sweet :eggplant:.")
    await ctx.message.author.send('My public IP address is: {}'.format(ip))


@commands.check(is_admin)
@bot.command()
async def echo(ctx, *, arg):
    await ctx.send(arg.format(ctx.author))


@commands.check(is_admin)
@bot.command()
async def flirt(ctx):
    flirts = [':eggplant:']

    await ctx.send(random.choice(flirts))


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
