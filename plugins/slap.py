#!/usr/bin/env python3


class Plugin:
    def __init__(self, bot):
        self.bot = bot
        bot.register_command(__name__, ['slap'], self.slap,
                             ['!##monsterhunter'])
        bot.register_command(__name__, ['stab'], self.stab,
                             ['##monsterhunter'])

    def slap(self, server, user, channel, nickname):
        """Slaps someone."""
        return self.do_action(server, user, nickname, 'slaps')

    def stab(self, server, user, channel, nickname):
        """Stabs someone."""
        return self.do_action(server, user, nickname, 'stabs')

    def do_action(self, server, user, nickname, action):
        if nickname == server.nickname:
            nickname = user.name
        return '\x01ACTION {} {}\x01'.format(action, nickname) 
