#!/usr/bin/env python3


import requests
import json


class Plugin:

    _name = 'youtube'

    def __init__(self, bot):
        self.bot = bot
        bot.register_command(self._name, ['youtube', 'yt', 'ytb', 'y'],
                             self.search, channels=['!##monsterhunter'])

    def search(self, server, user, channel, *query):
        """Search youtube for a video"""
        query = ' '.join(query)
        key = self.bot.settings['google_key']
        req = requests.get('https://www.googleapis.com/youtube/v3/search?'
                           'key={}&part=id,snippet&q={}'.format(key, query))
        data = req.json()
        if data['pageInfo']['totalResults'] == 0:
            return '[\x035YouTube\x03] \x02Nothing found\x02'

        item = data['items'][0]
        title = item['snippet']['title']
        if 'videoId' not in item['id']:
            return '[\x035YouTube\x03] \x02Nothing found\x02'
        vid_id = item['id']['videoId']
        vid_url = 'https://youtu.be/{}'.format(vid_id)
        return '[\x033YouTube\x03] \x02{}\x02 - {}'.format(title, vid_url)
