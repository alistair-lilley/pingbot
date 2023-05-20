import asyncio
import time
import json
import re
import os

dialogs = json.load(open("dialogues.json"))

MINUTE = 60

class Pinger:

    def __init__(self, guild, channel, username):
        if ("custom_dialogs.json" not in os.listdir() or
                    os.stat("custom_dialogs.json").st_size == 0):
            json.dump({}, open("custom_dialogs.json", 'w'))
        self.guild_vals = json.load(open("custom_dialogs.json"))
        self.target_user = username
        self.guild = guild
        self.channel = channel
        if self.guild in self.guild_vals:
            self.timeout_max = \
                self.guild_vals[str(self.guild.id)]["timeout"] * MINUTE
        else:
            self.timeout_max = dialogs["defaults"]["timeout"] * MINUTE
        self.stop_ping = False
        self.end_message = dialogs["timed_out"]

    async def start_pinging(self):
        if self.guild and not self._verify_user():
            await self.channel.send(re.sub(dialogs["user"], self.target_user,
                                           dialogs["not_in_server"]))
            return 
        start = time.time()
        end = start + self.timeout_max
        asyncio.create_task(self._ping_repeating(end))

    def _verify_user(self):
        ids = [str(memb.id) for memb in self.guild.members]
        return self.target_user[2:-1] in ids
    
    async def _ping_repeating(self, end):
        while time.time() < end and not self.stop_ping:
            if str(self.guild.id) in self.guild_vals:
                msg = self.guild_vals[str(self.guild.id)]["pingmsg"]
            else:
                msg = dialogs["defaults"]["pingmsg"]
            pingmsg = re.sub(dialogs["user"], self.target_user,
                                            dialogs["ping_message"])
            await self.channel.send(msg + pingmsg)
            time.sleep(1)
        await self.channel.send(self.end_message)
    
    def im_here(self):
        if str(self.guild.id) in self.guild_vals:
            self.end_message = self.guild_vals[str(self.guild.id)]["heremsg"]
        else:
            self.end_message = dialogs["defaults"]["heremsg"]
        self.stop_ping = True
    
    def force_stop(self):
        self.end_message = dialogs["force_stopped"]
        self.stop_ping = True