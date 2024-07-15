import discord
from discord.ext import commands, tasks
import random
from data import *
from pogoda import get_weather, NotFoundError
import music
import os
import utils, time
import asyncio
import database
import voice
#import icon
import logging
#import discord_logging
#import speech
import mod
import requests
import roulette
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger()
intents = discord.Intents.default()

intents.members = True
intents.message_content = True

handleri = logging.FileHandler(filename='info.log', encoding='utf-8', mode='a')
handleri.setLevel(logging.INFO)
handleri.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
handlers = logging.FileHandler(filename='error.log', encoding='utf-8', mode='a')
handlers.setLevel(logging.ERROR)
handlers.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

logger.addHandler(handleri)
logger.addHandler(handlers)

token = os.environ.get("BOT_TOKEN")

from discord.gateway import DiscordWebSocket


class MyDiscordWebSocket(DiscordWebSocket):

    async def send_as_json(self, data):
        if data.get('op') == self.IDENTIFY:
            if data.get('d', {}).get('properties', {}).get('$browser') is not None:
                data['d']['properties']['$browser'] = 'Discord Android'
                data['d']['properties']['$device'] = 'Discord Android'
        await super().send_as_json(data)


DiscordWebSocket.from_client = MyDiscordWebSocket.from_client

bot = commands.Bot(command_prefix=('g!'),intents=intents)
bot.http.user_agent = "Discord IOS"
bot.remove_command('help')

db = database.Database("reactionlight.db")
botcolour = 0
botname = "От Grouchy И Kelk'а"
logo = "https://cdn.discordapp.com/attachments/932191860712177664/997799046238457956/unknown.png"

def system_notification(data):
	print(data)

def isadmin(user):
	# Checks if command author has an admin role that was added with rl!admin
	admins = db.get_admins()
	if isinstance(admins, Exception):
		return False
	try:
		user_roles = [role.id for role in user.roles]
		return [admin_role for admin_role in admins if admin_role in user_roles]
	except AttributeError:
		# Error raised from 'fake' users, such as webhooks
		return False
				
@bot.event
async def on_ready():
#	chan = bot.get_channel(997789286596366386)
#	await chan.send("Бот в сети! :partying_face:")
	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="g!help"))
	print("Grouchy is online!")
	
@bot.command()
async def info(ctx):
	embed=discord.Embed(title="Информация", description="Я стал первым приложением,которое было созданно по инициативе Grouchy. На данный момент я являюсь ботом помощником,но возможно скоро вы сможете полноценно со мной поговорить", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ", color=0)
	embed.add_field(name="Kelk", value="https://t.me/itsKelk", inline=True)
	embed.add_field(name="Grouchy", value="https://t.me/grouchy25", inline=True)
	embed.set_footer(icon_url="https://cdn.discordapp.com/attachments/932191860712177664/997799046238457956/unknown.png", text="by Grouchy and Kelk")
	await ctx.message.reply(embed=embed)
	

@bot.command()
async def help(ctx):
	embed=discord.Embed(title="Помощь по командам", description="Мой префикс: `g!`") #, `g!monika`, `g!yuri`, `g!natsuki`, `g!sayori`
	embed.add_field(name="Мои команды", value="`g!info`, `g!help`, `g!hentai`, `g!ping`, `g!donate`, `g!hello`, `g!howru`, `g!8ball`, `g!weather`", inline=False)
	embed.add_field(name="Музыка", value="`g!join`, `g!summon`, `g!leave`, `g!volume`, `g!now`, `g!pause`, `g!resume`, `g!stop`, `g!skip`, `g!queue`, `g!shuffle`, `g!remove`, `g!loop`, `g!play`", inline=False)
	embed.add_field(name="Reaction Roles", value="`g!rr-new`, `g!rr-abort`, `g!rr-edit`, `g!rm-embed`", inline=False)
	embed.add_field(name="Приватные войсы", value="`g!pv-setup` (прописывать владельцу сервера), `g!pv-limit`, `g!pv-lock`, `g!pv-unlock`, `g!pv-allow`, `g!pv-deny`, `g!pv-limit`, `g!pv-name`, `g!pv-claim`", inline=False)
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
		
@bot.command()
async def vip(ctx):
	vip = utils.check_for_vip(ctx.guild.id)
	if vip < time.time():
		await ctx.message.reply("Випки нету")
	else:
		await ctx.message.reply(f"Випка подключена до <t:{vip}> (истечет <t:{vip}:R>)")
		
		
@bot.event
async def on_message(message):
	await bot.process_commands(message)

	if isadmin(message.author):
		user = str(message.author.id)
		channel = str(message.channel.id)
		step = db.step(user, channel)
		msg = message.content.split()

		if step is not None:
			# Checks if the setup process was started before.
			# If it was not, it ignores the message.
			if step == 0:
				db.step0(user, channel)
			elif step == 1:
				# The channel the message needs to be sent to is stored
				# Advances to step two
				try:
					server = bot.get_guild(message.guild.id)
					bot_user = server.get_member(bot.user.id)
					target_channel = message.channel_mentions[0].id
					bot_permissions = bot.get_channel(target_channel).permissions_for(
						bot_user
					)
					writable = bot_permissions.read_messages
					readable = bot_permissions.view_channel
					if not writable or not readable:
						await message.channel.send(
							"Я не могу читать или писать сообщения в этом канале."
						)
						return
				except IndexError:
					await message.channel.send("Канал который вы указали не существует.")
					return

				db.step1(user, channel, target_channel)
				await message.channel.send(
					"Прикрепи роли и эмодзи, разделённые одним пробелом (одна комбинация за сообщение). "
					"Когда закончишь, напиши `готово`. Пример:\n:smile:"
					" `@Роль`"
				)
			elif step == 2:
				if msg[0].lower() != "готово":
					# Stores reaction-role combinations until "done" is received
					try:
						reaction = msg[0]
						role = message.role_mentions[0].id
						await message.add_reaction(reaction)
						db.step2(user, channel, role, reaction)
					except IndexError:
						await message.channel.send(
							"Упомяни роль после реакции. Пример:\n:smile:"
							" `@Роль`"
						)
					except discord.HTTPException:
						await message.channel.send(
							"Ты можешь использовать только эмодзи с этого сервера, либо стандартные эмодзи Discord'а"
						)
				else:
					# Advances to step three
					db.step2(user, channel, done=True)

					selector_embed = discord.Embed(
						title="Заглавие_сообщения",
						description="Подпись_сообщения",
						colour=botcolour,
					)
					selector_embed.set_footer(text=f"{botname}", icon_url=logo)
					await message.channel.send(
						"Что вы хотите видеть в сообщение?\nФорматирование таково:"
						" `Текст // Заглавие_сообщения // Подпись_сообщения`.\n\n`Заглавие_сообщения`"
						" и `Подпись_сообщения` опциональные. Вы можете написать `none` в любой"
						" из аргументов команды (например `Заглавие_сообщения`) чтобы бот"
						" проигнорировал их.\n\n\nТекст",
						embed=selector_embed,
					)
			elif step == 3:
				# Receives the title and description of the reaction-role message
				# If the formatting is not correct it reminds the user of it
				msg_values = message.content.split(" // ")
				selector_msg_body = (
					msg_values[0] if msg_values[0].lower() != "none" else None
				)
				selector_embed = discord.Embed(colour=botcolour)
				selector_embed.set_footer(text=f"{botname}", icon_url=logo)
				if len(msg_values) > 1:

					if msg_values[1].lower() != "none":
						selector_embed.title = msg_values[1]
					if len(msg_values) > 2 and msg_values[2].lower() != "none":
						selector_embed.description = msg_values[2]

				# Prevent sending an empty embed instead of removing it
				selector_embed = (
					selector_embed
					if selector_embed.title or selector_embed.description
					else None
				)

				if selector_msg_body or selector_embed:
					target_channel = bot.get_channel(
						db.get_targetchannel(user, channel)
					)
					selector_msg = None
					try:
						selector_msg = await target_channel.send(
							content=selector_msg_body, embed=selector_embed
						)
					except discord.Forbidden:
						await message.channel.send(
							"У меня нет прав для отправки сообщений в"
							f" {target_channel.mention}."
						)
					if isinstance(selector_msg, discord.Message):
						combos = db.get_combos(user, channel)
						error = db.end_creation(user, channel, selector_msg.id)
						if error and system_channel:
							await message.channel.send(
								"Я не могу вписать это в базу данных. Проверьте"
								f" {system_channel.mention} для большей информации."
							)
							await system_notification(
								f"Ошибка датабазы:\n```\n{error}\n```"
							)
						elif error:
							await message.channel.send(
								"Я не могу вписать это в базу данных."
							)
						for reaction in combos:
							try:
								await selector_msg.add_reaction(reaction)
							except discord.Forbidden:
								await message.channel.send(
									"У меня нет прав чтобы реагироать на сообщения"
									f" в канале {target_channel.mention}."
								)
				else:
					await message.channel.send(
						"Нельзя использовать пустой текст для сообщения."
					)


@bot.event
async def on_raw_reaction_add(payload):
	reaction = str(payload.emoji)
	msg_id = payload.message_id
	ch_id = payload.channel_id
	user_id = payload.user_id
	guild_id = payload.guild_id
	exists = db.exists(msg_id)
	if isinstance(exists, Exception):
		await system_notification(
			f"Ошибка датабазы после того как пользователь добавил реакцию:\n```\n{exists}\n```"
		)
		return
	elif exists:
		# Checks that the message that was reacted to is a reaction-role message managed by the bot
		reactions = db.get_reactions(msg_id)
		if isinstance(reactions, Exception):
			await system_notification(
				f"Ошибка датабазы при получении реакций:\n```\n{reactions}\n```"
			)
			return
		ch = bot.get_channel(ch_id)
		msg = await ch.fetch_message(msg_id)
		user = bot.get_user(user_id)
		if reaction not in reactions:
			# Removes reactions added to the reaction-role message that are not connected to any role
			await msg.remove_reaction(reaction, user)
		else:
			# Gives role if it has permissions, else 403 error is raised
			role_id = reactions[reaction]
			server = bot.get_guild(guild_id)
			member = server.get_member(user_id)
			role = discord.utils.get(server.roles, id=role_id)
			if user_id != bot.user.id:
				try:
					await member.add_roles(role)
				except discord.Forbidden:
					await system_notification(
						"Кто-то пытался добавить себе роль, но у меня нет прав для ее добавления."
						" Убедитесь, что у меня есть роль, которая иерархически выше, чем роль, "
						"которую я должен назначить, и что у меня есть разрешение `Управление ролями`."
					)


@bot.event
async def on_raw_reaction_remove(payload):
	reaction = str(payload.emoji)
	msg_id = payload.message_id
	user_id = payload.user_id
	guild_id = payload.guild_id
	exists = db.exists(msg_id)
	if isinstance(exists, Exception):
		await system_notification(
			f"Ошибка базы данных после того, как пользователь удалил реакцию:\n```\n{exists}\n```"
		)
		return
	elif exists:
		# Checks that the message that was unreacted to is a reaction-role message managed by the bot
		reactions = db.get_reactions(msg_id)
		if isinstance(reactions, Exception):
			await system_notification(
				f"Ошибка базы данных при получении реакций:\n```\n{reactions}\n```"
			)
			return
		if reaction in reactions:
			role_id = reactions[reaction]
			# Removes role if it has permissions, else 403 error is raised
			server = bot.get_guild(guild_id)
			member = server.get_member(user_id)
			role = discord.utils.get(server.roles, id=role_id)
			try:
				await member.remove_roles(role)
			except discord.Forbidden:
				await system_notification(
						"Кто-то пытался добавить себе роль, но у меня нет прав для ее добавления."
						" Убедитесь, что у меня есть роль, которая иерархически выше, чем роль, "
						"которую я должен назначить, и что у меня есть разрешение `Управление ролями`."
				)


@bot.command(name="rr-new")
async def new(ctx):
	if isadmin(ctx.message.author):
		# Starts setup process and the bot starts to listen to the user in that channel
		# For future prompts (see: "async def on_message(message)")
		started = db.start_creation(ctx.message.author.id, ctx.message.channel.id)
		if started:
			await ctx.send("Упомяните #канал, куда я должен отправить сообщение авто-роли.")
		else:
			await ctx.send(
				"Вы уже создаёте авто-роль сообщение. "
				f"Используйте другой канал или напишите `g!rr-abort` сперва."
			)
	else:
		await ctx.send(
			f"У вас нет админ роли. Напишите `g!admin` сперва."
		)


@bot.command(name="rr-abort")
async def abort(ctx):
	if isadmin(ctx.message.author):
		# Aborts setup process
		aborted = db.abort(ctx.message.author.id, ctx.message.channel.id)
		if aborted:
			await ctx.send("Добавление авто-роль сообщения отменено.")
		else:
			await ctx.send(
				"Нет запущенных вами процессов создания роль-реакции сообщения в этом канале."
			)
	else:
		await ctx.send(f"У вас нет админ роли.")


@bot.command(name="rr-edit")
async def edit_selector(ctx):
	if isadmin(ctx.message.author):
		# Reminds user of formatting if it is wrong
		msg_values = ctx.message.content.split()
		if len(msg_values) < 2:
			await ctx.send(
				f"**Напиши** `g!rr-edit #имя-канала` чтобы начать. Замени"
				" `#имя-канала` на канал, в котором находится сообщение роль-реакции сообщения, которое вы хотите отредактировать."
			)
			return
		elif len(msg_values) == 2:
			try:
				channel_id = ctx.message.channel_mentions[0].id
			except IndexError:
				await ctx.send("Вам нужно упомянуть канал.")
				return

			all_messages = db.fetch_messages(channel_id)
			if isinstance(all_messages, Exception):
				await system_notification(
					f"Ошибка базы данных при получении сообщений:\n```\n{all_messages}\n```"
				)
				return
			channel = bot.get_channel(channel_id)
			if len(all_messages) == 1:
				await ctx.send(
					"В этом канале есть только одно сообщение ролm-реакции."
					f" **Напиши**:\n```\ng!rr-edit #{channel.name} // 1 // Новое сообщение"
					" // Новый заголовок (Опционально) // Новая подпись заголовка"
					" (Опционально)\n```\nчтобы редактировать сообщение роль-реакции. Вы также можете вписать"
					" `none` в любой из аргументов выше"
					" чтобы бот проигнорировал их."
				)
			elif len(all_messages) > 1:
				selector_msgs = []
				counter = 1
				for msg_id in all_messages:
					try:
						old_msg = await channel.fetch_message(int(msg_id))
					except discord.NotFound:
						# Skipping reaction-role messages that might have been deleted without updating CSVs
						continue
					except discord.Forbidden:
						ctx.send(
							"У меня нет прав на редактирование сообщения роль-реакции"
							f" которое я создал ранее.\n\nID: {msg_id} в"
							f" {channel.mention}"
						)
						continue
					entry = (
						f"`{counter}`"
						f" {old_msg.embeds[0].title if old_msg.embeds else old_msg.content}"
					)
					selector_msgs.append(entry)
					counter += 1

				await ctx.send(
					f"Здесь **{len(all_messages)}** сообщений роль-реакции в этом"
					f" канале. **Напиши**:\n```\ng!rr-edit #{channel.name} //"
					" НОМЕР_СООБЩЕНИЯ // Новое сообщение"
					" // Новый заголовок (Опционально) // Новая подпись заголовка \n```\nчтобы отредактировать нужное сообщение."
					" Вы также можете вписать"
					" `none` в любой из аргументов выше"
					" чтобы бот проигнорировал их. Список"
					" текущих сообщений роль-реакции:\n\n"
					+ "\n".join(selector_msgs)
				)
			else:
				await ctx.send("В этом канале нет сообщений роль-реакции.")
		elif len(msg_values) > 2:
			try:
				# Tries to edit the reaction-role message
				# Raises errors if the channel sent was invalid or if the bot cannot edit the message
				channel_id = ctx.message.channel_mentions[0].id
				channel = bot.get_channel(channel_id)
				msg_values = ctx.message.content.split(" // ")
				selector_msg_number = msg_values[1]
				all_messages = db.fetch_messages(channel_id)
				if isinstance(all_messages, Exception):
					await system_notification(
						"Ошибка базы данных при получении сообщений:"
						f"\n```\n{all_messages}\n```"
					)
					return
				counter = 1

				# Loop through all msg_ids and stops when the counter matches the user input
				if all_messages:
					message_to_edit_id = None
					for msg_id in all_messages:
						if str(counter) == selector_msg_number:
							message_to_edit_id = msg_id
							break
						counter += 1
				else:
					await ctx.send(
						"Вы выбрали сообщение роль-реакции, которое не существует."
					)
					return

				if message_to_edit_id:
					old_msg = await channel.fetch_message(int(message_to_edit_id))
				else:
					await ctx.send(
						"Выберите допустимый номер сообщения роль-реакции "
						"(т.е. номер слева от содержимого сообщения роли реакции в списке выше)."
					)
					return

				await old_msg.edit(suppress=False)
				selector_msg_new_body = (
					msg_values[2] if msg_values[2].lower() != "none" else None
				)
				selector_embed = discord.Embed()
				if len(msg_values) == 3 and old_msg.embeds:
					selector_embed = old_msg.embeds[0]
				if len(msg_values) > 3 and msg_values[3].lower() != "none":
					selector_embed.title = msg_values[3]
					selector_embed.colour = botcolour
					if old_msg.embeds and len(msg_values) == 4:
						selector_embed.description = old_msg.embeds[0].description
				if len(msg_values) > 4 and msg_values[4].lower() != "none":
					selector_embed.description = msg_values[4]
					selector_embed.colour = botcolour

				# Prevent sending an empty embed instead of removing it
				selector_embed = (
					selector_embed
					if selector_embed.title or selector_embed.description
					else None
				)

				if selector_msg_new_body or selector_embed:
					await old_msg.edit(
						content=selector_msg_new_body, embed=selector_embed
					)
					await ctx.send("Сообщение изменено.")
				else:
					await ctx.send(
						"Вы не можете использовать пустое сообщение в качестве сообщения роль-реакции."
					)

			except IndexError:
				await ctx.send("Канал, который вы упомянули, недействителен..")

			except discord.Forbidden:
				await ctx.send("У меня нет прав на редактирование данного сообщения.")

	else:
		await ctx.send("У вас нет админ роли")


@bot.command(name="rm-embed")
async def remove_selector_embed(ctx):
	if isadmin(ctx.message.author):
		# Reminds user of formatting if it is wrong
		msg_values = ctx.message.content.split()
		if len(msg_values) < 2:
			await ctx.send(
				f"**Напиши** `g!rm-embed #имя-канала` чтобы начать. Замени"
				" `#имя-канала` на канал, где сообщение роль-реакции вы"
				" хотите убрать."
			)
			return
		elif len(msg_values) == 2:
			try:
				channel_id = ctx.message.channel_mentions[0].id
			except IndexError:
				await ctx.send("Канал, который вы упомянули, недействителен.")
				return

			channel = bot.get_channel(channel_id)
			all_messages = db.fetch_messages(channel_id)
			if isinstance(all_messages, Exception):
				await system_notification(
					f"Ошибка базы данных при получении сообщений:\n```\n{all_messages}\n```"
				)
				return
			if len(all_messages) == 1:
				await ctx.send(
					"В этом канале есть только одно сообщение роль-реакции. **Напиши**:"
					f"\n```\ng!rm-embed #{channel.name} // 1\n```"
					"\nчтобы убрать эмбед с этого сообщения."
				)
			elif len(all_messages) > 1:
				selector_msgs = []
				counter = 1
				for msg_id in all_messages:
					try:
						old_msg = await channel.fetch_message(int(msg_id))
					except discord.NotFound:
						# Skipping reaction-role messages that might have been deleted without updating the DB
						continue
					except discord.Forbidden:
						ctx.send(
							"У меня нет прав чтобы изменять сообщение"
							f" которое я раньше создал.\n\nID: {msg_id} в"
							f" {channel.mention}"
						)
						continue
					entry = (
						f"`{counter}`"
						f" {old_msg.embeds[0].title if old_msg.embeds else old_msg.content}"
					)
					selector_msgs.append(entry)
					counter += 1

				await ctx.send(
					f"Здесь **{len(all_messages)}** сообщений авто-роли в этом"
					f" канале. **Напиши**:\n```\ng!rm-embed #{channel.name} //"
					" НОМЕР_СООБЩЕНИЯ\n```\nчтобы убрать конкретный. Текущий список"
					" авто-роль сообщений:\n\n"
					+ "\n".join(selector_msgs)
				)
			else:
				await ctx.send("В этом канале нет авто-роль сообщений.")
		elif len(msg_values) > 2:
			try:
				# Tries to edit the reaction-role message
				# Raises errors if the channel sent was invalid or if the bot cannot edit the message
				channel_id = ctx.message.channel_mentions[0].id
				channel = bot.get_channel(channel_id)
				msg_values = ctx.message.content.split(" // ")
				selector_msg_number = msg_values[1]
				all_messages = db.fetch_messages(channel_id)
				if isinstance(all_messages, Exception):
					await system_notification(
						"Ошибка датабазы при измененеии"
						f" сообщений:\n```\n{all_messages}\n```"
					)
					return
				counter = 1

				# Loop through all msg_ids and stops when the counter matches the user input
				if all_messages:
					message_to_edit_id = None
					for msg_id in all_messages:
						if str(counter) == selector_msg_number:
							message_to_edit_id = msg_id
							break
						counter += 1
				else:
					await ctx.send(
						"Вы выбрали сообщение которое не существует."
					)
					return

				if message_to_edit_id:
					old_msg = await channel.fetch_message(int(message_to_edit_id))
				else:
					await ctx.send(
						"Выберите допустимый номер сообщения роль-реакции "
						"(т.е. номер слева от содержимого сообщения роли реакции в списке выше)."
					)
					return

				try:
					await old_msg.edit(embed=None)
					await ctx.send("Эмбед удалён.")
				except discord.HTTPException as e:
					if e.code == 50006:
						await ctx.send(
							"Вы не можете удалить эмбед, если ее сообщение пусто. Пожалуйста"
							f" сперва измените это сообщение с помощью: \n`g!rr-edit"
							f" #{ctx.message.channel_mentions[0]} //"
							f" {selector_msg_number} // Новое сообщение`"
						)
					else:
						await ctx.send(str(e))

			except IndexError:
				await ctx.send("Канал, который вы упомянули, недействителен.")

			except discord.Forbidden:
				await ctx.send("У меня нет прав на редактирование сообщения.")

	else:
		await ctx.send("У вас нет админ роли")

@bot.command(name="rr-admin")
@commands.has_permissions(administrator=True)
async def add_admin(ctx):
	# Adds an admin role ID to the database
	try:
		role = ctx.message.role_mentions[0].id
	except IndexError:
		try:
			role = int(ctx.message.content.split()[1])
		except ValueError:
			await ctx.send("Укажите сущесвующую @Роль или её ID.")
			return
		except IndexError:
			await ctx.send("Укажите сущесвующую @Роль или её ID.")
			return
	add = db.add_admin(role)
	if isinstance(add, Exception):
		await system_notification(
			f"Ошибка базы данных при добавлении нового администратора:\n```\n{add}\n```"
		)
		return
	await ctx.send("Добавил роль в мой список администраторов.")


@bot.command(name="rm-admin")
@commands.has_permissions(administrator=True)
async def remove_admin(ctx):
	# Removes an admin role ID from the database
	try:
		role = ctx.message.role_mentions[0].id
	except IndexError:
		try:
			role = int(ctx.message.content.split()[1])
		except ValueError:
			await ctx.send("Укажите сущесвующую @Роль или её ID.")
			return
		except IndexError:
			await ctx.send("Укажите сущесвующую @Роль или её ID.")
			return
	remove = db.remove_admin(role)
	if isinstance(remove, Exception):
		await system_notification(
			f"Ошибка базы данных при удалении администратора:\n```\n{remove}\n```"
		)
		return
	await ctx.send("Удалил роль из моего списка администраторов.")


@bot.command(name="adminlist")
@commands.has_permissions(administrator=True)
async def list_admin(ctx):
	# Lists all admin IDs in the database, mentioning them if possible
	admin_ids = db.get_admins()
	if isinstance(admin_ids, Exception):
		await system_notification(
			f"Ошибка базы данных при получении администраторов:\n```\n{admin_ids}\n```"
		)
		return
	server = bot.get_guild(ctx.message.guild.id)
	local_admins = []
	foreign_admins = []
	for admin_id in admin_ids:
		role = discord.utils.get(server.roles, id=admin_id)
		if role is not None:
			local_admins.append(role.mention)
		else:
			foreign_admins.append(f"`{admin_id}`")

	if local_admins and foreign_admins:
		await ctx.send(
			"Админы бота на этом сервере:\n- "
			+ "\n- ".join(local_admins)
#			+ "\n\nThe bot admins from other servers are:\n- "
#			+ "\n- ".join(foreign_admins)
		)
	elif local_admins and not foreign_admins:
		await ctx.send(
			"The bot admins on this server are:\n- "
#			+ "\n- ".join(local_admins)
#			+ "\n\nThere are no bot admins from other servers."
		)
	elif not local_admins and foreign_admins:
		await ctx.send(
			"There are no bot admins on this server."
#			"\n\nThe bot admins from other"
#			" servers are:\n- "
#			+ "\n- ".join(foreign_admins)
		)
	else:
		await ctx.send("Нет зарегистрированных администраторов ботов.")

@bot.command()
async def tyan(ctx):
	url = requests.get("https://api.waifu.pics/sfw/waifu").json()['url']
	embed=discord.Embed(title="Тян", description=f"Запрошено {ctx.message.author.mention}", color=0)
	embed.set_image(url=url)
	embed.set_footer(icon_url="https://cdn.discordapp.com/attachments/932191860712177664/997799046238457956/unknown.png", text="by Grouchy and Kelk")
	await ctx.message.reply(embed=embed)

@bot.command()
async def neko(ctx):
	url = requests.get("https://nekos.life/api/v2/img/neko").json()['url']
	embed=discord.Embed(title="Неко", description=f"Запрошено {ctx.message.author.mention}", color=0)
	embed.set_image(url=url)
	embed.set_footer(icon_url="https://cdn.discordapp.com/attachments/932191860712177664/997799046238457956/unknown.png", text="by Grouchy and Kelk")
	await ctx.message.reply(embed=embed)

	
async def setup_cogs():
	await bot.add_cog(music.Music(bot))
	await bot.add_cog(voice.Voice(bot))
#	await bot.add_cog(speech.Speech(bot))
	#bot.add_cog(icon.ServerIcon(bot))
	mod.setup(bot)
	await bot.add_cog(roulette.Game(bot))
	
loop = asyncio.get_event_loop()

asyncio.run(setup_cogs())
	
try:
	loop.run_until_complete(bot.start(token))
except KeyboardInterrupt:
	loop.run_until_complete(bot.close())
	utils.db.close()
	# cancel all tasks lingering
finally:
	loop.close()

