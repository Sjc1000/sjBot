#!/usr/bin/env python3


doodles = ['Sami_']


class Plugin:
    def __init__(self, bot):
        self.bot = bot
        bot.register_command(__name__, ['mh3u', '3u'], self.mh3u,
                             channels=['##monsterhunter'])
        bot.register_command(__name__, ['mh4u', '4u'], self.mh4u,
                             channels=['##monsterhunter'])
        bot.register_command(__name__, ['mhgen', 'gen'], self.mhgen,
                             channels=['##monsterhunter'])
        bot.register_command(__name__, ['mhxx', 'xx'], self.mhxx)

    def mhxx(self, server, user, channel, *query):
        """Searches for a mhxx related query."""
        url = self.search(query, 'mhxxx.kiranico.com/')
        if url is None:
            return 'Could not find that.'
        return '\x02Here you go, Doodle\x02 - {}'.format(url)

    def mh3u(self, server, user, channel, *query):
        """Searches for a mh3u query."""
        url = self.search(query, 'kiranico.com/en/mh3u')
        if url is None:
            return 'Could not find that.'
        return '\x02Here you go, Doodle\x02 - {}'.format(url)

    def mh4u(self, server, user, channel, *query):
        """Searches for a mh4u query."""
        url = self.search(query, 'kiranico.com/en/mh4u')        
        if url is None:
            return 'Could not find that.'
        return '\x02Here you go, Doodle\x02 - {}'.format(url)

    def mhgen(self, server, user, channel, *query):
        """Searches for a mhgen query."""
        name = 'Doodle' if user.name in doodles else 'Squiggle'
        url = self.search(query, 'http://mhgen.kiranico.com/')
        if url is None:
            return 'Could not find that.'
        return '\x02Here you go, {}\x02 - {}'.format(name, url)

    def search(self, query, site):
        try:
            result = self.bot.google_search(' '.join(query), site)
        except Exception as e:
            return None
        if len(result) == 0:
            return None
        return result[0]
