#!/usr/bin/env python3


import re
import json
import os.path
import inspect
import random


ignore = ['##monsterhunter']


class Plugin:
    def __init__(self, bot):
        self.bot = bot
        bot.register_event(__name__, ['PRIVMSG'], self.message)
        bot.register_event(__name__, 'TICK', self.shutdown)
        bot.register_command(__name__, ['presents'], self.count,
                             channels=['!##monsterhunter'])
        if not os.path.exists('plugins/items.json'):
            self.items = {}
        else:
            with open('plugins/items.json', 'r') as f:
                self.items = json.loads(f.read())

    def shutdown(self):
        with open('plugins/items.json', 'w') as f:
            f.write(json.dumps(self.items))
        return None

    def count(self, server, user, channel):
        """Counts the presents for this channel."""
        if channel not in self.items:
            return 'I have 0 presents.'
        return 'I have {} presents.'.format(len(self.items[channel]))

    def message(self, server, host, _, channel, *message):
        if channel in ignore:
            return None
        message = ' '.join(message)[1:]
        nickname, host = host[1:].split('!')
        if channel not in self.items:
            self.items[channel] = []

        if message.startswith('\x01ACTION'):
            giving = re.search('gives {} (.*?)\.?\x01'.format(server.nickname),
                           message, re.I)
            if giving is not None:
                item = giving.group(1).strip()
                self.items[channel].append(item)
                server.privmsg(channel, 'I now have {}.'.format(item))
                return None
        
        regift = re.search('{}(,|:) give (.*?) a present'.format(
                           server.nickname), message, re.I)

        if regift is not None:
            if len(self.items[channel]) == 0:
                server.privmsg(channel, 'I have no items to give!')
                return None

            item = random.choice(self.items[channel])
            index = self.items[channel].index(item)
            del self.items[channel][index]
            server.privmsg(channel, '\x01ACTION gives {} {}.\x01'.format(
                           regift.group(2), item))
            return None
        return None
