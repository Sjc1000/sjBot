#!/usr/bin/env python3


import requests


class Plugin:
    def __init__(self, bot):
        self.bot = bot
        bot.register_command(__name__, ['imdb', 'movie'], self.search,
                             channels=['!##monsterhunter'])

    def search(self, server, user, channel, *movie):
        search = ' '.join(movie)
        req = requests.get('http://www.omdbapi.com/?s={}'.format(search))
        print( req )
        data = req.json()
        print( data )
        title = data['Search'][0]['Title']
        print( title )
        return None
