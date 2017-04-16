#!/usr/bin/env python3


import requests


class Plugin:

    _name = 'wolfram'

    def __init__(self, bot):
        self.bot = bot
        bot.register_command(self._name, ['wolfram', 'wa'], self.wolfram)

    def wolfram(self, server, user, channel, *query):
        """Queries wolfram."""
        query = ' '.join(query)
        key = self.bot.settings['wolfram_key']
        req = requests.get('https://api.wolframalpha.com/v1/'
                           'result?i={}&appid={}'.format(query, key))
        text = req.text
        if text == 'No short answer available':
            color = 5
        else:
            color = 3
        return '[\x03{}Wolfram\x03] {}'.format(color, text)
