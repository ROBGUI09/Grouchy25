import discord
from discord.ext import commands
import sqlite3
import json
import datetime
import asyncio
import re

botcolour = 16734003

def str_time_to_seconds(str_time, language='ru'):
    if str_time == "": return (None, "вечно")

    conv_dict = {
        'w': 'weeks',
        'week': 'weeks',
        'weeks': 'weeks',
        'н': 'weeks',
        'нед': 'weeks',
        'неделя': 'weeks',
        'недели': 'weeks',
        'недель': 'weeks',
        'неделю': 'weeks',

        'd': 'days',
        'day': 'days',
        'days': 'days',
        'д': 'days',
        'день': 'days',
        'дня': 'days',
        'дней': 'days',

        'h': 'hours',
        'h': 'hours',
        'hour': 'hours',
        'hours': 'hours',
        'ч': 'hours',
        'час': 'hours',
        'часа': 'hours',
        'часов': 'hours',

        'm': 'minutes',
        'min': 'minutes',
        'mins': 'minutes',
        'minute': 'minutes',
        'minutes': 'minutes',
        'мин': 'minutes',
        'минута': 'minutes',
        'минуту': 'minutes',
        'минуты': 'minutes',
        'минут': 'minutes',

        's': 'seconds',
        'sec': 'seconds',
        'secs': 'seconds',
        'second': 'seconds',
        'seconds': 'seconds',
        'сек': 'seconds',
        'секунда': 'seconds',
        'секунду': 'seconds',
        'секунды': 'seconds',
        'секунд': 'seconds'
    }

    pat = r'[0-9]+[w|week|weeks|н|нед|неделя|недели|недель|неделю|d|day|days|д|день|дня|дней|h|hour|hours|ч|час|часа|часов|min|mins|minute|minutes|мин|минута|минуту|минуты|минут|s|sec|secs|second|seconds|c|сек|секунда|секунду|секунды|секунд]{1}'
    def timestr_to_dict(tstr):
        #convert 1d2h3m4s to {"d": 1, "h": 2, "m": 3, "s": 4}
        return {conv_dict[p[-1]]: int(p[:-1]) for p in re.findall(pat, str_time)}

    def timestr_to_seconds(tstr):
        return datetime.timedelta(**timestr_to_dict(tstr)).total_seconds()

    def plural(n, arg):
        days = []
        if language == "ru":
            if arg == 'weeks':
                days = ['неделя', 'недели', 'недель']
            elif arg == 'days':
                days = ['день', 'дня', 'дней']
            elif arg == 'hours':
                days = ['час', 'часа', 'часов']
            elif arg == 'minutes':
                days = ['минута', 'минуты', 'минут']
            elif arg == 'seconds':
                days = ['секунда', 'секунды', 'секунд']
        elif language == "en":
            if arg == 'weeks':
                days = ['week', 'weeks', 'weeks']        
            elif arg == 'days':
                days = ['day', 'day', 'days']
            elif arg == 'hours':
                days = ['hour', 'hour', 'hours']
            elif arg == 'minutes':
                days = ['minute', 'minute', 'minutes']
            elif arg == 'seconds':
                days = ['second', 'second', 'seconds']

        if n % 10 == 1 and n % 100 != 11:
            p = 0
        elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
            p = 1
        else:
            p = 2
        return f'{str(n)} {days[p]}'

    counter_in_str = ""
    for i in timestr_to_dict(str_time).items():
        counter_in_str += f"{plural(i[1], i[0])} "

    return int(timestr_to_seconds(str_time)), counter_in_str


class ReputationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect('dbs/reputation.db')
        self.cursor = self.db.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS reputation (
                user_id INTEGER PRIMARY KEY,
                positive TEXT,
                negative TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS punishments (
                user_id INTEGER,
                type TEXT,
                duration INTEGER,
                reason TEXT,
                expires_at INTEGER,
                PRIMARY KEY (user_id, type)
            )
        """)
        self.db.commit()

        # Запускаем задачу для проверки истечения наказаний
        self.check_punishments_task = None

    async def cog_before_invoke(self, ctx: commands.Context):
        if self.check_punishments_task is None:
            self.check_punishments_task = self.bot.loop.create_task(self.check_punishments())
            print("ran checker")

    def parse_duration(self, duration):
        return str_time_to_seconds(duration)

    async def check_punishments(self):
        """
        Проверка истечения наказаний.
        """
        while True:
            self.cursor.execute("SELECT user_id, type, expires_at FROM punishments WHERE expires_at IS NOT NULL AND expires_at <= ?", (datetime.datetime.now(datetime.timezone.utc).timestamp(),))
            punishments = self.cursor.fetchall()

            for user_id, type, expires_at in punishments:
                if type == "ban":
                    try:
                        member = await self.bot.fetch_user(user_id)
                        await self.bot.http.unban(self.bot.get_guild(member.guild.id).id, user_id)
                    except discord.HTTPException:
                        pass
                elif type == "mute":
                    try:
                        member = await self.bot.fetch_user(user_id)
                        guild = self.bot.get_guild(member.guild.id)

                        await guild.get_member(user_id).edit(mute=False, reason="Срок мута истек")
                    except discord.HTTPException:
                        pass
                elif type == "kick":
                    try:
                        member = await self.bot.fetch_user(user_id)
                        guild = self.bot.get_guild(member.guild.id)
                        await guild.unban(member, reason="Срок кика истек")
                    except discord.HTTPException:
                        pass

                self.cursor.execute("DELETE FROM punishments WHERE user_id = ? AND type = ?", (user_id, type))
                self.db.commit()

            await asyncio.sleep(5)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, duration: str, *, reason=None):
        try:
            duration, sdur = self.parse_duration(duration)
            if duration:
                # Создаем временный инвайт
                invite = await ctx.channel.create_invite(max_age=0, max_uses=1, unique=True)
                await member.send(f"Кажется, тебя забанили, но это временно! Твой бан истечёт через {dur}; вот твой личный вечный одноразовый инвайт: {invite.url}")

            await member.ban(reason=reason, delete_message_days=0)
            await ctx.send(f"Пользователь {member.mention} забанен на {sdur}. Причина: {reason}")

            expires_at = datetime.datetime.now(datetime.timezone.utc) + duration if duration else None
            self.cursor.execute("INSERT OR REPLACE INTO punishments (user_id, type, duration, reason, expires_at) VALUES (?, ?, ?, ?, ?)", (member.id, "ban", duration.total_seconds() if duration else None, reason, expires_at.timestamp()))
            self.db.commit()

        except discord.Forbidden:
            await ctx.send("У меня нет прав на бан этого пользователя.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member: discord.Member, duration: str, *, reason=None):
        try:
            duration, sdur = self.parse_duration(duration)

            await member.edit(mute=True, reason=reason)
            await ctx.send(f"**Silence!** Пользователь {member.mention} замучен на {sdur}. Причина: {reason}")

            expires_at = datetime.datetime.now(datetime.timezone.utc) + duration if duration else None
            self.cursor.execute("INSERT OR REPLACE INTO punishments (user_id, type, duration, reason, expires_at) VALUES (?, ?, ?, ?, ?)", (member.id, "mute", duration.total_seconds() if duration else None, reason, expires_at.timestamp()))
            self.db.commit()

        except discord.Forbidden:
            await ctx.send("У меня нет прав на мут этого пользователя.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member: discord.Member, *, reason=None):
        try:
            await member.edit(mute=False, reason=reason)
            await ctx.send(f"Пользователь {member.mention} размучен. Причина: {reason}")

            # Удаляем информацию о муте из базы данных
            self.cursor.execute("DELETE FROM punishments WHERE user_id = ? AND type = ?", (member.id, "mute"))
            self.db.commit()
        except discord.Forbidden:
            await ctx.send("У меня нет прав на размут этого пользователя.")

    @commands.command()
    async def report(self, ctx, member: discord.Member, *, reason=None):
        if reason is None:
            reason = "No reason provided"

        owner = ctx.guild.owner
        embed = discord.Embed(title="Репорт", color=discord.Color.red())
        embed.add_field(name="От", value=ctx.author.mention, inline=False)
        embed.add_field(name="Зарепорченный пользователь", value=member.mention, inline=False)
        embed.add_field(name="Причина", value=reason, inline=False)
        embed.add_field(name="Сообщение", value=ctx.message.content, inline=False)
        if ctx.message.reference:
            repmsg = await message.channel.fetch_message(message.reference.message_id)
            embed.add_field(name="Зарепорченное сообщение", value=repmsg.content, inline=False)
            embed.add_field(name="Прикрепленные файлы", value=f"[{', '.join(a.filename for a in repmsg.attachments)}]({', '.join(a.url for a in repmsg.attachments)})", inline=False)
        if ctx.message.attachments:
            embed.add_field(name="Прикрепленные файлы репорта", value=f"[{', '.join(a.filename for a in ctx.message.attachments)}]({', '.join(a.url for a in ctx.message.attachments)})", inline=False)
        await owner.send(embed=embed)
        await ctx.send(f"Пользователь {member.mention} был зарепорчен.")

    @commands.command(name='+rep')
    async def positive_rep(self, ctx, member: discord.Member, *, reason=None):
        if member.id == ctx.author.id:
            await ctx.send("Ты не можешь голосовать за себя!")
            return

        if any(n["id"] == ctx.author.id for n in json.loads(self.get_negative(member.id))):
            await ctx.send("Ты уже голосовал за этого участника! `=rep`")
            return

        self.cursor.execute(
            "SELECT positive FROM reputation WHERE user_id = ?", (member.id,)
        )
        positive = self.cursor.fetchone()

        if positive is None:
            positive = json.dumps([{"id": ctx.author.id, "reason": reason}])
        else:
            positive = json.loads(positive[0])
            if any(p["id"] == ctx.author.id for p in positive):
                await ctx.send("Ты уже голосовал за этого участника! `=rep`")
                return
            positive.append({"id": ctx.author.id, "reason": reason})
            positive = json.dumps(positive)

        self.cursor.execute(
            "INSERT OR REPLACE INTO reputation (user_id, positive, negative) VALUES (?, ?, ?)",
            (member.id, positive, self.get_negative(member.id)),
        )
        self.db.commit()
        await ctx.send(f"Ты добавил +1 репутации {member.mention}!")

    @commands.command(name='-rep')
    async def negative_rep(self, ctx, member: discord.Member, *, reason=None):
        if member.id == ctx.author.id:
            await ctx.send("Ты не можешь голосовать за себя!")
            return

        if any(n["id"] == ctx.author.id for n in json.loads(self.get_positive(member.id))):
            await ctx.send("Ты уже голосовал за этого участника! `=rep`")
            return

        self.cursor.execute(
            "SELECT positive, negative FROM reputation WHERE user_id = ?", (member.id,)
        )
        negative = self.cursor.fetchone()

        if negative is None:
            negative = json.dumps([{"id": ctx.author.id, "reason": reason}])
        else:
            negative = json.loads(negative[0])
            if any(n["id"] == ctx.author.id for n in negative):
                await ctx.send("Ты уже голосовал за этого участника! `=rep`")
                return
            negative.append({"id": ctx.author.id, "reason": reason})
            negative = json.dumps(negative)

        self.cursor.execute(
            "INSERT OR REPLACE INTO reputation (user_id, positive, negative) VALUES (?, ?, ?)",
            (member.id, self.get_positive(member.id), negative),
        )
        self.db.commit()
        await ctx.send(f"Ты убавил -1 репутации {member.mention}!")

    @commands.command(name='=rep')
    async def revoke_rep(self, ctx, member: discord.Member):
        self.cursor.execute(
            "SELECT positive, negative FROM reputation WHERE user_id = ?", (member.id,)
        )
        dat = self.cursor.fetchone()

        if dat is None:
            await ctx.send(f"{member.mention} не имеет репутации.")
            return

        positive, negative = dat

        if positive:
            positive = json.loads(positive)
            positive = [p for p in positive if p["id"] != ctx.author.id]
            positive = json.dumps(positive)
        else:
            positive = None

        if negative:
            negative = json.loads(negative)
            negative = [n for n in negative if n["id"] != ctx.author.id]
            negative = json.dumps(negative)
        else:
            negative = None

        self.cursor.execute(
            "INSERT OR REPLACE INTO reputation (user_id, positive, negative) VALUES (?, ?, ?)",
            (member.id, positive, negative),
        )
        self.db.commit()
        await ctx.send(f"Ты отменил свой голос за {member.mention}!")

    @commands.command(name='?rep')
    async def check_rep(self, ctx, member: discord.Member = None, page: int = 1):
        if member is None:
            member = ctx.author

        self.cursor.execute(
            "SELECT positive, negative FROM reputation WHERE user_id = ?", (member.id,)
        )
        dat = self.cursor.fetchone()

        if dat is None:
            await ctx.send(f"{member.mention} не имеет репутации.")
            return

        positive, negative = dat

        items_per_page = 5
        start_index = (page - 1) * items_per_page
        end_index = start_index + items_per_page

        if positive:
            positive = json.loads(positive)
            if len(positive) > end_index:
                page_positive = positive[start_index:end_index]
            else:
                page_positive = positive[start_index:]
        else:
            page_positive = []

        if negative:
            negative = json.loads(negative)
            if len(negative) > end_index:
                page_negative = negative[start_index:end_index]
            else:
                page_negative = negative[start_index:]
        else:
            page_negative = []

        if not page_positive and not page_negative:
            await ctx.send(f"Лог репутации {member.mention} пуст.")
            return

        embed = discord.Embed(title=f"Страница {page}", description=f"Репутация {member.mention}", color=botcolour)
        if page_positive:
            embed.add_field(name="+rep", value="\n".join([f"от {await self.bot.fetch_user(p['id'])}: {p['reason']}" for p in page_positive]), inline=False)
        if page_negative:
            embed.add_field(name="-rep", value="\n".join([f"от {await self.bot.fetch_user(n['id'])}: {n['reason']}" for n in page_negative]), inline=False)

        await ctx.send(embed=embed)

    def get_positive(self, user_id):
        """
        Получение положительной репутации из базы данных.
        """
        self.cursor.execute(
            "SELECT positive FROM reputation WHERE user_id = ?", (user_id,)
        )
        positive = self.cursor.fetchone()
        return "[]" if positive is None else positive[0]

    def get_negative(self, user_id):
        """
        Получение отрицательной репутации из базы данных.
        """
        self.cursor.execute(
            "SELECT negative FROM reputation WHERE user_id = ?", (user_id,)
        )
        negative = self.cursor.fetchone()
        return "[]" if negative is None else negative[0]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        ctx = await self.bot.get_context(message)

        if message.content.startswith('+rep'):
            args = message.content.split()
#            if len(args) != 2:
#                await message.channel.send("Неверный формат команды! Используй +rep <@пользователь> [причина]")
#                return

            if message.reference:
                member = (await message.channel.fetch_message(message.reference.message_id)).author
                reason = " ".join(args[1:])
            else:
                try:
                    member = await commands.MemberConverter().convert(ctx=ctx, argument=args[1])
                except commands.BadArgument:
                    await message.channel.send("Не удалось найти пользователя. Убедитесь, что вы правильно пингнули пользователя.")
                    return
                reason = " ".join(args[2:])

            await self.positive_rep(ctx, member, reason=reason)

        elif message.content.startswith('-rep'):
            args = message.content.split()
#            if len(args) != 2:
#                await message.channel.send("Неверный формат команды! Используй -rep <@пользователь> [причина]")
#                return

            if message.reference:
                member = (await message.channel.fetch_message(message.reference.message_id)).author
                reason = " ".join(args[1:])
            else:
                try:
                    member = await commands.MemberConverter().convert(ctx=ctx, argument=args[1])
                except commands.BadArgument:
                    await message.channel.send("Не удалось найти пользователя. Убедитесь, что вы правильно пингнули пользователя.")
                    return
                reason = " ".join(args[2:])

            await self.negative_rep(ctx, member, reason=reason)

        elif message.content.startswith('?rep'):
            args = message.content.split()
#            if len(args) != 2:
#                await message.channel.send("Неверный формат команды! Используй -rep <@пользователь> [причина]")
#                return

            if message.reference:
                member = (await message.channel.fetch_message(message.reference.message_id)).author
            else:
                try:
                    member = await commands.MemberConverter().convert(ctx=ctx, argument=args[1])
                except commands.BadArgument:
                    await message.channel.send("Не удалось найти пользователя. Убедитесь, что вы правильно пингнули пользователя.")
                    return

            await self.check_rep(ctx, member)

        elif message.content.startswith('=rep'):
            args = message.content.split()
#            if len(args) != 2:
#                await message.channel.send("Неверный формат команды! Используй -rep <@пользователь> [причина]")
#                return

            if message.reference:
                member = (await message.channel.fetch_message(message.reference.message_id)).author
            else:
                try:
                    member = await commands.MemberConverter().convert(ctx=ctx, argument=args[1])
                except commands.BadArgument:
                    await message.channel.send("Не удалось найти пользователя. Убедитесь, что вы правильно пингнули пользователя.")
                    return

            await self.revoke_rep(ctx, member)

def setup(bot):
    bot.add_cog(ReputationCog(bot))
