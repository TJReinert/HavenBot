import ConfigurationHelper
import MessageHelper
import discord
import PermissionChecks
from discord.ext import commands


class MemberAlerts:
    defaults = {
        'enabled': 'True',
        'message': '{0.mention}, welcome to {0.guild.name}!',
        'welcome_channel': '-1',
        'leave_channel': '-1',
        'leave_message': '{0.display_name}#{0.discriminator} has left the server. :wave:'
    }

    def __init__(self, bot):
        self.configUtil = ConfigurationHelper.ConfigUtil('welcome')
        self.messageUtil = MessageHelper.MessageUtil(bot)

        if not self.configUtil.config_exists():
            self.create_default_config()
        else:
            self.configUtil.update_defaults(self.defaults)

        self.bot = bot

    def create_default_config(self):
        self.configUtil.write_new_settings(self.defaults)

    def toggle(self):
        is_enabled = self.is_enabled()
        if is_enabled:
            self.disable()
        else:
            self.enable()
        return not is_enabled

    def enable(self):
        self.configUtil.set('enabled', 'True')

    def disable(self):
        self.configUtil.set('enabled', 'False')

    def set_welcome_message(self, message):
        self.configUtil.set('message', message)

    def get_welcome_message(self):
        return self.configUtil.get('message')

    def set_welcome_channel_id(self, channel_id):
        self.configUtil.set('welcome_channel', channel_id)

    def get_welcome_channel_id(self):
        return int(self.configUtil.get('welcome_channel'))

    def set_leave_message(self, message):
        self.configUtil.set('leave_message', message)

    def get_leave_message(self):
        return self.configUtil.get('leave_message')

    def set_leave_channel_id(self, channel_id):
        self.configUtil.set('leave_channel', channel_id)

    def get_leave_channel_id(self):
        return int(self.configUtil.get('leave_channel'))

    def is_enabled(self):
        return 'True' == self.configUtil.get('enabled')

    @commands.check(PermissionChecks.is_admin)
    @commands.command(name='welcome.toggle')
    async def toggle_welcome(self, ctx):
        new_state = 'enabled' if self.toggle() else 'disabled'
        await ctx.send("Welcome messeges have been {}.".format(new_state))

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
    @commands.command(name='welcome.here', aliases=['join.here'])
    async def set_welcome_channel(self, ctx):
        self.set_welcome_channel_id(str(ctx.channel.id))
        await ctx.send("Okay, I will welcome new members in {0.channel.mention}".format(ctx))

    @commands.check(PermissionChecks.is_admin)
    @commands.command(name='leave.here')
    async def set_leave_channel(self, ctx):
        self.set_leave_channel_id(str(ctx.channel.id))
        await ctx.send("Okay, I will let everyone know when someone leaves in {0.channel.mention}".format(ctx))

    @commands.check(is_enabled)
    async def on_member_join(self, member):
        message = self.get_welcome_message()
        channel_id = self.get_welcome_channel_id()

        await self.messageUtil.format_and_send_channel(channel_id, message, member)

    @commands.check(is_enabled)
    async def on_member_remove(self, member):
        await self.messageUtil.format_and_send_channel(self.get_leave_channel_id(), self.get_leave_message(), member)

    @commands.check(is_enabled)
    async def on_member_ban(self, member):
        message = '{0.display_name}#{0.discriminator} has been banned from the server. '
        await self.messageUtil.format_and_send_channel(self.get_leave_channel_id(), message, member)

    @commands.check(is_enabled)
    async def on_member_unban(self, member):
        message = '{0.display_name}#{0.discriminator} has been unbanned from the server.'
        await self.messageUtil.format_and_send_channel(self.get_leave_channel_id(), message, member)

    @commands.command()
    @commands.guild_only()
    async def joined(self, ctx, *, member: discord.Member):
        """Says when a member joined."""
        await ctx.send('{member.display_name} joined on {member.joined_at}')


def setup(bot):
    bot.add_cog(MemberAlerts(bot))
