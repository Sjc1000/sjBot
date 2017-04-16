#!/usr/bin/env python3


import os
import importlib
import types
import inspect
import threading
import urllib.parse
import json
import hashlib
import time

import base as irc
import requests
from bs4 import BeautifulSoup


DEBUG = False


class Bot:
    def __init__(self):
        self.plugins = []
        self.commands = []
        self.events = []
        self.plugin_times = {}
        self.load_plugins()
        self.load_settings()
        self.reload_loop()
        self.command_cooldown = [0, 0]

    def reload_loop(self):
        thread = threading.Thread(target=self._reload_loop)
        thread.daemon = True
        thread.start()
        return None

    def _reload_loop(self):
        while True:
            time.sleep(20)
            self.load_plugins()
            self.load_settings()
            self.run_tick_event()
        return None

    def run_tick_event(self):
        for event in self.events:
            if event['events'] == 'TICK':
                event['function']()
        return None

    def load_settings(self):
        with open('settings.json', 'r') as f:
            self.settings = json.loads(f.read())
        return None

    def shutdown(self):
        print()
        for plugin in self.plugins:
            function = getattr(plugin, 'shutdown', None)
            if function is not None:
                print('Shutting down plugin: {}'.format(plugin))
                function()
        return None

    def queue_for_update(self, plugins):
        for plugin in plugins:
            directory = 'plugins/{}'.format(plugin)
            self.plugin_times[directory] = 0
        return None

    def find_plugin(self, name):
        for plugin in self.plugins:
            plugin_name = getattr(plugin, '_name', None)
            if plugin_name == name:
                return plugin
        return None

    def load_plugins(self):
        files = [x for x in os.listdir('plugins') if x.endswith('.py')]
        for name in files:
            directory = 'plugins/{}'.format(name)
            mtime = os.path.getmtime(directory)
            if (directory in self.plugin_times
            and mtime == self.plugin_times[directory]):
                continue
            print('Plugin: {}'.format(directory))
            self.plugin_times[directory] = mtime
            fname, ext = os.path.splitext(name)
            loader = importlib.machinery.SourceFileLoader(fname, directory)
            module = types.ModuleType(loader.name)
            loader.exec_module(module)
            
            find_class = getattr(module, 'Plugin', False)
            if not find_class:
                print('\t- No class.')
                continue
            print('\t- Init')
            plugin = module.Plugin(self)
            new_name = str(plugin)[1:].split('.')[0]
            for index, item in enumerate(list(self.plugins)):
                name = str(item)[1:].split('.')[0]
                if new_name == name:
                    print('\t- Unloading old plugin.')
                    old_plugin = self.plugins[index]
                    close_function = getattr(old_plugin, 'shutdown', None)
                    if close_function is not None:
                        print('\t- Gracefully closing old version.')
                        close_function()
                    del self.plugins[index]

            self.plugins.append(plugin)
            print('\t- Loaded plugin.')
        return None

    def register_command(self, plugin, aliases, function, channels=[],
                         owner=False):
        cmd_string = '{}+{}+{}'.format(plugin, ','.join(aliases),
                     function.__name__)
        for check in list(self.commands):
            check_string = '{}+{}+{}'.format(check['plugin'],
                           ','.join(check['aliases']),
                            check['function'].__name__)
            if check_string == cmd_string:
                index = self.commands.index(check)
                print('\t- Unloading: {}'.format(function.__name__))
                del self.commands[index]

        print('\t- Loading: {}'.format(function.__name__))
        command = {'aliases': aliases, 'function': function,
                'ignore': channels, 'owner': owner, 'plugin': plugin}
        self.commands.append(command)
        return cmd_string

    def register_event(self, plugin, events, function, channels=[],
                       owner=False):
        event_name = '{}+{}+{}'.format(plugin, ','.join(events),
                      function.__name__)
        for index, check in enumerate(list(self.events)):
            check_name = '{}+{}+{}'.format(check['plugin'],
                         ','.join(check['events']),
                         check['function'].__name__)
            if event_name == check_name:
                print('\t- Unloading: {}'.format(function.__name__))
                del self.events[index]

        print('\t- Loading: {}'.format(function.__name__))
        event = {'events': events, 'function': function,
                'ignore': channels, 'owner': owner, 'plugin': plugin}
        self.events.append(event)
        return None

    @irc.privmsg
    def message(self, server, user, channel, message, host):
        user = User(user, host)
        if channel == user.name:
            triggers = self.settings['triggers']['pm']
        elif channel in self.settings['triggers']:
            triggers = self.settings['triggers'][channel]
        else:
            triggers = self.settings['triggers']['default']
        for trigger in triggers:
            if message.startswith(trigger):
                _, message = message.split(trigger, 1)
                if message == '':
                    return None

                if ' ' not in message:
                    command = message
                    params = []
                else:
                    command, params = message.split(' ', 1)
                    params = params.split(' ')
                if command.startswith(trigger):
                    return None

                params = [x for x in params if x.strip() != '']
                command = command.lower()
                thread = threading.Thread(target=self.call_command,
                         args=(command, params, server, user, channel))
                thread.daemon = True
                thread.start()
        return None

    def ignore_command(self, channel, data, user):
        if DEBUG or channel == user.name:
            return False
        if data['ignore'] == [] or channel in data['ignore']:
            return False
        for chan in data['ignore']:
            if chan.startswith('!'):
                _, name = chan.split('!', 1)
                if name == channel:
                    return True
                else:
                    return False
        return True

    def google_search(self, query, site=''):
        if site != '':
            site = 'site:{} '.format(site)
        query = site + query
        req = requests.get('http://google.com/search?safe=off&q={}'.format(query))
        soup = BeautifulSoup(req.text, 'html.parser')
        url = soup.find_all('h3')
        urls = []
        for index, item in enumerate(url):
            href = item.a.get('href')
            item_url = href.split('=', 1)[1].split('&')[0]
            if not item_url.startswith('http'):
                continue
            urls.append(urllib.parse.unquote(item_url))
        return urls 

    def call_command(self, command, params, server, user, channel):
        if (self.command_cooldown[0] > 8
        and time.time()-self.command_cooldown[1] < 10):
            return None
        if self.command_cooldown[0] > 8:
            self.command_cooldown[0] = 0
        self.command_cooldown[0] += 1
        self.command_cooldown[1] = time.time()

        data = self.is_command(command)
        if data is None:
            chan_name = str(channel)
            if chan_name in self.settings['default_commands']:
                params = [command] + params
                command = self.settings['default_commands'][chan_name]
                data = self.is_command(command)
            else:
                return None

        ignore = self.ignore_command(channel, data, user)
        if ignore:
            return None

        # Inspect the function to see if you passed the right params.
        # params: server, user, channel, x...

        sig = inspect.signature(data['function']) 
        prms = sig.parameters
        optional = 0
        required = 0

        for i, p in enumerate(prms):
            if i < 3:
                continue

            if (prms[p].default == prms[p].empty and
            prms[p].kind != prms[p].VAR_POSITIONAL):
                required += 1
            else:
                optional += 1

        if (len(params) > (required+optional)
        and not any(prms[p].kind == prms[p].VAR_POSITIONAL for p in prms)
        or len(params) < required):
            server.privmsg(channel, 'Invalid params: Command "{}" takes '
                           'between {} and {} params.'.format(command,
                           required, optional))
            return None

        function = data['function']
        output = function(server, user, channel, *params)
        if output is not None:
            if isinstance(output, list):
                for item in output:
                    server.privmsg(channel, item)
            else:
                server.privmsg(channel, output)
        return None

    def is_command(self, command):
        for info in self.commands:
            if command in info['aliases']:
                return info
        return None

    def is_event(self, event):
        events = []
        for info in self.events:
            if event in info['events']:
                events.append(info)
        return events

    @irc.irc_data('PING')
    def reload_plugins(self, server, *_):
        self.load_plugins()
        return None

    @irc.connected
    def send_pass(self, server):
        server.privmsg('NickServ', 
                       'identify sjBot {}'.format(self.settings['bot_password']))
        #self.join_channels(server)
        return None

    @irc.identified
    def join_channels(self, server, *_):
        for channel in self.settings['channels']:
            server.join(channel)
        return None

    @irc.recv_data
    def log(self, server, data):
        print('[IN ] {}'.format(data))
        self.call_event(server, data)
        return None

    def call_event(self, server, data):
        split = data.split(' ')
        event = None
        check_one = self.is_event(split[0])
        if check_one != []:
            event = check_one
        else:
            event = self.is_event(split[1])

        if event == []:
            return None

        for ev in event:
            function = ev['function']
            args = [server]
            args.extend(split)
            thread = threading.Thread(target=function, args=tuple(args))
            thread.start()
        return None

    @irc.sent_data
    def log_out(self, server, data):
        print('[OUT] {}'.format(data))
        return None


class User:
    def __init__(self, name, host):
        self.name = name
        self.host = host


if __name__ == '__main__':
    bot = Bot()

    server = irc.Server('localhost', nickname='sjBot', ref=bot)
    server.connect()
    server.identify()

    try:
        server.main()
    except KeyboardInterrupt:
        bot.shutdown()
