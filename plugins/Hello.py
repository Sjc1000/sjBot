#!/usr/bin/env python3


class Plugin:
    def __init__(self, bot):
        self.bot = bot
        self.bot.register_command(__name__, ['hello', 'hi'], self.hello,
                                  ['!##monsterhunter'])
        self.bot.register_event(__name__, ['PRIVMSG'], self.auto_hello)

    def hello(self, server, user, channel, username=None):
        """Says hello."""
        if username is not None:
            return 'Hello {}.'.format(username)
        return 'Hello {}.'.format(user.name)

    def auto_hello(self, server, host, _, channel, *message):
        message = ' '.join(message)[1:]
        if message.lower() == 'hi {}'.format(server.nickname.lower()):
            nickname, host = host[1:].split('!')
            server.privmsg(channel, 'Hi {}'.format(nickname))
        return None
