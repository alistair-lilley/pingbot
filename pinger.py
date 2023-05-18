import asyncio
import time
import json
import re

dialogs = json.load(open("dialogues.json"))

MINUTE = 60

class Pinger:

    def __init__(self, guild, channel, username, timeout_minutes):
        self.target_user = username
        self.guild = guild
        self.channel = channel
        self.timeout_max = timeout_minutes * MINUTE
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
            await self.channel.send(re.sub(dialogs["user"], self.target_user,
                                           dialogs["game_time"]))
            time.sleep(1)
        await self.channel.send(self.end_message)
    
    def im_here(self):
        self.end_message = dialogs["here"]
        self.stop_ping = True
    
    def force_stop(self):
        self.end_message = dialogs["force_stopped"]
        self.stop_ping = True