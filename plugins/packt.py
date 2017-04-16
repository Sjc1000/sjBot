#!/usr/bin/env python3


import json
import os
import requests
import time
from bs4 import BeautifulSoup


url = 'https://packtpub.com/packt/offers/free-learning'


class Plugin:
    def __init__(self, bot):
        self.bot = bot
        bot.register_command(__name__, ['packt'], self.packt,
                             ['#donationcoder'])
        bot.register_event(__name__, ['PING'], self.remind, ['#donationcoder'])
        bot.register_command(__name__, ['packt-remind', 'packt_remind'],
                             self.remind_list, ['#donationcoder'])
        bot.register_event(__name__, ['TICK'], self.shutdown)
        if not os.path.exists('plugins/packt_last'):
            self.last = ''
        else:
            with open('plugins/packt_last', 'r') as f:
                self.last = f.read()
        if not os.path.exists('plugins/packt_remind.json'):
            with open('plugins/packt_remind.json', 'w') as f:
                f.write('[]')

    def shutdown(self):
        with open('plugins/packt_last', 'w') as f:
            f.write(self.last)
        return None

    def remind_list(self, server, user, channel):
        with open('plugins/packt_remind.json', 'r') as f:
            names = json.loads(f.read())
        if user.name not in names:
            names.append(user.name)
            output = 'You will be reminded of new books.'
        else:
            del names[names.index(user.name)]
            output = 'You will not be reminded of new books.'
        with open('plugins/packt_remind.json', 'w') as f:
            f.write(json.dumps(names))
        return output

    def remind(self, server, *_):
        title, remaining = self.get_data()
        if self.last == '':
            self.last = title
            return None
        if self.last.strip() != title.strip():
            message = '[\x033Packt\x03] New Book: \x02{}\x02 - {}'.format(
                      title, url)
            server.privmsg('#donationcoder', message)
            self.last = title

            with open('plugins/packt_remind.json', 'r') as f:
                names = json.loads(f.read())

            if names == []:
                return None
            
            message_plugin = self.bot.find_plugin('message')
            if message_plugin is None:
                return None
            data = message_plugin.data
            for name in names:
                if name not in data:
                    data[name] = []
                data[name].append(message)
        return None

    def packt(self, server, user, channel):
        title, remaining = self.get_data()
        remaining = ':'.join([str(x) for x in remaining])
        return '[\x033Packt\x03] \x02{}\x02 {} - {}'.format(title, remaining, url)

    def get_data(self):
        req = requests.get(url, headers={'User-Agent': 'Remind Bot'})
        soup = BeautifulSoup(req.text, 'html.parser')
        title = soup.find('div', {'class': 'dotd-title'}).find('h2')
        title = title.text.strip()
        countdown = soup.find('span', {'class': 'packt-js-countdown'})
        countdown = countdown.get('data-countdown-to')
        difference = int(countdown)-time.time()
        countdown = reversed(seconds_to_hms(int(difference)))
        return title, countdown


def seconds_to_hms(seconds, times=[60, 60]):
    if times == [] or seconds < times[0]:
        return [seconds]
    rem, new = divmod(seconds, times[0])
    return [new] + seconds_to_hms(rem, times[1:])
