import discord
from discord.ext import commands
import random
from data import *
from pogoda import get_weather, NotFoundError
import music
import os


token = "OTk3NDIxNjk2Mzg0NTA3OTA0.GcOgBO.JoUxNv2pC22mHEMJT261nAOUPKrZXuShZa0jmA"

bot = commands.Bot(command_prefix=('g!'))
bot.remove_command('help')

@bot.event
async def on_ready():
	chan = bot.get_channel(997789286596366386)
	await chan.send("Бот в сети! :partying_face:")
	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="g!help"))
	
@bot.command()
async def info(ctx):
	embed=discord.Embed(title="Информация", description="Я стал первым приложением,которое было созданно по инициативе Grouchy. На данный момент я являюсь ботом помощником,но возможно скоро вы сможете полноценно со мной поговорить", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ", color=0)
	embed.add_field(name="Kelk", value="https://t.me/ROBGUI09", inline=True)
	embed.add_field(name="Grouchy", value="https://t.me/grouchy25", inline=True)
	embed.set_footer(icon_url="https://cdn.discordapp.com/attachments/932191860712177664/997799046238457956/unknown.png", text="by Grouchy and Kelk")
	await ctx.message.reply(embed=embed)
	
@bot.command()
async def monika(ctx):
	images = [
		"https://cdn.discordapp.com/attachments/932191860712177664/997839931932168272/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997840025498697810/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997840132801560586/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997840511681433691/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997840534984990750/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997840974938128415/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997841175039983616/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997841262960984144/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997841601072214077/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997841652326596738/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997841963627851886/unknown.png"
	]
	embed=discord.Embed(title="Моника", description=f"Запрошено {ctx.message.author.mention}", color=0)
	embed.set_image(url=random.choice(images))
	embed.set_footer(icon_url="https://cdn.discordapp.com/attachments/932191860712177664/997799046238457956/unknown.png", text="by Grouchy and Kelk")
	await ctx.message.reply(embed=embed)

@bot.command()
async def yuri(ctx):
	images = [
		"https://cdn.discordapp.com/attachments/932191860712177664/997842824420659301/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997842856590979163/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997842885057708043/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997842982587879465/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997843380572782703/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997843489079427082/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997843579638661260/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997843719178948668/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997843991104069723/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997844446995562526/unknown.png"
	]
	embed=discord.Embed(title="Юри", description=f"Запрошено {ctx.message.author.mention}", color=0)
	embed.set_image(url=random.choice(images))
	embed.set_footer(icon_url="https://cdn.discordapp.com/attachments/932191860712177664/997799046238457956/unknown.png", text="by Grouchy and Kelk")
	await ctx.message.reply(embed=embed)
	
@bot.command()
async def natsuki(ctx):
	images = [
		"https://cdn.discordapp.com/attachments/932191860712177664/997844940761616495/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997844989591699486/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997845133607305296/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997845346891870339/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997845405360459807/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997845640652542083/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997845808605052988/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997846160683307069/unknown.png",
	]
	embed=discord.Embed(title="Натцуки", description=f"Запрошено {ctx.message.author.mention}", color=0)
	embed.set_image(url=random.choice(images))
	embed.set_footer(icon_url="https://cdn.discordapp.com/attachments/932191860712177664/997799046238457956/unknown.png", text="by Grouchy and Kelk")
	await ctx.message.reply(embed=embed)
	
@bot.command()
async def sayori(ctx):
	images = [
		"https://cdn.discordapp.com/attachments/932191860712177664/997847464004550786/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997847757303857202/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997848061231505438/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997848101048045648/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997848191363973170/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997848714427240538/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997848740301918228/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997849176471781376/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997849455833395210/unknown.png",
		"https://cdn.discordapp.com/attachments/932191860712177664/997850372108451911/unknown.png"
	]
	embed=discord.Embed(title="Сайори", description=f"Запрошено {ctx.message.author.mention}", color=0)
	embed.set_image(url=random.choice(images))
	embed.set_footer(icon_url="https://cdn.discordapp.com/attachments/932191860712177664/997799046238457956/unknown.png", text="by Grouchy and Kelk")
	await ctx.message.reply(embed=embed)
	
@bot.command()
async def hentai(ctx):
	await ctx.message.reply("|| https://cdn.discordapp.com/attachments/997873592303898675/997886931281137826/videoplayback_3.mp4 ||")
	
@bot.command()
async def help(ctx):
	embed=discord.Embed(title="Помощь по командам", description="Мой префикс: `g!`")
	embed.add_field(name="Мои команды", value="`g!info`, `g!help`, `g!monika`, `g!yuri`, `g!natsuki`, `g!sayori`, `g!hentai`, `g!ping`, `g!donate`, `g!hello`, `g!howru`, `g!8ball`, `g!weather`", inline=False)
	embed.set_footer(icon_url="https://cdn.discordapp.com/attachments/932191860712177664/997799046238457956/unknown.png", text="by Grouchy and Kelk")
	await ctx.message.reply(embed=embed)
	
@bot.command()
async def ping(ctx):
	await ctx.message.reply(f'Понг! За `{round(bot.latency * 1000)}ms` <:SayoriCool:997427409697648690>')
	
@bot.command()
async def donate(ctx):
	await ctx.message.reply("Вы можете безвозмездно нам задонатить по этому адресу: <https://www.donationalerts.com/r/robert300> :3")
	
@bot.command()
async def hello(ctx):
	await ctx.message.reply(random.choice(hellotexts))
	
@bot.command()
async def howru(ctx):
	await ctx.message.reply(random.choice(howrutexts))
	
@bot.command(name="8ball")
async def ball(ctx, *arg):
	embed=discord.Embed(description=f"{ctx.message.author.mention} спросил у магического шара: **"+" ".join(arg)+"**")
	embed.add_field(name="Шар ответил:", value=random.choice(ballanswers), inline=False)
	embed.set_footer(icon_url="https://cdn.discordapp.com/attachments/932191860712177664/997799046238457956/unknown.png", text="by Grouchy and Kelk")
	await ctx.message.reply(embed=embed)
	
@bot.command()
async def weather(ctx, *args):
	arg = " ".join(args)
	if arg == "":
		embed=discord.Embed(description=":warning: Укажите город")
		embed.set_footer(icon_url="https://cdn.discordapp.com/attachments/932191860712177664/997799046238457956/unknown.png", text="by Grouchy and Kelk")
		await ctx.message.reply(embed=embed)
		return
	try:
		weather = get_weather(arg)
		icon = ":cloud:" if weather.weather.status == "Clouds" else ":sunny:" if weather.weather.status == "Clear" else ":question:"
		embed=discord.Embed(description=icon+" В городе "+weather.location.name+" сейчас "+weather.weather.detailed_status+" ("+weather.weather.status+")")
		embed.set_footer(icon_url="https://cdn.discordapp.com/attachments/932191860712177664/997799046238457956/unknown.png", text="by Grouchy and Kelk")
		await ctx.message.reply(embed=embed)
	except NotFoundError:
		embed=discord.Embed(description=":warning: Город \""+arg+"\" не найден!")
		embed.set_footer(icon_url="https://cdn.discordapp.com/attachments/932191860712177664/997799046238457956/unknown.png", text="by Grouchy and Kelk")
		await ctx.message.reply(embed=embed)
		

music.setup(bot)
	
bot.run(token)

