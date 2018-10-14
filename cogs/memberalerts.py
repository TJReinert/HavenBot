import ConfigurationHelper
import MessageHelper
import discord
import PermissionChecks
from discord.ext import commands
import re


class MemberAlerts:
    defaults = {
        'enabled': 'True',
        'autoBan': 'True',
        'message': '{0.mention}, welcome to {0.guild.name}!',
        'welcome_channel': '-1',
        'leave_channel': '-1',
        'leave_message': '{0.display_name}#{0.discriminator} has left the server. :wave:',
        'auto_ban_message': '{0.display_name}#{0.discriminator} auto banned.',
        'ban_channel': '-1'
    }

    def __init__(self, bot):
        self.configUtil = ConfigurationHelper.ConfigUtil('welcome')
        self.messageUtil = MessageHelper.MessageUtil(bot)
        self.ban_regex = r"(discord.(me|gg))"

        if not self.configUtil.config_exists():
            self.create_default_config()
        else:
            self.configUtil.update_defaults(self.defaults)

        self.bot = bot

    def create_default_config(self):
        self.configUtil.write_new_settings(self.defaults)

    def toggle(self):
        is_enabled = self.welcome_is_enabled()
        if is_enabled:
            self.disable_welcome()
        else:
            self.enable_welcome()
        return not is_enabled

    def enable_welcome(self):
        self.configUtil.set('enabled', 'True')

    def disable_welcome(self):
        self.configUtil.set('enabled', 'False')

    def toggle_auto_ban(self):
        is_enabled = self.auto_ban_is_enabled()
        if is_enabled:
            self.disable_auto_ban()
        else:
            self.enable_auto_ban()
        return not is_enabled

    def enable_auto_ban(self):
        self.configUtil.set('autoBan', 'True')

    def disable_auto_ban(self):
        self.configUtil.set('autoBan', 'False')

    def set_welcome_message(self, message):
        self.configUtil.set('message', message)

    def get_welcome_message(self):
        return self.configUtil.get('message')

    def set_welcome_channel_id(self, channel_id):
        self.configUtil.set('welcome_channel', channel_id)

    def get_welcome_channel_id(self):
        return int(self.configUtil.get('welcome_channel'))

    def set_ban_channel_id(self, channel_id):
        self.configUtil.set('ban_channel', channel_id)

    def get_ban_channel_id(self):
        return int(self.configUtil.get('ban_channel'))

    def set_leave_message(self, message):
        self.configUtil.set('leave_message', message)

    def get_leave_message(self):
        return self.configUtil.get('leave_message')

    def set_leave_channel_id(self, channel_id):
        self.configUtil.set('leave_channel', channel_id)

    def get_leave_channel_id(self):
        return int(self.configUtil.get('leave_channel'))

    def welcome_is_enabled(self):
        return 'True' == self.configUtil.get('enabled')

    def auto_ban_is_enabled(self):
        return 'True' == self.configUtil.get('autoBan')

    @commands.check(PermissionChecks.is_admin)
    @commands.command(name='welcome.toggle')
    async def toggle_welcome(self, ctx):
        new_state = 'enabled' if self.toggle() else 'disabled'
        await ctx.send("Welcome messeges have been {}.".format(new_state))

    @commands.check(PermissionChecks.is_admin)
    @commands.command(name='autoban.toggle')
    async def toggle_auto_ban(self, ctx):
        new_state = 'enabled' if self.toggle_auto_ban() else 'disabled'
        await ctx.send("Autoban has been {}.".format(new_state))

    @commands.check(PermissionChecks.is_admin)
    @commands.command(name='welcome.here', aliases=['join.here'])
    async def set_welcome_channel(self, ctx):
        self.set_welcome_channel_id(str(ctx.channel.id))
        await ctx.send("Okay, I will welcome new members in {0.channel.mention}".format(ctx))

    @commands.check(PermissionChecks.is_admin)
    @commands.command(name='welcome.set')
    async def set_welcome(self, ctx, *, arg):
        self.set_welcome_message(arg)
        await ctx.send("Welcome messeges have been set to {}.".format(arg)
                       + '\n'
                       + "It will look like this when someone joins."
                       + '\n')

        await self.on_member_join(ctx.author)

    @commands.check(PermissionChecks.is_admin)
    @commands.command(name='leave.here')
    async def set_leave_channel(self, ctx):
        self.set_leave_channel_id(str(ctx.channel.id))
        await ctx.send("Okay, I will let everyone know when someone leaves in {0.channel.mention}".format(ctx))

    @commands.check(PermissionChecks.is_admin)
    @commands.command(name='ban.here')
    async def set_ban_channel(self, ctx):
        self.set_ban_channel_id(str(ctx.channel.id))
        await ctx.send("Okay, I will let everyone know when someone is banned in {0.channel.mention}".format(ctx))

    @commands.check(PermissionChecks.is_admin)
    @commands.command(name='leave.set')
    async def set_leave(self, ctx, *, arg):
        self.set_leave_message(arg)
        await ctx.send("Leave messeges have been set to {}.".format(arg)
                       + '\n'
                       + "It will look like this when someone leaves."
                       + '\n')

        await self.on_member_remove(ctx.author)

    def name_is_forbidden(self, member):
        matches = re.search(self.ban_regex, member.display_name, re.MULTILINE | re.IGNORECASE)
        return matches is not None

    @commands.check(welcome_is_enabled)
    async def on_member_join(self, member):
        if self.auto_ban_is_enabled() and self.name_is_forbidden(member):
            try:
                await member.guild.ban(member, reason='Auto ban: Forbidden name')
            except discord.Forbidden:
                await self.messageUtil.format_and_send_channel(self.get_ban_channel_id(),
                                                               'Unable to ban {0.display_name}. Missing permissions!',
                                                               member)

        else:
            channel_id = self.get_welcome_channel_id()
            message = self.get_welcome_message()

            await self.messageUtil.format_and_send_channel(channel_id, message, member)

    @commands.check(welcome_is_enabled)
    async def on_member_remove(self, member):
        await self.messageUtil.format_and_send_channel(self.get_leave_channel_id(), self.get_leave_message(), member)

    @commands.check(welcome_is_enabled)
    async def on_member_ban(self, guild, member):
        message = '{0.display_name}#{0.discriminator} has been banned from the server. '
        await self.messageUtil.format_and_send_channel(self.get_ban_channel_id(), message, member)

    @commands.check(welcome_is_enabled)
    async def on_member_unban(self, guild, member):
        message = '{0.display_name}#{0.discriminator} has been unbanned from the server.'
        await self.messageUtil.format_and_send_channel(self.get_ban_channel_id(), message, member)

    @commands.command()
    @commands.guild_only()
    async def joined(self, ctx, *, member: discord.Member):
        """Says when a member joined."""
        await ctx.send('{member.display_name} joined on {member.joined_at}')


def setup(bot):
    bot.add_cog(MemberAlerts(bot))
