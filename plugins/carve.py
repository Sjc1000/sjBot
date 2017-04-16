#!/usr/bin/env python3


import time
import random


carves = {'1-10': ['Plate', 'Pelt', 'Bone', 'Fang', 'Scale', 'Claw', 'Tail',
          'Wing', 'Talon'], '11-15': ['Ear', 'Fellwing', 'Shard', 'Ripper',
          'Cortex', 'Horn', 'Carapace', 'Marrow'], '16-18': ['Gem', 'Pallium',
          'Heart', '_You were tripped by a Konchu D:',
          '_You were rammed by a Rhenoplos D:', '_You carved through {person} '
          'and carved the dirt underneath. D:']}


class Plugin:

    _name = 'carve'

    def __init__(self, bot):
        self.bot = bot
        bot.register_command(self._name, ['carve'], self.carve,
                             channels=['##monsterhunter'])
        self.times = {}

    def carve(self, server, user, channel, *person):
        """Carves a person"""
        person = ' '.join(person)
        if user.name not in self.times:
            self.times[user.name] = {'time': time.time(), 'count': 0, 'last': 0}

        utime = self.times[user.name]
        utime['time'] = time.time()
        if utime['count'] > 2 and utime['time'] - utime['last'] < 300:
            print( utime['time'] - utime['last'] )
            return None
        elif utime['count'] > 2 and utime['time'] - utime['last'] > 300:
            utime['count'] = 0

        utime['count'] += 1
        utime['last'] = utime['time']

        string = 'You got {person} {item}'
        if person == 'Trump':
            return "You got Trump's hair."
        
        if person == 'Athena':
            return "You got Athena's ASS."

        if person in ['McLown', 'ShadyFigure']:
            return "You couldn't carve anything off."

        number = random.randint(0, 18)
        items = None

        for rarity in carves:
            low = int(rarity.split('-')[0])
            high = int(rarity.split('-')[1])
            if number >= low and number <= high:
                items = carves[rarity]
                break

        if items is None:
            return 'Nothing found! D:'
        
        item = random.choice(items)
        if item.startswith('_'):
            return item[1:].format(person=person)
    
        if person.endswith('s') and not person.endswith('ss'):
            person += "'"
        else:
            person += "'s"

        return string.format(person=person, item=item)
