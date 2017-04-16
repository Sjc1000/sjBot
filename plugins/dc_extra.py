#!/usr/bin/env python3


class Plugin:
    def __init__(self, bot):
        self.bot = bot
        bot.register_command('dc_key', ['key', 'keys'], self.keys,
                             ['#donationcoder'])
        bot.register_command('dc_pass', ['password', 'forgot'], self.password,
                             ['#donationcoder'])

    def keys(self, server, user, channel):
        return ('Click this link to access your DonationCoder keys '
                '- http://www.donationcoder.com/Keys/')

    def password(self, server, user, channel):
        return ('Click this link to reset your DonationCoder password '
                '- https://www.donationcoder.com/forum/index.php?action=reminder')
