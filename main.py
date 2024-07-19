import discord
from discord.ext import commands, tasks
import random
from data import *
import os
import utils, time
import asyncio
from cogs import voice, rep, dota, reactionlight, music
import logging
import requests
from dotenv import load_dotenv
from pathlib import Path
import pogoda
Path(DATABASES_FOLDER).mkdir(parents=True, exist_ok=True)

load_dotenv()
logger = logging.getLogger(__name__)
intents = discord.Intents.default()

intents.members = True
intents.message_content = True

from logging.handlers import RotatingFileHandler

handleri = RotatingFileHandler(filename='info.log', encoding='utf-8', mode='a', maxBytes=10485760, backupCount=5)
handleri.setLevel(logging.INFO)
handleri.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
handlers = RotatingFileHandler(filename='error.log', encoding='utf-8', mode='a', maxBytes=10485760, backupCount=5)
handlers.setLevel(logging.ERROR)
handlers.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

logger.addHandler(handleri)
logger.addHandler(handlers)

from discord.gateway import DiscordWebSocket
class MyDiscordWebSocket(DiscordWebSocket):

    async def send_as_json(self, data):
        if data.get('op') == self.IDENTIFY and data.get('d', {}).get('properties', {}).get('$browser') is not None:
            data['d']['properties']['$browser'] = 'Discord Android'
            data['d']['properties']['$device'] = 'Discord Android'

        await super().send_as_json(data)


DiscordWebSocket.from_client = MyDiscordWebSocket.from_client

prefixes = ["s!"]
bot = commands.Bot(command_prefix=prefixes, intents=intents)
bot.http.user_agent = "Discord IOS"
bot.remove_command('help')
				
@bot.event
async def on_ready():
	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="s!help"))
	print("Grouchy is online!")
	
@bot.command()
async def info(ctx):
	embed=discord.Embed(title="Информация", description="E S E S E S E S E S E S E S E S E S E S E S E S E S E S E S E S E S E S E S E S E S E S E S E S", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ", colour=botcolour)
	embed.add_field(name="Kelk", value="https://t.me/itsKelk", inline=True)
	embed.add_field(name="Grouchy", value="https://t.me/grouchy25", inline=True)
	embed.set_footer(icon_url=logo, text=botname)
	await ctx.message.reply(embed=embed)
	

@bot.command()
async def help(ctx):
	embed=discord.Embed(title="Помощь по командам", description="Мой префикс: `s!`",colour=botcolour) #, `s!monika`, `s!yuri`, `s!natsuki`, `s!sayori`
	embed.add_field(name="Мои команды", value="`s!info`, `s!help`, `s!donate`, `s!8ball`, `s!weather`", inline=False)
	embed.add_field(name="Музыка", value="`s!playlist`, `s!join`, `s!summon`, `s!leave`, `s!volume`, `s!now`, `s!pause`, `s!resume`, `s!stop`, `s!skip`, `s!queue`, `s!shuffle`, `s!remove`, `s!loop`, `s!play`", inline=False)
	embed.add_field(name="Утилиты", value="`s!ahelp`")
	embed.set_footer(icon_url=logo, text=botname)
	await ctx.message.reply(embed=embed)

@bot.command()
async def ahelp(ctx):
	embed=discord.Embed(title="Помощь по админ командам", description="Мой префикс: `s!`",colour=botcolour)
	embed.add_field(name="?",value="`s!ping`", inline=False)
	embed.add_field(name="ReactionRoles",value="`s!rr-new`, `s!rr-abort`, `s!rr-edit`, `s!rm-embed`", inline=False)
	embed.add_field(name="Приватные войсы", value="`s!pv-setup` (прописывать владельцу сервера), `s!pv-limit`, `s!pv-lock`, `s!pv-unlock`, `s!pv-allow`, `s!pv-deny`, `s!pv-limit`, `s!pv-name`, `s!pv-claim`", inline=False)
	embed.set_footer(icon_url=logo, text=botname)
	await ctx.message.reply(embed=embed)

	
@bot.command()
async def ping(ctx):
	await ctx.message.reply(f'Понг! За `{round(bot.latency * 1000)}ms` <:SayoriCool:997427409697648690>')
	
@bot.command()
async def donate(ctx):
	await ctx.message.reply("Вы можете безвозмездно нам задонатить по этому адресу: <https://www.donationalerts.com/r/robert300>")
	
	
@bot.command(name="8ball")
async def ball(ctx, *arg):
	embed=discord.Embed(description=f"{ctx.message.author.mention} спросил у магического шара: **"+" ".join(arg)+"**",colour=botcolour)
	embed.add_field(name="Шар ответил:", value=random.choice(ballanswers), inline=False)
	embed.set_footer(icon_url=logo, text=botname)
	await ctx.message.reply(embed=embed)
	
@bot.command()
async def weather(ctx, *args):
	arg = " ".join(args)
	if not arg:
		embed=discord.Embed(description=":warning: Укажите город",colour=botcolour)
		embed.set_footer(icon_url=logo, text=botname)
		await ctx.message.reply(embed=embed)
		return
	try:
		weather = get_weather(arg)
		icon = ":cloud:" if weather.weather.status == "Clouds" else ":sunny:" if weather.weather.status == "Clear" else ":question:"
		embed = discord.Embed(
			description=f"{icon} В городе {weather.location.name} сейчас {weather.weather.detailed_status} ({weather.weather.status})",
			colour=botcolour,
		)
		embed.set_footer(icon_url=logo, text=botname)
		await ctx.message.reply(embed=embed)
	except NotFoundError:
		embed=discord.Embed(description=":warning: Город \""+arg+"\" не найден!",colour=botcolour)
		embed.set_footer(icon_url=logo, text=botname)
		await ctx.message.reply(embed=embed)

@bot.command()
async def vip(ctx):
	vip = utils.check_for_vip(ctx.guild.id)
	if vip < time.time():
		await ctx.message.reply("Випки нету")
	else:
		await ctx.message.reply(f"Випка подключена до <t:{vip}> (истечет <t:{vip}:R>)")


@bot.command()
async def tyan(ctx):
	url = requests.get("https://api.waifu.pics/sfw/waifu").json()['url']
	embed=discord.Embed(title="Тян", description=f"Запрошено {ctx.message.author.mention}", color=botcolour)
	embed.set_image(url=url)
	embed.set_footer(icon_url=logo, text=botname)
	await ctx.message.reply(embed=embed)

@bot.command()
async def neko(ctx):
	url = requests.get("https://nekos.life/api/v2/img/neko").json()['url']
	embed=discord.Embed(title="Неко", description=f"Запрошено {ctx.message.author.mention}", color=botcolour)
	embed.set_image(url=url)
	embed.set_footer(icon_url=logo, text=botname)
	await ctx.message.reply(embed=embed)

	
async def setup_cogs():
	await bot.add_cog(music.Music(bot))
	await bot.add_cog(voice.Voice(bot))
	await bot.add_cog(rep.ReputationCog(bot))
	await bot.add_cog(dota.DotaInfo(bot))
	await bot.add_cog(reactionlight.ReactionLight(bot))
#	await bot.add_cog(speech.Speech(bot))
	#bot.add_cog(icon.ServerIcon(bot))
#	mod.setup(bot)
	#await bot.add_cog(roulette.Game(bot))
	
loop = asyncio.get_event_loop()

asyncio.run(setup_cogs())
	
try:
	loop.run_until_complete(bot.start(os.environ.get("BOT_TOKEN")))
except KeyboardInterrupt:
	loop.run_until_complete(bot.close())
	utils.db.close()
	# cancel all tasks lingering
finally:
	loop.close()

