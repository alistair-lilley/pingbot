import discord
import json
import re

from dotenv import dotenv_values

from pinggroup import PingGroup

config = dotenv_values(".env")

TOKEN = config["TOKEN"]

intents = discord.Intents.all()
intents.message_content = True

dialogs = json.load(open("dialogues.json"))

class Bot(discord.Client):

    async def on_ready(self):
        print(f"WELCOME TO PINGER BOT: {self.user}")
        self.ping_group = PingGroup()

    async def on_message(self, message):
        if message.author == self.user:
            return

        elif message.content.startswith("!ping"):
            content = message.content.split(' ')
            if len(content) < 2:
                await message.channel.send(dialogs["missing_username"])
            elif len(content) > 2:
                await message.channel.send(dialogs["too_many_words"])
            else:
                cmd = content[0]
                target_user = content[1]
                await message.channel.send(re.sub(dialogs["user"], target_user,
                                                  dialogs["starting_ping"]))
                await self.ping_group.add_pinger(message.guild, message.channel,
                                                target_user)
        
        elif message.content.startswith("!stop"):
            content = message.content.split(' ', 2)
            cmd = content[0]
            target_user = content[1]
            self.ping_group.force_kill(target_user)

        elif "here" in message.content.lower():
            self.ping_group.user_arrived(message.author)


if __name__ == "__main__":
    bot = Bot(intents=intents)
    bot.run(TOKEN)