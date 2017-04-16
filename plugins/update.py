#!/usr/bin/env python3


import requests


class Plugin:
    
    _name = 'update'

    def __init__(self, bot):
        self.bot = bot
        bot.register_command(self._name, ['update', 'version'], self.update,
                             ['#ahk', '#ahkscript', '#Sjc_Bot'])

    def update(self, server, user, channel):
        """Links to the AutoHotkey download."""
        req = requests.get('https://autohotkey.com/download/1.1/version.txt')
        version = req.text
        return ('[\x033AutoHotkey\x03] \x02Latest version: v{}\x02 - '
                'http://autohotkey.com/download/ahk-install.exe'.format(version))
