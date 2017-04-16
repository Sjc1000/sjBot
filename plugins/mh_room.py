#!/usr/bin/env python3


import time
import datetime
import re


channels = ['##monsterhunter']


class Plugin:
    def __init__(self, bot):
        self.bot = bot
        self.rooms = {}
        #bot.register_command(__name__, ['room'], self.room, channels=['##monsterhunter'])
        #bot.register_event(__name__, ['PING'], self.check)

    def room(self, server, user, channel, hall, password=None):
        nickname = user.name
        new_channel = '##monsterhunter-{}'.format(nickname)

        if hall in self.rooms:
            server.send('MODE {} -i'.format(new_channel))
        else:
            server.join(new_channel)
        
        self.bot.register_command(new_channel, ['id'], self.show_id,
                                  channels=[new_channel])
        self.bot.register_command(new_channel, ['pass'], self.show_pass,
                                  channels=[new_channel])

        if password is not None:
            server.send('MODE {} +i'.format(new_channel))
            server.send('INVITE {} {}'.format(nickname, new_channel))
            send = '\x02{}\x02 has created a protected room.'.format(nickname)
        else:
            send = ('\x02{0}\x02 has created a room -' 
                    ' ##monsterhunter-{0}'.format(nickname))
        self.rooms[new_channel] = {'id': hall, 'password': password,
                                   'activity': datetime.datetime.now()}
        return send

    def show_id(self, server, user, channel):
        return self.rooms[channel.name]['id']

    def show_pass(self, server, user, channel, new=None):
        if new is not None:
            self.rooms[channel.name]['password'] = new
            return 'New password: {}'.format(new)
        passw = self.rooms[channel.name]['password']
        if passw is None:
            return 'No password set for this hall.'
        return passw

    def check(self, server, *_):
        now = datetime.datetime.now()
        for room in dict(self.rooms):
            activity = self.rooms[room]['activity']
            inactive = now-activity
            if inactive.seconds > 4800:
                server.privmsg(room, 'No activity in {}, quitting.'.format(
                               inactive))
                server.send('MODE {} -i'.format(room))
                del self.rooms[room]
                for item in list(self.bot.commands):
                    if item['ignore'] == [room]:
                        index = self.bot.commands.index(item)
                        del self.bot.commands[index]
        return None
