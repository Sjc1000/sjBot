#!/usr/bin/env python3


import requests


class Plugin:
    
    _name = 'ddg'

    def __init__(self, bot):
        self.bot = bot
        bot.register_command(self._name, ['define', 'def', 'ddg'], self.search,
                             channels=['!##monsterhunter'])

    def search(self, server, user, channel, *query):
        """Searches DuckDuckGo."""
        query = ' '.join(query)
        req = requests.get('http://api.duckduckgo.com/?q={}'
                           '&format=json'.format(query))
        data = req.json()
        topics = data['RelatedTopics']
        if topics == []:
            return '[\x035DuckDuckGo\x03] No results found'

        first = topics[0]
        return '[\x033DuckDuckGo\x03] \x02{Text}\x02 - {FirstURL}'.format(**first)
