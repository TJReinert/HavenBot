import discord, sys
from discord.ext import commands
from Welcome import Welcome
from pathlib import Path

bot = commands.Bot(command_prefix='$', description='A bot that greets the user back.')


@bot.event
async def on_ready():
    print('Version: ' + discord.__version__)
    print('User: ' + bot.user.name)
    print('id: ' + str(bot.user.id))
    print('token: ' + get_token())
    print('------')


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


@bot.command()
async def toggleWelcome(ctx):
    if ctx.message.author.guild_permissions.administrator:
        new_state = 'enabled' if welcome.toggle() else 'disabled'
        await ctx.send("Welcome messeges have been {}.".format(new_state))


@bot.command()
async def setWelcome(ctx, *, arg):
    if ctx.message.author.guild_permissions.administrator:
        welcome.set_welcome_message(arg)
        await ctx.send("Welcome messeges have been set to {}.".format(arg)
                       + '\n'
                       + "It will look like this when someone joins."
                       + '\n')
        await welcome_member(ctx.author)


@bot.command()
async def welcomeHere(ctx):
    if ctx.message.author.guild_permissions.administrator:
        welcome.set_channel_id(str(ctx.channel.id))
        await ctx.send("Okay, I will welcome new members in {0.channel.mention}".format(ctx))


@bot.command()
async def shutdown(ctx):
    if ctx.message.author.guild_permissions.administrator:
        await ctx.send("ByeBye!")
        # todo get context for user who executed
        sys.exit("{0.message.author.name} executed shutdown command".format(ctx))


def get_token():
    token_file = Path('token')
    if token_file.exists():
        return token_file.read_text()
    else:
        sys.exit("Token file and token must exist.")


bot.run(get_token())
