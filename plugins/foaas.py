#!/usr/bin/env python3


import requests


class Plugin:

    _name = 'foaas'

    def __init__(self, bot):
        self.bot = bot
        bot.register_command(self._name, ['foaas'], self.query,
                             ['!##monsterhunter', '!#ahk', '!#ahkscript'])

    def query(self, server, user, channel, *query):
        query = ' '.join(query)
        req = requests.get('http://foaas.com/{}'.format(query),
                           headers={'Accept': 'text/plain'})
        return req.text
