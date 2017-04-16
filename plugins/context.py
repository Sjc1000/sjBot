#!/usr/bin/env python3


import time


class Plugin:
    def __init__(self, bot):
        self.bot = bot
        bot.register_command(__name__, ['context'], self.context)

    def context(self, server, user, chan, channel=None):
        """Returns the last 10 messages for a channel."""
        if channel is None:
            channel = chan

        replace = self.bot.find_plugin('vim-replace')
        messages = replace.storage[channel]
        for dtime, nickname, message in messages[-10:]:
            message_string = '({}:{}:{}) {}: {}'.format(dtime.hour, dtime.minute,
                              dtime.second, nickname, message)
            server.privmsg(user.name, message_string)
            time.sleep(1)
        return None
