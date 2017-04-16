#!/usr/bin/env python3


class Plugin:
    
    _name = 'google'

    def __init__(self, bot):
        self.bot = bot
        bot.register_command(self._name, ['google', 'g'], self.search,
                             channels=['!##monsterhunter'])

    def search(self, server, user, channel, *query):
        """Search google for a query."""
        query = ' '.join(query)
        results = self.bot.google_search(query)
        if results == []:
            return '[\x035Google\x03] \x02No results\x02'
        return '[\x033Google\x03] {}'.format(results[0])
