#!/usr/bin/env python3


import socket
import time
import os
import inspect
import threading


irc_functions = {}


def thread_connections(connections):
    successfull = []
    for connection in connections:
        connected = connection.connect()
        if connected:
            successfull.append(connection)
            connection.identify()
            thread = threading.Thread(target=connection.main)
            thread.start()
    return successfull


class irc_data:
    def __init__(self, message_type):
        global irc_functions
        if message_type not in irc_functions:
            irc_functions[message_type] = []
        self.message_type = message_type

    def __call__(self, func):
        global irc_functions
        def run(*args, **kwargs):
            return func(*args, **kwargs)
        irc_functions[self.message_type].append(func)
        return run


class Channel:
    def __init__(self, name):
        self.name = name
        self.users = {}

    def add_user(self, user, host=None, status=None, char=None):
        new_user = User(user, host, status, char)
        self.users[user] = new_user
        return None

    def remove_user(self, user):
        if user in self.users:
            del self.users[user]
        return None

    @property
    def operators(self):
        return {name:user for name, user in self.users.items()
                if user.is_operator}

    @property
    def voiced(self):
        return {name:user for name, user in self.users.items()
                if user.is_voiced}

    def __str__(self):
        return self.name


class User:
    def __init__(self, name, host, status=None, status_char=None):
        self.name = name
        self.host = host
        self.status = status
        self.status_char = status_char

    @property
    def is_operator(self):
        return self.status == 'o'

    @property
    def is_voiced(self):
        return self.status == 'v'
    
    def __str___(self):
        return self.name


class Server:
    def __init__(self, server=None, port=6667, nickname=None, username=None,
                 hostname=None, realname=None, password=None,
                 channels=[], ref=None):
        if any(x is None for x in [server, nickname]):
            raise AttributeError('server and nickname are required.')
        self.server = server
        self.nickname = nickname
        self.port = port
        self.username = username or nickname
        self.hostname = username or nickname
        self.realname = realname or nickname
        self.password = password
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.channels = {}
        self.server_settings = {}
        self.join_channels = channels
        self.ref = ref or self

    def __repr__(self):
        return '{}:{} {}'.format(self.server, self.port, self.nickname)

    def send(self, data):
        try:
            self.socket.send('{}\r\n'.format(data).encode('utf-8'))
        except BrokenPipeError:
            return False
        self.call_decorator('sent_data', data=data)
        return None

    def identify(self):
        if self.password is not None:
            self.send('PASS ' + self.password)
        self.send('NICK ' + self.nickname)
        self.send('USER {} {} {} :{}'.format(
                    self.nickname, self.username, self.hostname,
                    self.realname))
        return None

    def connect(self):
        for attempt in range(10):
            try:
                self.socket.connect((self.server, self.port))
            except (socket.gaierror, ConnectionRefusedError):
                time.sleep((attempt+1)*10)
                continue
            else:
                return True
        return False

    def main(self):
        prev = b''
        while True:
            prev += self.socket.recv(1024)
            if prev == b'':
                break
            while b'\r\n' in prev:
                line, prev = prev.split(b'\r\n', 1)
                line = line.decode('utf-8')
                self.call_decorator('recv_data', line)
                split = line.split(' ')
                first = getattr(self, 'r_' + split[0], None)
                func = first or getattr(self, 'r_' + split[1], None)
                if func is None:
                    continue
                if func == first:
                    params = split[1:]
                    func_name = split[0]
                else:
                    func_name = split[1]
                    params = [split[0]] + split[2:]
                func(*params)
                self.call_decorator(func_name, *params)
        return None

    def join(self, *channels):
        self.send('JOIN {}'.format(','.join(channels)))
        return None

    def add_channel(self, channel):
        new_channel = Channel(channel)
        self.channels[channel] = new_channel
        return None

    def add_user(self, channel, user):
        if channel not in self.channels:
            return None
        self.channels[channel].add_user(user)
        return None

    def remove_user(self, channel, user):
        if channel not in self.channels:
            return None
        self.channels[channel].remove_user(user)
        return None

    @property
    def channel_list(self):
        return iter(self.channels.values())

    def r_PING(self, server):
        self.send('PONG {}'.format(server))
        return None

    def r_001(self, *_):
        for channel in self.join_channels:
            self.send('JOIN {}'.format(channel))
        self.call_decorator('connected')
        return None

    def r_005(self, nickname, *options):
        for option in options:
            if '=' in option:
                key, value = option.split('=')
            else:
                key, value = option, True
            self.server_settings[key] = value
        return None

    def r_JOIN(self, host, channel):
        nickname, host = host[1:].split('!')
        if channel.startswith(':'):
            channel = channel[1:]
        channel = Channel(channel)
        if nickname != self.nickname:
            user = User(nickname, host)
            self.call_decorator('user_join', channel=channel,
                                user=user, host=host)
            self.add_user(channel, user)
        else:
            self.add_channel(channel)
        return None

    def r_PART(self, host, channel, *reason):
        nickname, host = host[1:].split('!')
        channel = self.channels[channel]
        user = channel.remove_user(nickname)
        self.call_decorator('user_part', channel=channel, user=nickname, host=host)
        return None

    def r_QUIT(self, host, *reason):
        nickname, host = host[1:].split('!')
        message = ' '.join(reason)
        self.call_decorator('user_quit', user=nickname, message=message, host=host)
        return None

    def r_NICK(self, host, newnick):
        nickname, host = host[1:].split('!')
        self.call_decorator('user_nick', user=nickname, nick=newnick, host=host)
        return None


    def r_396(self, *_):
        self.call_decorator('identified')
        return None


    def r_366(self, host, nickname, channel, *_):
        self.call_decorator('self_join', channel)
        return None

    def r_PRIVMSG(self, host, channel, *message):
        nickname, host = host[1:].split('!')
        message = ' '.join(message)[1:]
        if channel == self.nickname:
            channel = nickname
        self.call_decorator('privmsg', user=nickname, message=message,
                            channel=channel, host=host)
        return None

    def call_decorator(self, name, *args, **kwargs):
        if name in irc_functions:
            functions = irc_functions[name]
            for function in functions:
                if (self.ref is not None
                and str(self.ref.__class__).startswith('<class')):
                    args = (self.ref, self) + args
                function(*args, **kwargs)
        return None

    def privmsg(self, person, message):
        self.message(person, message)
        return None

    def message(self, person, message):
        self.send('PRIVMSG {} :{}'.format(person, message))
        return None


privmsg = irc_data('privmsg')
self_join = irc_data('self_join')
user_join = irc_data('user_join')
self_part = irc_data('self_part')
user_part = irc_data('user_part')
user_quit = irc_data('user_quit')
user_nick = irc_data('user_nick')
connected = irc_data('connected')
recv_data = irc_data('recv_data')
sent_data = irc_data('sent_data')
identified = irc_data('identified')
