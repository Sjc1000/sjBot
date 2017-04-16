#!/usr/bin/env python3


import subprocess
from datetime import datetime


ignore = ['##monsterhunter']


class Plugin:

    _name = 'vim-replace'

    def __init__(self, bot):
        self.bot = bot
        self.storage = {}
        bot.register_event(self._name, 'PRIVMSG', self.privmsg)

    def privmsg(self, server, host, _, channel, *message):
        nickname, host = host[1:].split('!')
        if channel not in self.storage:
            self.storage[channel] = []
        message = ' '.join(message)[1:].strip()
        if message.startswith('s/') and channel not in ignore:
            for _, text_nick, text_message in reversed(self.storage[channel]):
                if text_nick != nickname:
                    continue
                command = ['sed', '-e', '{}'.format(message)]
                try:
                    output = subprocess.check_output(command,
                             input=text_message.encode('utf-8'))
                except subprocess.CalledProcessError:
                    continue
                output = output.decode('utf-8')
                output = output.strip('\n ')
                if output == text_message:
                    continue
                output = repr(output)[1:-1]
                if output.strip() == '':
                    continue
                server.privmsg(channel, '{} \x02meant\x02 to say:'
                               ' {}'.format(nickname, output))
                return None
            return None
        self.storage[channel].append((datetime.utcnow(), nickname, message))
        self.storage[channel] = self.storage[channel][-50:]
        return None
