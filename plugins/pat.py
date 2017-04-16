#!/usr/bin/env python3


class Plugin:
    def __init__(self, bot):
        self.bot = bot
        bot.register_event(__name__, 'PRIVMSG', self.message)

    def message(self, server, host, _, channel, *message):
        message = ' '.join(message)[1:]
        if message.startswith('\x01ACTION pats {}'.format(server.nickname)):
            server.privmsg(channel, '\x01ACTION purrs like a Walrus.\x01')
        return None
