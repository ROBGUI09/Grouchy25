from discord.ext import tasks, commands
from datetime import datetime
import requests

class ServerIcon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.night.start()
        self.day.start()

    def cog_unload(self):
        self.night.cancel()
        self.day.cancel()

    @tasks.loop(time=datetime(8,0,0))
    async def day(self):
        r = requests.get("https://cdn.discordapp.com/attachments/932191860712177664/998565760865681468/unknown.png")
        await bot.edit_server(bot.get_guild(997404296909947001), icon=r.content)
        
    @tasks.loop(time=datetime(18,0,0))
    async def night(self):
        r = requests.get("https://cdn.discordapp.com/attachments/932191860712177664/998565623045050368/unknown.png")
        await bot.edit_server(bot.get_guild(997404296909947001), icon=r.content)
