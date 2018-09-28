import configparser as ConfigParser
from pathlib import Path


class ConfigUtil:
    config = ConfigParser.ConfigParser()
    settings_file = 'settings.ini'

    def __init__(self, section_name):
        self.section_name = section_name

    def config_exists(self):
        self.read()
        path = Path(self.settings_file)
        if path.exists():
            self.config.read(self.settings_file)
            return self.config.has_section(self.section_name)
        else:
            return False

    def write_new_settings(self, settings):
        self.read()

        section = self.section_name
        config = self.config

        config.add_section(section)
        for option, value in settings.items():
            config.set(section, option, value)

        self.save()

    def save(self):
        with open(self.settings_file, 'w') as configfile:
            self.config.write(configfile)

    def read(self):
        self.config.read(self.settings_file)

    def get(self, option):
        self.read()
        return self.config.get(self.section_name, option)

    def set(self, option, value):
        self.read()
        self.config.set(self.section_name, option, value)
        self.save()

    def update_defaults(self, defaults):
        """Sets the defaults for the module if the key does not exist,
        if there are extras that have been deprecated they will be removed"""
        self.read()
        for key in self.config[self.section_name]:
            if key not in defaults.keys():
                self.config.remove_option(self.section_name, key)

        for key, value in defaults.items():
            if key not in self.config[self.section_name]:
                self.config.set(self.section_name, key, value)

        self.save()


if __name__ == '__main__':
    configUtil = ConfigUtil('welcome')
    var = {
        'enabled': 'True',
        'message': '{0.mention}, welcome to {0.guild.name}!',
        'welcome_channel': '-1',
        'leave_channel': '-1',
        'leave_message': '{0.display_name}#{0.discriminator} has left the server. :wave:',
        'newval': 'wooooyhooo'
    }
    configUtil.update_defaults(var)
