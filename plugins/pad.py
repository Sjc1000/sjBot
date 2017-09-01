#!/usr/bin/env python3


doodles = ['Sami_']


class Plugin:
    def __init__(self, bot):
        self.bot = bot
        bot.register_command(__name__, ['pad', 'pd'], self.pad,
                             channels=['##monsterhunter'])

    def pad(self, server, user, channel, *query):
        """Searches for a PAD query."""
        url = self.search(query, 'http://pad.wikia.com/wiki/')
        if url is None:
            return 'Could not find that.'
        return '\x02Here you go\x02 - {}'.format(url)

    def search(self, query, site):
        try:
            result = self.bot.google_search(' '.join(query), site)
        except Exception as e:
            return None
        if len(result) == 0:
            return None
        return result[0]
