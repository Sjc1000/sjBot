#!/usr/bin/env python3


import inspect


pm_channels = ['##monsterhunter']


class Plugin:
    def __init__(self, bot):
        self.bot = bot
        bot.register_command(__name__, ['help', 'commands'], self.help)

    def help(self, server, user, channel, command=None):
        """Shows le help."""
        if command is None:
            output = self.list_all(server, user, channel)
        else:
            output = self.list_info(server, user, channel, command)

        if channel not in pm_channels:
            return output

        if isinstance(output, list):
            for line in output:
                server.privmsg(user.name, line)
        else:
            server.privmsg(user.name, output)
        return None

    def list_info(self, server, user, channel, command):
        info = self.bot.is_command(command)
        if info is None:
            return 'Could not find that command.'
        ignore = self.bot.ignore_command(channel, info, user)
        if ignore:
            return 'Could not find that command.'
        aliases = info['aliases']
        params = inspect.signature(info['function']).parameters
        param_info = 'Usage: \x02{}\x02'.format(aliases[0])
        for i, p in enumerate(params):
            if i < 3:
                continue
            param_info += ' {}'.format(p)
        docs = inspect.getdoc(info['function'])
        docs = 'Docs: {}'.format(docs)
        return [param_info, docs]

    def list_all(self, server, user, channel):
        cmd_list = []
        for command in self.bot.commands:
            if self.bot.ignore_command(channel, command, user):
                continue
            cmd_list.append(command['aliases'][0])
        cmd_list = sorted(cmd_list)
        return 'Commands: {}.'.format(', '.join(cmd_list))
