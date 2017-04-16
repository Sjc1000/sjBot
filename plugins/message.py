#!/usr/bin/env python3


import time
import os
import json


class Plugin:

    _name = 'message'

    def __init__(self, bot):
        self.bot = bot
        bot.register_command(__name__, ['message', 'msg'], self.create_message)
        bot.register_event(__name__, ['PRIVMSG'], self.check_message)
        if not os.path.exists('plugins/message_data.json'):
            self.data = {}
        else:
            with open('plugins/message_data.json', 'r') as f:
                self.data = json.loads(f.read())

    def shutdown(self):
        with open('plugins/message_data.json', 'w') as f:
            f.write(json.dumps(self.data))
        return None

    def check_message(self, server, host, channel, *_):
        """Stores a message."""
        nickname, host = host[1:].split('!')
        if nickname not in self.data:
            return None

        messages = self.data[nickname]
        count = ('{} messages'.format(len(messages)) if len(messages) > 1 
                 else '1 message')
        server.privmsg(nickname, 'You have {}:'.format(count))
        for message in messages:
            server.privmsg(nickname, message)
            time.sleep(1)

        del self.data[nickname]
        return None

    def create_message(self, server, user, channel, receiver, *message):
        message = '{}: {}'.format(user.name, ' '.join(message))
        if receiver not in self.data:
            self.data[receiver] = []
        self.data[receiver].append(message)
        if user.name == receiver:
            return 'I will remind you next time you talk.'
        return 'I will tell \x02{}\x02 next time I see them.'.format(receiver)
