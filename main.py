from classes.storage import IpStore, ChannelCache

import asyncio
import discord
import logging
import time
import os
import re

# Initialises runtime logging (async)
def setup_logger():
  logger = logging.getLogger('discord')
  logger.setLevel(logging.DEBUG)
  handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
  handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
  logger.addHandler(handler)

# Secret Key Retrieval
def get_secret_key():
  with open('secret.key') as f:
    return f.readline()
  
# Instantiate bot client
client = discord.Client()
token = get_secret_key()

# Instantiate the storage for ip checks
ip_store = IpStore()
channel_cache = ChannelCache()

# Settings
periodic_checks = True
interval = 3600         #seconds

# Checks the connection periodicly
async def check_connection_loop(channel, interval, loop_amount=1000):
  for _ in range(loop_amount):
    if ip_store.get_ip() is None:
      await channel.send("<@168036364913344512> set your server ip with '>test <ip>'")
      return
    
    is_online, num_players = ip_store.check_ip()
    if is_online:
      cur_time = time.localtime(time.time())
      await channel.send(f"[{cur_time[3]}:{cur_time[4]}] Hello peeps, the server is currently online at {ip_store.get_ip()}, with {num_players} player(s) online!")
    else:
      await channel.send('Server is down <@168036364913344512> - get yo ass on it')
    await asyncio.sleep(interval)

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  channel = await channel_cache.get_channel(client)
  if periodic_checks and not channel is None:
    await check_connection_loop(channel, interval)

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  
  if message.content.startswith('>help'):
    await message.channel.send('Commands:\n```>check - Checks if a certain ip is online (and sets it as the default for hourly checks)\n>on9   - Checks if the server is online (and number of players)```')
  
  if message.content.startswith('>check'):
    channel_cache.set_channel_id(message.channel.id)
    match = re.search("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", message.content)
    
    if match is None:
      await message.channel.send('No ip address found (e.g. >check 192.168.0.1)')
    
    if ip_store.set_ip(match.group()):
      await message.channel.send("It's up, good job berayan~")
    else:
      await message.channel.send('Server is down <@168036364913344512> - get yo ass on it')
    
  if message.content.startswith('>on9'):
    is_online, num_players = ip_store.check_ip()
    if is_online:
      cur_time = time.localtime(time.time())
      await message.channel.send(f"[{cur_time[3]}:{cur_time[4]}] Hello peeps, the server is currently online at {ip_store.get_ip()}, with {num_players} player(s) online!")
    else:
      await message.channel.send('Server is down <@168036364913344512> - get yo ass on it')

client.run(token)