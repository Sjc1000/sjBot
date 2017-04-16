#!/usr/bin/env python3


import random


class Plugin:

    _name = 'dance'

    def __init__(self, bot):
        self.bot = bot
        bot.register_command(self._name, ['dance'], self.dance,
                             channels=['!##monsterhunter'])
        bot.register_command(self._name, ['dance_old'], self.dance_old,
                             channels=['#donationcoder'])

    def dance(self, server, user, channel, person=None):
        """Busts some moves!"""
        movements = ['\\o\\', '/o/', '\\o/', '\\o_', '_o/']
        return self.do_dance(movements, person)

    def dance_old(self, server, user, channel, person=None):
        """Old style dance."""
        movements = ['^(^.^)^', '<(^.^<)', '(>^.^)>', 'v(^.^)v']
        return self.do_dance(movements, person)
    
    def do_dance(self, movements, person):
        if person is not None:
            output = 'Dance with me {}! '.format(person)
        else:
            output = 'Dance! '
        for i in range(random.randint(4, 8)):
            output += '\x03{}{}\x03 '.format(random.randint(1, 9),
                       random.choice(movements))
        return output
