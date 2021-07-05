import os
from mcstatus import MinecraftServer

def mc_check(ip):
  server = MinecraftServer.lookup(ip)
  if server is None:
    return False, 0
  status = server.status()
  return True, status.players.online

def ping_check(ip, attempts=1):
  response = os.system("ping -n 1 " + ip)
  return response == 0

class ChannelCache():
  def __init__(self, save_location='channel.txt'):
    self.save_location = save_location
    self.channel_id = None
    self.load_from_file()
    
  def save_to_file(self, channel_id):
    with open(self.save_location, 'w') as f:
      f.write(str(channel_id))
  
  def load_from_file(self):
    if not os.path.exists(self.save_location):
      return False
    with open(self.save_location, 'r') as f:
      self.channel_id = f.readline()
    return True

  async def get_channel(self, client):
    if self.channel_id is None:
      return None
    return await client.fetch_channel(self.channel_id)
  
  def set_channel_id(self, channel_id):
    self.channel_id = channel_id
    self.save_to_file(channel_id)
  
class IpStore():
  def __init__(self, save_location="current_ip.txt"):
    self.save_location = save_location
    self.ip = None
    self.load_from_file()
    
  def save_to_file(self):
    if self.check_ip()[0]:
      with open(self.save_location, 'w') as f:
        f.write(self.ip)
      return True
    else:
      return False
  
  def load_from_file(self):
    if not os.path.exists(self.save_location):
      return False
    with open(self.save_location, 'r') as f:
      self.ip = f.readline()
    return True

  def set_ip(self, ip):
    if not mc_check(ip)[0]:
      return False

    self.ip = ip
    self.save_to_file()
    return True
  
  def get_ip(self):
    return self.ip
  
  def check_ip(self):
    return mc_check(self.ip)