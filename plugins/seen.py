#!/usr/bin/env python3


import time
import threading
import os.path
import json
from math import ceil


class Plugin:
    def __init__(self, bot):
        self.bot = bot
        bot.register_command(__name__, ['seen'], self.seen)
        bot.register_event(__name__, ['PRIVMSG'], self.message)
        bot.register_event(__name__, ['PING'], self.ping)
        if not os.path.exists('plugins/seen_data.json'):
            with open('plugins/seen_data.json', 'w') as f:
                f.write('{}')
            self.data = {}
        else:
            with open('plugins/seen_data.json', 'r') as f:
                self.data = json.loads(f.read())

    def ping(self, server, *_):
        # Dump the variables to disk.
        self.shutdown()
        return None
    
    def shutdown(self):
        with open('plugins/seen_data.json', 'w') as f:
            f.write(json.dumps(self.data))
        return None

    def message(self, server, host, _, channel, *message):
        nickname, host = host[1:].split('!')
        info = 'chatting in {}'.format(channel)
        self.data[nickname] = [time.time(), info]
        return None

    def seen(self, server, user, channel, nickname):
        """Shows when someone was last seen."""
        if nickname == server.nickname:
            return '{} was seen right now, talking to you.'.format(nickname)

        if nickname not in self.data:
            return "I can't remember {}.".format(nickname)
        
        seen_time, message = self.data[nickname]
        tm = seconds_to_hms(time.time()-seen_time)
        names = ['seconds', 'minutes', 'hours', 'days']
        joined = list(reversed(list(zip(tm, names))))
        string = ', '.join(['{} {}'.format(ceil(x[0]), x[1]) for x in joined])
        return '{} was seen {} ago, {}'.format(nickname, string, message)


def seconds_to_hms(seconds, times=[60, 60, 24]):
    if times == [] or seconds < times[0]:
        return [seconds]
    rem, new = divmod(seconds, times[0])
    return [new] + seconds_to_hms(rem, times[1:])
