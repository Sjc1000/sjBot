#!/usr/bin/env python3


import subprocess
import time
import json
import os


class Plugin:

    _name = 'remind'

    def __init__(self, bot):
        self.bot = bot
        bot.register_command(self._name, ['remindme', 'remind'], self.remind)
        bot.register_event(self._name, 'TICK', self.check_remind)
        if not os.path.exists('plugins/remind.json'):
            with open('plugins/remind.json', 'w') as f:
                f.write('{}')
        with open('plugins/remind.json', 'r') as f:
            self.data = json.loads(f.read())

    def shutdown(self):
        with open('plugins/remind.json', 'w') as f:
            f.write(json.dumps(self.data))
        return None

    def check_remind(self):
        current_time = time.time()
        message_plugin = self.bot.find_plugin('message')
        for user in self.data:
            for data in list(self.data[user]):
                sent, remind_time, message = data
                if current_time > remind_time:
                    if user not in message_plugin.data:
                        message_plugin.data[user] = []
                    send_message = 'Reminder: {}'.format(message)
                    message_plugin.data[user].append(send_message)
                    del self.data[user][self.data[user].index(data)]
        return None

    def remind(self, server, user, channel, *info):
        """Remind yourself. Usage: remindme time: message"""
        info = ' '.join(info)
        if ':' not in info:
            return 'Invalid syntax. Please use date time:message'

        when, message = info.split(':', 1)
        when, message = (when.strip(), message.strip())

        command = ['date', '-d', when, '+%s']
        remind_time = subprocess.check_output(command).decode('utf-8')

        if remind_time.startswith('date: invalid date'):
            return 'Invalid time.'

        remind_time = float(remind_time)

        current_time = time.time()
        if current_time > remind_time:
            return 'That time is in the past!'

        if user.name not in self.data:
            self.data[user.name] = []
        remind = (time.time(), remind_time, message)
        self.data[user.name].append(remind)
        real_date = subprocess.check_output(['date', '-d', when]).decode('utf-8')
        return 'You will be reminded on {}'.format(real_date)
