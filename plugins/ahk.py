#!/usr/bin/env python3


import json
import difflib
import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import process


url = 'http://ahk4.us/docs/'
ignore = ['_', '.']


class Plugin:
    
    _name = 'autohotkey'

    def __init__(self, bot):
        self.bot = bot
        bot.register_command(self._name, ['docs'], self.docs,
                             ['!##monsterhunter'])
        bot.register_command(self._name, ['info'], self.info,
                             ['!##monsterhunter'])

    def docs(self, server, user, channel, *query):
        """Queries the AutoHotkey docs"""
        if query[0][0] in ignore:
            return None
        item = self.search(query)
        if item is None:
            return '[\x035AutoHotkey\x03] \x02Nothing found\x02'
        return '[\x033AutoHotkey\x03] {}{}'.format(url, item)

    def info(self, server, user, channel, *query):
        """Gets information about a command or function."""
        item = self.search(query)
        if item is None:
            return '[\x035AutoHotkey\x03] \x02Nothing found\x02'
        req = requests.get('{}{}'.format(url, item))
        soup = BeautifulSoup(req.text, 'html.parser')
        desc = soup.find('p').text
        syntax = soup.find('pre', {'class': 'Syntax'}).text
        syntax = syntax.splitlines()[0]
        return [desc, syntax]

    def search(self, query):
        with open('plugins/docs.json', 'r') as f:
            docs = json.loads(f.read())


        query = ' '.join(query).strip().lower()
        replace = '()'

        # Check if it matches any of the urls.
        for item in docs:
            check = item.lower()
            for char in replace:
                check = check.replace(char, '')
            if query == check:
                return docs[item]
            name, ext = docs[item].split('.')
            if query == name.lower():
                return docs[item]

        matches = process.extractOne(query, docs.keys())
        if matches != []:
            chosen = matches[0]
            return docs[chosen]
        return None
