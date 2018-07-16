import ConfigurationHelper


class Welcome:
    configUtil = ConfigurationHelper.ConfigUtil('welcome')

    def __init__(self):
        if not self.configUtil.config_exists():
            self.create_default_config()

    def create_default_config(self):
        var = [
            ('enabled', 'True'),
            ('message', '{0.mention}, welcome to {0.guild.name}!'),
            ('channel', '-1'),
        ]
        self.configUtil.write_new_settings(var)

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

    def set_channel_id(self, channelId):
        self.configUtil.set('channel', channelId)

    def get_channel_id(self):
        return int(self.configUtil.get('channel'))

    def is_enabled(self):
        return 'True' == self.configUtil.get('enabled')


w = Welcome()

w.get_welcome_message()
# change welcome messege 1 line
