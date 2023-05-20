import discord
import json
import re
import sys
import os

from dotenv import dotenv_values

from pinggroup import PingGroup

config = dotenv_values(".env")

TOKEN = config["TOKEN"]
ALI = config["ALI"]

intents = discord.Intents.all()
intents.message_content = True

dialogs = json.load(open("dialogues.json"))
if ("custom_dialogs.json" not in os.listdir() or
            os.stat("custom_dialogs.json").st_size == 0):
    json.dump({}, open("custom_dialogs.json", 'w'))
guild_vals = json.load(open("custom_dialogs.json"))

class Bot(discord.Client):

    async def on_ready(self):
        print(f"WELCOME TO PINGER BOT: {self.user}")
        self.ping_group = PingGroup()
        self.commands = {
            "!help" : self.help,
            "!ping" : self.ping,
            "!stop" : self.stop,
            "!pingmsg" : self.change_ping_msg,
            "!heremsg" : self.change_here_msg,
            "!maxtime" : self.max_time
        }

    async def on_message(self, message):

        if (message.author == self.user or
             (not message.guild and message.author.id != ALI)):
            return

        elif message.content == "!shutdown" and str(message.author.id) == ALI:
            await message.channel.send(dialogs["shutting_down"])
            sys.exit()

        elif message.content.startswith('!'):
            await self.commands[message.content.split()[0]](message)

        elif "here" in message.content.lower():
            await self.here(message)
    
    async def help(self, message):
        if message.channel.name != "ping":
            await message.channel.send(dialogs["wrong_channel"])
            return
        helpmsg = open("help.txt").read()
        await message.channel.send(helpmsg)

    async def ping(self, message):
        if message.channel.name != "ping":
            await message.channel.send(dialogs["wrong_channel"])
            return
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
    
    async def stop(self, message):
        if message.channel.name != "ping":
            return
        content = message.content.split(' ', 2)
        cmd = content[0]
        target_user = content[1]
        self.ping_group.force_kill(target_user)

    async def change_ping_msg(self, message):
        if message.channel.name != "ping":
            await message.channel.send(dialogs["wrong_channel"])
            return
        content = message.content.split(' ', 1)
        if len(content[1]) > 500:
            await message.channel.send(dialogs["message_too_long"])
        else:
            if str(message.guild.id) not in guild_vals:
                guild_vals[str(message.guild.id)] = {
                    "pingmsg": content[1],
                    "heremsg": dialogs["defaults"]["heremsg"],
                    "timeout": dialogs["defaults"]["timeout"]
                    }
            else:
                guild_vals[str(message.guild.id)]["pingmsg"] = content[1]
            json.dump(guild_vals, open("custom_dialogs.json", 'w'))
            await message.channel.send(dialogs["message_changed"])
        
    async def change_here_msg(self, message):
        if message.channel.name != "ping":
            await message.channel.send(dialogs["wrong_channel"])
            return
        content = message.content.split(' ', 1)
        if len(content[1]) > 500:
            await message.channel.send(dialogs["message_too_long"])
        else:
            if str(message.guild.id) not in guild_vals:
                guild_vals[str(message.guild.id)] = {
                    "pingmsg": dialogs["defaults"]["pingmsg"],
                    "heremsg": content[1],
                    "timeout": dialogs["defaults"]["timeout"]
                    }
            else:
                guild_vals[str(message.guild.id)]["heremsg"] = content[1]
            json.dump(guild_vals, open("custom_dialogs.json", 'w'))
            await message.channel.send(dialogs["message_changed"])
        
    async def max_time(self, message):
        if message.channel.name != "ping":
            await message.channel.send(dialogs["wrong_channel"])
            return
        content = message.content.split()
        if len(content) != 2:
            await message.channel.send(dialogs["no_timeout_value"])
        elif not content[1].isdigit():
            await message.channel.send(dialogs["timeout_must_be_int"])
        elif not (1 < int(content[1]) < 15):
            await message.channel.send(dialogs["too_long_or_short"])
        else:
            if str(message.guild.id) not in guild_vals:
                guild_vals[str(message.guild.id)] = {
                    "pingmsg": dialogs["defaults"]["pingmsg"],
                    "heremsg": dialogs["defaults"]["heremsg"],
                    "timeout": int(content[1])
                    }
            else:
                guild_vals[str(message.guild.id)]["timeout"] = int(content[1])
            json.dump(guild_vals, open("custom_dialogs.json", 'w'))
            await message.channel.send(dialogs["maxtime_changed"])

    async def here(self, message):
        if message.channel.name != "ping":
            return
        self.ping_group.user_arrived(message.author)       




if __name__ == "__main__":
    bot = Bot(intents=intents)
    bot.run(TOKEN)
