#!/usr/bin/env python3


import re
import requests
from bs4 import BeautifulSoup


url_regex = '((?:https?://)((?:www\.)?.*?)(?:/|$).*)$'
ignore_nicks = ['DcForum', 'SteBot', 'robokins', 'ForumBot']
ignore_channels = ['##monsterhunter']


class Plugin:
    def __init__(self, bot):
        self.bot = bot
        bot.register_event(__name__, ['PRIVMSG'], self.auto_url)
    
    def auto_url(self, server, host, _, channel, *message):
        nickname, host = host[1:].split('!')
        if channel in ignore_channels or nickname in ignore_nicks:
            return None
        output = []
        message = ' '.join(message)[1:]
        for msg in message.split(' '):
            if msg.strip() == '':
                continue
            match = re.findall(url_regex, msg)
            for url in match:
                full, name = url
                full = full.strip()
                name = name.strip()


                try:
                    req = requests.get(full)
                except requests.exceptions.ConnectionError:
                    output.append('[\x035{}\x03] \x02ConnectionError\x02'.format(name))
                    continue

                new_name = re.search(url_regex, req.url)
                name = new_name.group(2)

                if name.startswith('www.'):
                    name = name.replace('www.', '')

                if name in ['youtube.com', 'youtu.be']:
                    result = handle_youtube(req.url, self.bot.settings['google_key'])
                    output.append(result)
                    continue

                if name == 'github.com':
                    result = handle_github(req.url)
                    output.append(result)
                    continue

                if name == 'p.ahkscript.org':
                    continue

                text = req.text
                soup = BeautifulSoup(text, 'html.parser')
                title = soup.find('title')
                if title is None:
                    return None
                title = repr(title.text.strip('\n '))[1:-1]
                output.append('[\x033{}\x03] \x02{}\x02'.format(name, title))
        if output == []:
            return None
        output = [x.strip('\r\n\t') for x in output if x is not None]
        server.privmsg(channel, '   '.join(output))
        return None


def handle_youtube(url, key):
    video_match = re.search('(yout.*v=|yout.*/)(.*?)(\&|\s+|$|#|\?|\s)', url)
    if video_match == None:
        return '[\x035YouTube\x03] \x02No Match\x02'

    video_id = video_match.group(2).strip()
    req = requests.get('https://www.googleapis.com/youtube/v3/videos?id={}'
                       '&key={}&part=snippet,contentDetails,statistics,'
                       'status'.format(video_id, key))
    data = req.json()
    item = data['items'][0]
    title = item['snippet']['title']
    time = (item['contentDetails']['duration'].replace('PT', '').replace(
            'S', '').replace('H', ':').replace('M', ':').split(':'))
    for i, v in enumerate(time):
        if v == '':
            v = 0
        time[i] = '{0:02d}'.format(int(v))
    time = ':'.join(time)
    if ':' not in time:
        time = time + ' seconds'
    return '[\x033YouTube\x03] \x02{}\x02 - {}'.format(repr(title)[1:-1], time)


def handle_github(url):
    match = re.search('github\.com/(.*?)/(.*?)($|/| )', url)
    user, repo = match.group(1), match.group(2)
    user, repo = user.strip(), repo.strip()
    req = requests.get('https://api.github.com/repos/{}/{}/'
                       'languages'.format(user, repo))
    data = req.json()
    if 'message' in data and data['message'] == 'Not Found':
        return None

    req = requests.get('https://api.github.com/repos/{}/{}'.format(user, repo))
    repo_data = req.json()
    title = repo_data['description'].replace('\n', ' ')
    if len(title) > 50:
        title = title[:50] + '...'
    title = '{} - {}'.format(repo_data['name'], title)
    languages = '/'.join(data.keys())
    title = repr(title)[1:-1]
    languages = repr(languages)[1:-1]
    return '[\x033Github\x03] \x02{}\x02 ({})'.format(title, languages)
