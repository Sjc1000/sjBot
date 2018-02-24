#!/usr/bin/env python3


import json
import os


class Plugin:
    def __init__(self, bot):
        self.bot = bot
        bot.register_command(__name__, ['quote'], self.quote,
                            channels=['#uptone'])
        bot.register_command(__name__, ['unquote'], self.unquote,
                            channels=['#uptone'])
        bot.register_event(__name__, 'TICK', self.shutdown)
        if not os.path.exists('plugins/facts.json'):
            self.facts = []
        else:
            with open('plugins/facts.json', 'r') as f:
                self.facts = json.loads(f.read())
        self.load()

    def load(self):
        for (name, info) in self.facts:
            self.bot.register_command(
                self, [name], lambda *a: info,
                ['#uptone'])
        return None

    def shutdown(self):
        with open('plugins/facts.json', 'w') as f:
            f.write(json.dumps(self.facts))
        return None

    def quote(self, server, user, channel, quote_name, *info):
        quote_name = quote_name.lower()
        self.bot.register_command(
            self, [quote_name], lambda *a: ' '.join(info),
            ['#uptone'])
        self.facts.append([quote_name, ' '.join(info)])
        return 'Added {}'.format(quote_name)

    def unquote(self, server, user, channel, quote_name):
        for index, item in enumerate(list(self.bot.commands)):
            if item['aliases'] == [quote_name]:
                del self.bot.commands[index]
                return 'Removed {}'.format(quote_name)
        return 'Could not find that quote.'
