"""
MIT License

Copyright (c) 2019-2020 eibex

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from discord.ext import commands
import sqlite3
from random import randint


def initialize(database):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS 'messages' ('message_id' INT, 'channel' INT,"
        " 'reactionrole_id' INT);"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS 'reactionroles' ('reactionrole_id' INT, 'reaction'"
        " NVCARCHAR, 'role_id' INT);"
    )
    cursor.execute("CREATE TABLE IF NOT EXISTS 'admins' ('role_id' INT);")
    conn.commit()
    cursor.close()
    conn.close()


class ReactionRoleCreationTracker:
    def __init__(self, user, channel, database):
        self.database = database
        initialize(self.database)

        self.user = user
        self.channel = channel
        self.step = 0
        self.target_channel = None
        self.combos = {}
        self.message_id = None
        self._generate_reactionrole_id()

    def _generate_reactionrole_id(self):
        conn = sqlite3.connect(self.database)
        while True:
            self.reactionrole_id = randint(0, 100000)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM messages WHERE reactionrole_id = ?",
                (self.reactionrole_id,),
            )
            already_exists = cursor.fetchall()
            if already_exists:
                continue
            cursor.close()
            conn.close()
            break

    def commit(self):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO 'messages' ('message_id', 'channel', 'reactionrole_id')"
            " values(?, ?, ?);",
            (self.message_id, self.target_channel, self.reactionrole_id),
        )
        for reaction in self.combos:
            role_id = self.combos[reaction]
            cursor.execute(
                "INSERT INTO 'reactionroles' ('reactionrole_id', 'reaction', 'role_id')"
                " values(?, ?, ?);",
                (self.reactionrole_id, reaction, role_id),
            )
        conn.commit()
        cursor.close()
        conn.close()


class Database:
    def __init__(self, database):
        self.database = database
        initialize(self.database)

        self.reactionrole_creation = {}

    def start_creation(self, user, channel):
        tracker = ReactionRoleCreationTracker(user, channel, self.database)
        if f"{user}_{channel}" not in self.reactionrole_creation:
            self.reactionrole_creation[f"{user}_{channel}"] = tracker
            return True
        return False


    def abort(self, user, channel):
        if f"{user}_{channel}" in self.reactionrole_creation:
            del self.reactionrole_creation[f"{user}_{channel}"]
            return True
        return False


    def step(self, user, channel):
        if f"{user}_{channel}" in self.reactionrole_creation:
            tracker = self.reactionrole_creation[f"{user}_{channel}"]
            return tracker.step
        return None


    def get_targetchannel(self, user, channel):
        tracker = self.reactionrole_creation[f"{user}_{channel}"]
        return tracker.target_channel


    def get_combos(self, user, channel):
        tracker = self.reactionrole_creation[f"{user}_{channel}"]
        return tracker.combos


    def step0(self, user, channel):
        tracker = self.reactionrole_creation[f"{user}_{channel}"]
        tracker.step += 1


    def step1(self, user, channel, target_channel):
        tracker = self.reactionrole_creation[f"{user}_{channel}"]
        tracker.target_channel = target_channel
        tracker.step += 1


    def step2(self, user, channel, role=None, reaction=None, done=False):
        tracker = self.reactionrole_creation[f"{user}_{channel}"]
        if not done:
            tracker.combos[reaction] = role
        else:
            tracker.step += 1


    def end_creation(self, user, channel, message_id):
        tracker = self.reactionrole_creation[f"{user}_{channel}"]
        tracker.message_id = message_id
        try:
            tracker.commit()
        except sqlite3.Error as e:
            logging.error(f"Database error occurred: {e}")
            return e
            return e
        del self.reactionrole_creation[f"{user}_{channel}"]


    def exists(self, message_id):
        try:
            conn = sqlite3.connect(self.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM messages WHERE message_id = ?;", (message_id,))
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return result
        except sqlite3.Error as e:
            return e


    def get_reactions(self, message_id):
        try:
            conn = sqlite3.connect(self.database)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT reactionrole_id FROM messages WHERE message_id = ?;", (message_id,)
            )
            reactionrole_id = cursor.fetchall()[0][0]
            cursor.execute(
                "SELECT reaction, role_id FROM reactionroles WHERE reactionrole_id = ?;",
                (reactionrole_id,),
            )
            combos = {}
            for row in cursor:
                reaction = row[0]
                role_id = row[1]
                combos[reaction] = role_id
            cursor.close()
            conn.close()
            return combos
        except sqlite3.Error as e:
            return e


    def fetch_messages(self, channel):
        try:
            conn = sqlite3.connect(self.database)
            cursor = conn.cursor()
            cursor.execute("SELECT message_id FROM messages WHERE channel = ?;", (channel,))
            all_messages_in_channel = []
            for row in cursor:
                message_id = int(row[0])
                all_messages_in_channel.append(message_id)
            cursor.close()
            conn.close()
            return all_messages_in_channel
        except sqlite3.Error as e:
            return e


    def fetch_all_messages(self):
        try:
            conn = sqlite3.connect(self.database)
            cursor = conn.cursor()
            cursor.execute("SELECT message_id, channel FROM messages;")
            all_messages = {}
            for row in cursor:
                message_id = int(row[0])
                channel_id = int(row[1])
                all_messages[message_id] = channel_id
            cursor.close()
            conn.close()
            return all_messages
        except sqlite3.Error as e:
            return e


    def delete(self, message_id):
        try:
            conn = sqlite3.connect(self.database)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT reactionrole_id FROM messages WHERE message_id = ?;", (message_id,)
            )
            reactionrole_id = cursor.fetchall()[0][0]
            cursor.execute("DELETE FROM messages WHERE reactionrole_id = ?;", (reactionrole_id,))
            cursor.execute(
                "DELETE FROM reactionroles WHERE reactionrole_id = ?;", (reactionrole_id,)
            )
            conn.commit()
            cursor.close()
            conn.close()
        except sqlite3.Error as e:
            return e


    def add_admin(self, role):
        try:
            conn = sqlite3.connect(self.database)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO 'admins' ('role_id') values(?);", (role,))
            conn.commit()
            cursor.close()
            conn.close()
        except sqlite3.Error as e:
            return e


    def remove_admin(self, role):
        try:
            conn = sqlite3.connect(self.database)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM admins WHERE role_id = ?;", (role,))
            conn.commit()
            cursor.close()
            conn.close()
        except sqlite3.Error as e:
            return e


    def get_admins(self):
        try:
            conn = sqlite3.connect(self.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admins;")
            admins = []
            for row in cursor:
                role_id = row[0]
                admins.append(role_id)
            cursor.close()
            conn.close()
            return admins
        except sqlite3.Error as e:
            return e

db = Database("dbs/reactionlight.db")

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

class ReactionLight(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	async def step1(self,message):
		bot = self.bot
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

	async def step2(self,message):
		bot = self.bot
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
					"Ты можешь использовать только эмодзи с этого сервера, "
					"либо стандартные эмодзи Discord'а"
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

	async def step3(self, message):
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

	@commands.Cog.listener()
	async def on_message(self, message):
		bot = self.bot

		if not isadmin(message.author): return 

		user = str(message.author.id)
		channel = str(message.channel.id)
		step = db.step(user, channel)
		msg = message.content.split()

		if step is None: return 
		# Checks if the setup process was started before.
		# If it was not, it ignores the message.
		if step == 0: db.step0(user, channel)
		elif step == 1: await self.step1(message)
		elif step == 2: await self.step2(message)
		elif step == 3: await self.step3(message)

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		bot = self.bot
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
		if not exists: return

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


	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		bot = self.bot
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
		if not exists: return

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


	@commands.command(name="rr-new")
	async def new(self, ctx):
		if not isadmin(ctx.message.author):
			return await ctx.send("У вас нет админ роли. Напишите `s!admin` сперва.")

		if started := db.start_creation(
			ctx.message.author.id, ctx.message.channel.id
		):
			await ctx.send("Упомяните #канал, куда я должен отправить сообщение авто-роли.")
		else:
			await ctx.send(
				'Вы уже создаёте авто-роль сообщение. Используйте другой канал или напишите `s!rr-abort` сперва.'
			)
			

	@commands.command(name="rr-abort")
	async def abort(self, ctx):
		if isadmin(ctx.message.author):
			return await ctx.send(f"У вас нет админ роли.")
			
		aborted = db.abort(ctx.message.author.id, ctx.message.channel.id)
		if aborted:
			await ctx.send("Добавление авто-роль сообщения отменено.")
		else:
			await ctx.send(
				"Нет запущенных вами процессов создания роль-реакции сообщения в этом канале."
			)
			


	@commands.command(name="rr-edit")
	async def edit_selector(self, ctx):
		bot = self.bot
		if isadmin(ctx.message.author):
			return await ctx.send("У вас нет админ роли")
			# Reminds user of formatting if it is wrong
		msg_values = ctx.message.content.split()
		if len(msg_values) < 2:
			await ctx.send(
				f"**Напиши** `s!rr-edit #имя-канала` чтобы начать. Замени"
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
					"В этом канале есть только одно сообщение роли-реакции."
					f" **Напиши**:\n```\ns!rr-edit #{channel.name} // 1 // Новое сообщение"
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
					f" канале. **Напиши**:\n```\ns!rr-edit #{channel.name} //"
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
				selector_embed = discord.Embed(colour=botcolour)
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

			


	@commands.command(name="rm-embed")
	async def remove_selector_embed(self, ctx):
		bot = self.bot
		if isadmin(ctx.message.author):
			return await ctx.send("У вас нет админ роли")

		msg_values = ctx.message.content.split()
		if len(msg_values) < 2:
			await ctx.send(
				f"**Напиши** `s!rm-embed #имя-канала` чтобы начать. Замени"
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
					f"\n```\ns!rm-embed #{channel.name} // 1\n```"
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
					f" канале. **Напиши**:\n```\ns!rm-embed #{channel.name} //"
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
							f" сперва измените это сообщение с помощью: \n`s!rr-edit"
							f" #{ctx.message.channel_mentions[0]} //"
							f" {selector_msg_number} // Новое сообщение`"
						)
					else:
						await ctx.send(str(e))

			except IndexError:
				await ctx.send("Канал, который вы упомянули, недействителен.")

			except discord.Forbidden:
				await ctx.send("У меня нет прав на редактирование сообщения.")


	@commands.command(name="rr-admin")
	@commands.has_permissions(administrator=True)
	async def add_admin(self, ctx):
	# Adds an admin role ID to the database
		try:
			role = ctx.message.role_mentions[0].id
		except IndexError:
			try:
				role = int(ctx.message.content.split()[1])
			except (IndexError,ValueError):
				await ctx.send("Укажите сущесвующую @Роль или её ID.")
				return

		add = db.add_admin(role)
		if isinstance(add, Exception):
			await system_notification(
				f"Ошибка базы данных при добавлении нового администратора:\n```\n{add}\n```"
			)
			return
		await ctx.send("Добавил роль в мой список администраторов.")


	@commands.command(name="rm-admin")
	@commands.has_permissions(administrator=True)
	async def remove_admin(self, ctx):
		try:
			role = ctx.message.role_mentions[0].id
		except IndexError:
			try:
				role = int(ctx.message.content.split()[1])
			except (ValueError,IndexError):
				await ctx.send("Укажите сущесвующую @Роль или её ID.")
				return

		remove = db.remove_admin(role)
		if isinstance(remove, Exception):
			await system_notification(
				f"Ошибка базы данных при удалении администратора:\n```\n{remove}\n```"
			)
			return
		await ctx.send("Удалил роль из моего списка администраторов.")


	@commands.command(name="adminlist")
	@commands.has_permissions(administrator=True)
	async def list_admin(self, ctx):
		bot = self.bot
		admin_ids = db.get_admins()
		if isinstance(admin_ids, Exception):
			return await system_notification(
				f"Ошибка базы данных при получении администраторов:\n```\n{admin_ids}\n```"
			)
			
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
			)
		elif local_admins and not foreign_admins:
			await ctx.send(
				"The bot admins on this server are:\n- "
			)
		elif not local_admins and foreign_admins:
			await ctx.send(
				"There are no bot admins on this server."
			)
		else:
			await ctx.send("Нет зарегистрированных администраторов ботов.")
