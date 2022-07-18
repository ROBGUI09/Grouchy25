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
import logging
import discord_logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

logger.addHandler(handler)

token = "OTk3NDIxNjk2Mzg0NTA3OTA0.GcOgBO.JoUxNv2pC22mHEMJT261nAOUPKrZXuShZa0jmA"

bot = commands.Bot(command_prefix=('g!'))
bot.remove_command('help')

db = database.Database("../reactionlight.db")
botcolour = 0
botname = "By Grouchy and Kelk"
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
	chan = bot.get_channel(997789286596366386)
	await chan.send("Бот в сети! :partying_face:")
	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="g!help"))
	print("Grouchy is online!")
	
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
		await ctx.message.reply("Випки нема :<")
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
							"I cannot read or send messages in that channel."
						)
						return
				except IndexError:
					await message.channel.send("The channel you mentioned is invalid.")
					return

				db.step1(user, channel, target_channel)
				await message.channel.send(
					"Attach roles and emojis separated by one space (one combination"
					" per message). When you are done type `done`. Example:\n:smile:"
					" `@Role`"
				)
			elif step == 2:
				if msg[0].lower() != "done":
					# Stores reaction-role combinations until "done" is received
					try:
						reaction = msg[0]
						role = message.role_mentions[0].id
						await message.add_reaction(reaction)
						db.step2(user, channel, role, reaction)
					except IndexError:
						await message.channel.send(
							"Mention a role after the reaction. Example:\n:smile:"
							" `@Role`"
						)
					except discord.HTTPException:
						await message.channel.send(
							"You can only use reactions uploaded to this server or"
							" standard emojis."
						)
				else:
					# Advances to step three
					db.step2(user, channel, done=True)

					selector_embed = discord.Embed(
						title="Embed_title",
						description="Embed_content",
						colour=botcolour,
					)
					selector_embed.set_footer(text=f"{botname}", icon_url=logo)
					await message.channel.send(
						"What would you like the message to say?\nFormatting is:"
						" `Message // Embed_title // Embed_content`.\n\n`Embed_title`"
						" and `Embed_content` are optional. You can type `none` in any"
						" of the argument fields above (e.g. `Embed_title`) to make the"
						" bot ignore it.\n\n\nMessage",
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
							"I don't have permission to send selector_msg messages to"
							f" the channel {target_channel.mention}."
						)
					if isinstance(selector_msg, discord.Message):
						combos = db.get_combos(user, channel)
						error = db.end_creation(user, channel, selector_msg.id)
						if error and system_channel:
							await message.channel.send(
								"I could not commit the changes to the database. Check"
								f" {system_channel.mention} for more information."
							)
							await system_notification(
								f"Database error:\n```\n{error}\n```"
							)
						elif error:
							await message.channel.send(
								"I could not commit the changes to the database."
							)
						for reaction in combos:
							try:
								await selector_msg.add_reaction(reaction)
							except discord.Forbidden:
								await message.channel.send(
									"I don't have permission to react to messages from"
									f" the channel {target_channel.mention}."
								)
				else:
					await message.channel.send(
						"You can't use an empty message as a role-reaction message."
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
			f"Database error after a user added a reaction:\n```\n{exists}\n```"
		)
		return
	elif exists:
		# Checks that the message that was reacted to is a reaction-role message managed by the bot
		reactions = db.get_reactions(msg_id)
		if isinstance(reactions, Exception):
			await system_notification(
				f"Database error when getting reactions:\n```\n{reactions}\n```"
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
						"Someone tried to add a role to themselves but I do not have"
						" permissions to add it. Ensure that I have a role that is"
						" hierarchically higher than the role I have to assign, and"
						" that I have the `Manage Roles` permission."
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
			f"Database error after a user removed a reaction:\n```\n{exists}\n```"
		)
		return
	elif exists:
		# Checks that the message that was unreacted to is a reaction-role message managed by the bot
		reactions = db.get_reactions(msg_id)
		if isinstance(reactions, Exception):
			await system_notification(
				f"Database error when getting reactions:\n```\n{reactions}\n```"
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
					"Someone tried to remove a role from themselves but I do not have"
					" permissions to remove it. Ensure that I have a role that is"
					" hierarchically higher than the role I have to remove, and that I"
					" have the `Manage Roles` permission."
				)


@bot.command(name="rr-new")
async def new(ctx):
	if isadmin(ctx.message.author):
		# Starts setup process and the bot starts to listen to the user in that channel
		# For future prompts (see: "async def on_message(message)")
		started = db.start_creation(ctx.message.author.id, ctx.message.channel.id)
		if started:
			await ctx.send("Mention the #channel where to send the auto-role message.")
		else:
			await ctx.send(
				"You are already creating a reaction-role message in this channel. "
				f"Use another channel or run `g!abort` first."
			)
	else:
		await ctx.send(
			f"You do not have an admin role. You might want to use `g!admin`"
			" first."
		)


@bot.command(name="rr-abort")
async def abort(ctx):
	if isadmin(ctx.message.author):
		# Aborts setup process
		aborted = db.abort(ctx.message.author.id, ctx.message.channel.id)
		if aborted:
			await ctx.send("Reaction-role message creation aborted.")
		else:
			await ctx.send(
				"There are no reaction-role message creation processes started by you"
				" in this channel."
			)
	else:
		await ctx.send(f"You do not have an admin role.")


@bot.command(name="rr-edit")
async def edit_selector(ctx):
	if isadmin(ctx.message.author):
		# Reminds user of formatting if it is wrong
		msg_values = ctx.message.content.split()
		if len(msg_values) < 2:
			await ctx.send(
				f"**Type** `g!edit #channelname` to get started. Replace"
				" `#channelname` with the channel where the reaction-role message you"
				" wish to edit is located."
			)
			return
		elif len(msg_values) == 2:
			try:
				channel_id = ctx.message.channel_mentions[0].id
			except IndexError:
				await ctx.send("You need to mention a channel.")
				return

			all_messages = db.fetch_messages(channel_id)
			if isinstance(all_messages, Exception):
				await system_notification(
					f"Database error when fetching messages:\n```\n{all_messages}\n```"
				)
				return
			channel = bot.get_channel(channel_id)
			if len(all_messages) == 1:
				await ctx.send(
					"There is only one reaction-role message in this channel."
					f" **Type**:\n```\ng!edit #{channel.name} // 1 // New Message"
					" // New Embed Title (Optional) // New Embed Description"
					" (Optional)\n```\nto edit the reaction-role message. You can type"
					" `none` in any of the argument fields above (e.g. `New Message`)"
					" to make the bot ignore it."
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
							"I do not have permissions to edit a reaction-role message"
							f" that I previously created.\n\nID: {msg_id} in"
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
					f"There are **{len(all_messages)}** reaction-role messages in this"
					f" channel. **Type**:\n```\ng!edit #{channel.name} //"
					" MESSAGE_NUMBER // New Message // New Embed Title (Optional) //"
					" New Embed Description (Optional)\n```\nto edit the desired one."
					" You can type `none` in any of the argument fields above (e.g."
					" `New Message`) to make the bot ignore it. The list of the"
					" current reaction-role messages is:\n\n"
					+ "\n".join(selector_msgs)
				)
			else:
				await ctx.send("There are no reaction-role messages in that channel.")
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
						"Database error when fetching"
						f" messages:\n```\n{all_messages}\n```"
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
						"You selected a reaction-role message that does not exist."
					)
					return

				if message_to_edit_id:
					old_msg = await channel.fetch_message(int(message_to_edit_id))
				else:
					await ctx.send(
						"Select a valid reaction-role message number (i.e. the number"
						" to the left of the reaction-role message content in the list"
						" above)."
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
					await ctx.send("Message edited.")
				else:
					await ctx.send(
						"You can't use an empty message as role-reaction message."
					)

			except IndexError:
				await ctx.send("The channel you mentioned is invalid.")

			except discord.Forbidden:
				await ctx.send("I do not have permissions to edit the message.")

	else:
		await ctx.send("You do not have an admin role.")


@bot.command(name="rm-embed")
async def remove_selector_embed(ctx):
	if isadmin(ctx.message.author):
		# Reminds user of formatting if it is wrong
		msg_values = ctx.message.content.split()
		if len(msg_values) < 2:
			await ctx.send(
				f"**Type** `g!rm-embed #channelname` to get started. Replace"
				" `#channelname` with the channel where the reaction-role message you"
				" wish to remove its embed is located."
			)
			return
		elif len(msg_values) == 2:
			try:
				channel_id = ctx.message.channel_mentions[0].id
			except IndexError:
				await ctx.send("The channel you mentioned is invalid.")
				return

			channel = bot.get_channel(channel_id)
			all_messages = db.fetch_messages(channel_id)
			if isinstance(all_messages, Exception):
				await system_notification(
					f"Database error when fetching messages:\n```\n{all_messages}\n```"
				)
				return
			if len(all_messages) == 1:
				await ctx.send(
					"There is only one reaction-role message in this channel. **Type**:"
					f"\n```\ng!rm-embed #{channel.name} // 1\n```"
					"\nto remove the reaction-role message's embed."
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
							"I do not have permissions to edit a reaction-role message"
							f" that I previously created.\n\nID: {msg_id} in"
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
					f"There are **{len(all_messages)}** reaction-role messages in this"
					f" channel. **Type**:\n```\ng!rm-embed #{channel.name} //"
					" MESSAGE_NUMBER\n```\nto remove its embed. The list of the"
					" current reaction-role messages is:\n\n"
					+ "\n".join(selector_msgs)
				)
			else:
				await ctx.send("There are no reaction-role messages in that channel.")
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
						"Database error when fetching"
						f" messages:\n```\n{all_messages}\n```"
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
						"You selected a reaction-role message that does not exist."
					)
					return

				if message_to_edit_id:
					old_msg = await channel.fetch_message(int(message_to_edit_id))
				else:
					await ctx.send(
						"Select a valid reaction-role message number (i.e. the number"
						" to the left of the reaction-role message content in the list"
						" above)."
					)
					return

				try:
					await old_msg.edit(embed=None)
					await ctx.send("Embed Removed.")
				except discord.HTTPException as e:
					if e.code == 50006:
						await ctx.send(
							"You can't remove an embed if its message is empty. Please"
							f" edit the message first with: \n`g!edit"
							f" #{ctx.message.channel_mentions[0]} //"
							f" {selector_msg_number} // New Message`"
						)
					else:
						await ctx.send(str(e))

			except IndexError:
				await ctx.send("The channel you mentioned is invalid.")

			except discord.Forbidden:
				await ctx.send("I do not have permissions to edit the message.")

	else:
		await ctx.send("You do not have an admin role.")

@bot.command(name="admin")
@commands.has_permissions(administrator=True)
async def add_admin(ctx):
	# Adds an admin role ID to the database
	try:
		role = ctx.message.role_mentions[0].id
	except IndexError:
		try:
			role = int(ctx.message.content.split()[1])
		except ValueError:
			await ctx.send("Please mention a valid @Role or role ID.")
			return
		except IndexError:
			await ctx.send("Please mention a @Role or role ID.")
			return
	add = db.add_admin(role)
	if isinstance(add, Exception):
		await system_notification(
			f"Database error when adding a new admin:\n```\n{add}\n```"
		)
		return
	await ctx.send("Added the role to my admin list.")


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
			await ctx.send("Please mention a valid @Role or role ID.")
			return
		except IndexError:
			await ctx.send("Please mention a @Role or role ID.")
			return
	remove = db.remove_admin(role)
	if isinstance(remove, Exception):
		await system_notification(
			f"Database error when removing an admin:\n```\n{remove}\n```"
		)
		return
	await ctx.send("Removed the role from my admin list.")


@bot.command(name="adminlist")
@commands.has_permissions(administrator=True)
async def list_admin(ctx):
	# Lists all admin IDs in the database, mentioning them if possible
	admin_ids = db.get_admins()
	if isinstance(admin_ids, Exception):
		await system_notification(
			f"Database error when fetching admins:\n```\n{admin_ids}\n```"
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
			"The bot admins on this server are:\n- "
			+ "\n- ".join(local_admins)
			+ "\n\nThe bot admins from other servers are:\n- "
			+ "\n- ".join(foreign_admins)
		)
	elif local_admins and not foreign_admins:
		await ctx.send(
			"The bot admins on this server are:\n- "
			+ "\n- ".join(local_admins)
			+ "\n\nThere are no bot admins from other servers."
		)
	elif not local_admins and foreign_admins:
		await ctx.send(
			"There are no bot admins on this server.\n\nThe bot admins from other"
			" servers are:\n- "
			+ "\n- ".join(foreign_admins)
		)
	else:
		await ctx.send("There are no bot admins registered.")

bot.add_cog(music.Music(bot))
bot.add_cog(voice.Voice(bot))
	
loop = asyncio.get_event_loop()
	
try:
	loop.run_until_complete(bot.start(token))
except KeyboardInterrupt:
	loop.run_until_complete(bot.close())
	utils.db.close()
	# cancel all tasks lingering
finally:
	loop.close()

