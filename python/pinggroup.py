import asyncio

from pinger import Pinger


class PingGroup:
    def __init__(self):
        self.pingers = dict()

    async def add_pinger(self, guild, channel, target_user):
        self.pingers[target_user] = Pinger(guild, channel, target_user)
        await self.pingers[target_user].start_pinging()

    def user_arrived(self, target_user):
        if f"<@{target_user.id}>" in self.pingers:
            self.pingers[f"<@{target_user.id}>"].im_here()

    def force_kill(self, target_user):
        if target_user in self.pingers:
            self.pingers[target_user].force_stop()
