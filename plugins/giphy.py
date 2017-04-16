#!/usr/bin/env python3


import requests
import random


class Plugin:
    def __init__(self, bot):
        self.bot = bot
        bot.register_command(__name__, ['giphy', 'gp'], self.giphy,
                             channels=['!##monsterhunter'])

    def giphy(self, server, user, channel, *query):
        """Searches giphy and returns a random result."""
        query = ' '.join(query)
        key = self.bot.settings['giphy_key']
        req = requests.get('http://api.giphy.com/v1/gifs/search?q={}'
                           '&api_key={}'.format(query, key))
        data = req.json()
        if data['data'] == []:
            return '[\x035Giphy\x03] No results'
        images = random.choice(data['data'])['images']
        return '[\x033Giphy\x03] {}'.format(images['original']['url'])


