from discord.ext import tasks, commands
from datetime import datetime
import requests
import schedule
import asyncio

class ServerIcon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.days = schedule.every().day.at("08:00").do(asyncio.run(day))
        self.nights = schedule.every().day.at("18:00").do(asyncio.run(night))

    def cog_unload(self):
        del self.days
        del self.nights

    async def day(self):
        r = requests.get("https://cdn.discordapp.com/attachments/932191860712177664/998565760865681468/unknown.png")
        await bot.edit_server(bot.get_guild(997404296909947001), icon=r.content)
        
    async def night(self):
        r = requests.get("https://cdn.discordapp.com/attachments/932191860712177664/998565623045050368/unknown.png")
        await bot.edit_server(bot.get_guild(997404296909947001), icon=r.content)
