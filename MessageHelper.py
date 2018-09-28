class MessageUtil:
    def __init__(self, bot):
        self.bot = bot

    async def format_and_send_channel(self, channel, message, member):
        # If this is an id, find the channel
        if isinstance(channel, int):
            channel = self.get_channel_from_id(channel, member)

        await channel.send(message.format(member))

    async def format_and_send_direct(self, message, member):
        await message.send(message.format(member))

    def get_channel_from_id(self, channel_id, member):
        if channel_id == -1:
            channel = self.bot.get_channel(member.guild.channels[00].id)
        else:
            channel = self.bot.get_channel(channel_id)
        return channel
