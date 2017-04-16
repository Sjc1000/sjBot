#!/usr/bin/env python3


class Plugin:
    def __init__(self, bot):
        self.bot = bot
        bot.register_command('paste', ['paste', 'p'], self.link,
                             ['#ahk', '#ahkscript'])

    def link(self, server, user, channel):
        return ('Paste your code in the official AutoHotkey pastebin -'
                ' http://p.ahkscript.org/')
