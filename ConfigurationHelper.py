import configparser as ConfigParser
from pathlib import Path


class ConfigUtil:
    config = ConfigParser.ConfigParser()
    settings_file = 'settings.ini'

    def __init__(self, section_name):
        self.section_name = section_name

    def config_exists(self):
        path = Path(self.settings_file)
        if path.exists():
            self.config.read(self.settings_file)
            return self.config.has_section(self.section_name)
        else:
            return False

    def write_new_settings(self, settings):
        section = self.section_name
        config = self.config

        config.add_section(section)
        for option, value in settings:
            config.set(section, option, value)

        self.save()

    def save(self):
        with open(self.settings_file, 'w') as configfile:
            self.config.write(configfile)

    def get(self, option):
        self.config.read(self.settings_file)
        return self.config.get(self.section_name, option)

    def set(self, option, value):
        self.config.set(self.section_name, option, value)
        self.save()
