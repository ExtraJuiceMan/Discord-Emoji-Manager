# -*- coding: utf-8 -*-
import os
import asyncio
import yaml
import requests
import discord
from bs4 import BeautifulSoup

print("""

#####################
DISCORD EMOJI MANAGER
#####################

Import emojis from http://discordemoji.com,
Clear emojis from your server,
or steal emojis from another one!

COMMANDS
-----------
All commands are in your server's text channel.

>addemoji <emoji name> <OPTIONAL name override>
Adds emoji from the Emojis folder to your server. If no optional name is specified,
the command will use the file's name as an emoji alias.

>addfolder <directory name>
Adds all images inside a folder in this script's directory as emojis.

>DEaddemoji <emoji name> <OPTIONAL name override>
Adds emoji from discordemoji.com to your server!

>DEaddcategory <category name>
Adds all emoji from a discordemoji.com category to your server!

>stealemoji <emoji name> <OPTIONL server ID> <OPTIONAL name override>
Steals an emoji from your visible emojis. If you want to target a specific server,
enter a server ID. If you want to change the name, you must enter both
the server ID and the overriden name.

>stealemojis <server id>
Steals all emojis from the specified server!

>clearemojis
Clears all emojis from the current server.

-------------
LOADING...
Do not type commands yet~!
-------------
""")

# DiscordEmoji scraper. cleaning up later.

page = requests.get('http://discordemoji.com/').text
html = BeautifulSoup(page, 'lxml')
cattabs = html.find_all('li', {'role' : 'presentation'})
categories = {}

for c in cattabs:
    a = c.find('a')
    categories[a['href'].replace('#', '')] = a.text

emoji_containers = html.find_all('div', {'role' : 'tabpanel'})
all_emojis = []
for container in emoji_containers:
    emojis = container.find_all('div', {'class' : 'col-md-2'})
    for emoji in emojis:
        emoji_category = categories.get(container['id'])
        emoji_img = 'http://discordemoji.com/' + emoji.find('img')['src']
        emoji_text = emoji.find('div', {'class' : 'emoji-text'}).text
        emoji_name = emoji_text.replace(':', '').replace('-', '_')
        emoji_data = (emoji_text, emoji_name, emoji_img, emoji_category)
        all_emojis.append(emoji_data)

with open('config.yaml', 'r') as f:
    config = yaml.load(f)
client = discord.Client()

@client.event
async def on_message(message):
    global all_emojis
    
    if message.author != client.user:
        return

    if not message.channel.permissions_for(message.author).manage_emojis and msg.startswith('>'):
        print('You do not have permissions to manage emojis in this server!')
        return

    msg = message.content

    if msg.startswith('>addemoji'):
        params = msg.split(' ')
        if len(params) < 2:
            await client.add_reaction(message, '❌')
            print('Invalid arguments. Please read the command guide.')
            return
        emote_name = params[2] if len(params) == 3 else params[1].split('.')[0]
        print('ADDING - ' + emote_name)
        try:
            try:
                f = open('Emojis/{}'.format(params[1]), 'rb')
            except:
                await client.add_reaction(message, '❌')
                print('Error opening {}. Maybe it doesn\'t exist?'.format(params[1]))
                return
            await client.create_custom_emoji(server=message.server, name=emote_name, image=f.read())
            await client.add_reaction(message, '✅')
        except Exception as e:
            await client.add_reaction(message, '❌')
            print('Error adding emoji! | ' + str(e))
            return

    if msg.startswith('>addfolder'):
        params = msg.split(' ')
        if len(params) < 2:
            await client.add_reaction(message, '❌')
            print('Invalid arguments. Please read the command guide.')
            return
        root = os.path.dirname(__file__)
        directory = root + params[1] + '/'
        ext = ('.png', '.jpeg', '.jpg')
        try:
            files = [f for f in os.listdir(directory) if f.endswith(ext)]
        except FileNotFoundError as e:
            await client.add_reaction(message, '❌')
            print('Error adding emojis from {}! Most likely, the directory does not exist.| '.format(params[1]) + str(e))
            return
        for f in files:
            emote_name = f.split('.')[0]
            print('ADDING - ' + emote_name)
            try:
                with open(params[1] + '/' + f, 'rb') as f:
                    await client.create_custom_emoji(server=message.server, name=emote_name, image=f.read())
            except Exception as e:
                print('Error adding {}! | '.format(emote_name) + str(e))
        await client.add_reaction(message, '✅')
        
        
    if msg.startswith('>DEaddemoji'):
        params = msg.split(' ')
        if len(params) < 2:
            await client.add_reaction(message, '❌')
            print('Invalid arguments. Please read the command guide.')
            return
        try:
            selected_emote = [emote for emote in all_emojis if emote[1] == params[1].lower()][0]
        except Exception as e:
            await client.add_reaction(message, '❌')
            print('Invalid emoji! | ' + str(e))
            return
        try:
            emote_name = selected_emote[1] if len(params) != 3 else params[2]
            print('ADDING - ' + emote_name)
            custom_image = requests.get(selected_emote[2]).content
            await client.create_custom_emoji(server=message.server, name=emote_name, image=custom_image)
            await client.add_reaction(message, '✅')
        except Exception as e:
            await client.add_reaction(message, '❌')
            print('Error adding emoji! | ' + str(e))
            return
            
    if msg.startswith('>DEaddcategory'):
        params = msg.split(' ', 1)
        if len(params) < 2:
            await client.add_reaction(message, '❌')
            print('Invalid arguments. Please read the command guide.')
            return
        selected_category = [emote for emote in all_emojis if emote[3].lower() == params[1].lower()]
        if not selected_category:
            await client.add_reaction(message, '❌')
            print('Invalid category!')
            return
        for emote in selected_category:
            try:
                print('ADDING - ' + emote[1])
                custom_image = requests.get(emote[2]).content
                await client.create_custom_emoji(server=message.server, name=emote[1], image=custom_image)
            except Exception as e:
                print('Error for ' + emote[1] + ' | ' + str(e))
        await client.add_reaction(message, '✅')

    if msg.startswith('>clearemojis'):
        try:
            emojis = message.server.emojis
            for emote in emojis:
                print('DELETING - ' + emote.name)
                await client.delete_custom_emoji(emote)
            await client.add_reaction(message, '✅')
        except Exception as e:
            await client.add_reaction(message, '❌')
            print('Error clearing emoji! | ' + str(e))

    if msg.startswith('>stealemojis'):
        params = msg.split(' ', 1)
        if len(params) < 2:
            await client.add_reaction(message, '❌')
            print('Invalid arguments. Please read the command guide.')
            return
        server = client.get_server(params[1])
        for emote in server.emojis:
            try:
                print('ADDING - ' + emote.name)
                custom_image = requests.get(emote.url).content
                await client.create_custom_emoji(server=message.server, name=emote.name, image=custom_image)
            except Exception as e:
                print('Error for ' + emote.name + ' | ' + str(e))
        await client.add_reaction(message, '✅')

    if msg.startswith('>stealemoji'):
        params = msg.split(' ')
        if len(params) < 2:
            await client.add_reaction(message, '❌')
            print('Invalid arguments. Please read the command guide.')
            return
        emotelist = client.get_all_emojis() if len(params) == 2 else client.get_server(params[2])
        if emotelist.emojis is None:
            await client.add_reaction(message, '❌')
            print('Server not found! Enter a proper server ID!')
            return
        stolenemoji = discord.utils.find(lambda e: e.name.lower() == params[1].lower(), emotelist)
        if stolenemoji:
            try:
                print('ADDING - ' + stolenemoji.name)
                emote_name = stolenemoji.name if len(params) < 3 else params[3]
                custom_image = requests.get(stolenemoji.url).content
                await client.create_custom_emoji(server=message.server, name=emote_name, image=custom_image)
            except Exception as e:
                await client.add_reaction(message, '❌')
                print('Error adding emoji! | ' + str(e))
                return
        else:
            await client.add_reaction(message, '❌')
            print('Emoji {} not found!'.format(params[1]))
            return
        await client.add_reaction(message, '✅')

    if msg.startswith('>exit'):
        exit()

@client.event
async def on_ready():  
    print('\nLoaded!')
    print('Logged in as:')
    print(client.user.name)
    print('------\n')
    
client.run(config['email'], config['password'])

