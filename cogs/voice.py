import discord
import asyncio
from discord.ext import commands
import traceback
import sqlite3
import validators
import dbuni

def create_db():
    c = dbuni('dbs/voice.db')
    c.connect()
    c.execute('''CREATE TABLE IF NOT EXISTS "guild" (
        `guildID`       INTEGER,
        `ownerID`       INTEGER,
        `voiceChannelID`        INTEGER,
        `voiceCategoryID`       INTEGER
);''')
    c.execute('''CREATE TABLE `guildSettings` (
        `guildID`       INTEGER,
        `channelName`   TEXT,
        `channelLimit`  INTEGER
);''')
    c.execute('''CREATE TABLE `userSettings` (
        `userID`        INTEGER,
        `channelName`   TEXT,
        `channelLimit`  INTEGER
);''')
    c.execute('''CREATE TABLE `voiceChannel` (
        `userID`        INTEGER,
        `voiceID`       INTEGER
);''')
    c.close()

create_db()

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = dbuni('dbs/voice.db')
        conn.connect()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        c = self.conn
        guildID = member.guild.id
        voice = c.execute("SELECT voiceChannelID FROM guild WHERE guildID = ?", (guildID,)).fetchone()
        if voice is None: return

        voiceID = voice[0]
        try:
            if after.channel.id == voiceID:
                cooldown = c.execute("SELECT * FROM voiceChannel WHERE userID = ?", (member.id,)).fetchone()
                if cooldown is None:
                    pass
                else:
                    await member.send("Ты создаёшь каналы слишком быстро, задержись на 15 секунд.")
                    await asyncio.sleep(15)
                voice = c.execute("SELECT voiceCategoryID FROM guild WHERE guildID = ?", (guildID,)).fetchone()
                setting = c.execute("SELECT channelName, channelLimit FROM userSettings WHERE userID = ?", (member.id,)).fetchone()
                guildSetting = c.execute("SELECT channelLimit FROM guildSettings WHERE guildID = ?", (guildID,)).fetchone()
                if setting is None:
                    name = f"Канал {member.name}'а"
                    if guildSetting is None:
                        limit = 0
                    else:
                        limit = guildSetting[0]
                else:
                    if guildSetting is None:
                        name = setting[0]
                        limit = setting[1]
                    elif guildSetting is not None and setting[1] == 0:
                        name = setting[0]
                        limit = guildSetting[0]
                    else:
                        name = setting[0]
                        limit = setting[1]
                categoryID = voice[0]
                id = member.id
                category = self.bot.get_channel(categoryID)
                channel2 = await member.guild.create_voice_channel(name,category=category)
                channelID = channel2.id
                await member.move_to(channel2)
                await channel2.set_permissions(self.bot.user, connect=True,read_messages=True)
                await channel2.edit(name= name, user_limit = limit)
                c.execute("INSERT INTO voiceChannel VALUES (?, ?)", (id,channelID))
                def check(a,b,c):
                    return len(channel2.members) == 0
                await self.bot.wait_for('voice_state_update', check=check)
                await channel2.delete()
                await asyncio.sleep(3)
                c.execute('DELETE FROM voiceChannel WHERE userID=?', (id,))
        except:
            pass

    @commands.command(name="pv-setup")
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        c = self.conn
        guildID = ctx.guild.id
        aid = ctx.author.id
        def check(m):
            return m.author.id == ctx.author.id
        await ctx.channel.send("**У вас есть 60 секунд, чтобы ответить**")
        await ctx.channel.send("**Выберите название для категории в которой вы хотите создавать приватные каналы :(Например 'Приватки')**")
        try:
            category = await self.bot.wait_for('message', check=check, timeout = 60.0)
        except asyncio.TimeoutError:
            await ctx.channel.send('Бот не дождался ответа. Начните заново.')
        else:
            new_cat = await ctx.guild.create_category_channel(category.content)
            await ctx.channel.send('**Выберите название для канала, через который вы хотите создавать приватные каналы: (Например "[+] Приватка")**')
            try:
                channel = await self.bot.wait_for('message', check=check, timeout = 60.0)
            except asyncio.TimeoutError:
                await ctx.channel.send('Бот не дождался ответа. Начните заново.')
            else:
                try:
                    channel = await ctx.guild.create_voice_channel(channel.content, category=new_cat)
                    voice = c.execute("SELECT * FROM guild WHERE guildID = ? AND ownerID=?", (guildID, aid)).fetchone()
                    if voice is None:
                        c.execute("INSERT INTO guild VALUES (?, ?, ?, ?)",(guildID,aid,channel.id,new_cat.id))
                    else:
                        c.execute("UPDATE guild SET guildID = ?, ownerID = ?, voiceChannelID = ?, voiceCategoryID = ? WHERE guildID = ?",(guildID,aid,channel.id,new_cat.id, guildID))
                    await ctx.channel.send("**Готово!**")
                except:
                    await ctx.channel.send("Вы ввели что-то неправильно.\nПопробуйте заново.")

    @commands.command(name="pv-setlimit")
    @commands.has_permissions(administrator=True)
    async def setlimit(self, ctx, num):
        c = self.conn
        if True:
            voice = c.execute("SELECT * FROM guildSettings WHERE guildID = ?", (ctx.guild.id,)).fetchone()
            if voice is None:
                c.execute("INSERT INTO guildSettings VALUES (?, ?, ?)", (ctx.guild.id,f"{ctx.author.name}'s channel",num))
            else:
                c.execute("UPDATE guildSettings SET channelLimit = ? WHERE guildID = ?", (num, ctx.guild.id))
            await ctx.send("Вы изменили стандартный лимит канала для вашего сервера.")
        else:
            await ctx.channel.send(f"{ctx.author.mention} только владелец сервера может делать это!")

    @setup.error
    async def info_error(self, ctx, error):
        print(error)

    @commands.command(name="pv-lock")
    async def lock(self, ctx):
        c = self.conn
        aid = ctx.author.id
        voice = c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (aid,)).fetchone()
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention}, вы не владелец канала.")
        else:
            channelID = voice[0]
            role = ctx.guild.default_role
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=False)
            await ctx.channel.send(f'{ctx.author.mention}, голосовой канал теперь закрыт! 🔒')

    @commands.command(name="pv-unlock")
    async def unlock(self, ctx):
        c = self.conn
        aid = ctx.author.id
        voice = c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (aid,)).fetchone()
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention}, вы не владелец канала.")
        else:
            channelID = voice[0]
            role = ctx.guild.default_role
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=True)
            await ctx.channel.send(f'{ctx.author.mention}, голосовой канал теперь открыт для всех. 🔓')

    @commands.command(name="pv-permit",aliases=["pv-allow"])
    async def permit(self, ctx, member : discord.Member):
        c = self.conn
        aid = ctx.author.id
        voice = c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (aid,)).fetchone()
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention}, вы не владелец канала.")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(member, connect=True,read_messages=True)
            await ctx.channel.send(f'{ctx.author.mention}, вы разрешили **{member.name}** заходить в ваш канал. ✅')

    @commands.command(name="pv-reject",aliases=["pv-deny"])
    async def reject(self, ctx, member : discord.Member):
        c = self.conn
        aid = ctx.author.id
        guildID = ctx.guild.id
        voice = c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (aid,)).fetchone()
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention}, вы не владелец канала.")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            for members in channel.members:
                if members.id == member.id:
                    voice = c.execute("SELECT voiceChannelID FROM guild WHERE guildID = ?", (guildID,)).fetchone()
                    channel2 = self.bot.get_channel(voice[0])
                    await member.move_to(channel2)
            await channel.set_permissions(member, connect=False,read_messages=False)
            await ctx.channel.send(f'{ctx.author.mention}, вы запретили **{member.name}** заходить в ваш канал. ❌')



    @commands.command(name="pv-limit")
    async def limit(self, ctx, limit):
        c = self.conn
        aid = ctx.author.id
        voice = c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (aid,)).fetchone()
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention}, вы не владелец канала.")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.edit(user_limit = limit)
            await ctx.channel.send(
                f'{ctx.author.mention}, вы установили лимит канала на '
                + f'{limit} участников.'
            )
            voice = c.execute("SELECT channelName FROM userSettings WHERE userID = ?", (id,)).fetchone()
            if voice is None:
                c.execute("INSERT INTO userSettings VALUES (?, ?, ?)", (id,f'{ctx.author.name}',limit))
            else:
                c.execute("UPDATE userSettings SET channelLimit = ? WHERE userID = ?", (limit, id))


    @commands.command(name="pv-name")
    async def name(self, ctx,*, name):
        c = self.conn
        id = ctx.author.id
        voice = c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,)).fetchone()
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention}, вы не владелец канала.")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.edit(name = name)
            await ctx.channel.send(
                f'{ctx.author.mention}, вы установили '
                + f'{name} как название вашего канала.'
            )
            voice = c.execute("SELECT channelName FROM userSettings WHERE userID = ?", (id,)).fetchone()
            if voice is None:
                c.execute("INSERT INTO userSettings VALUES (?, ?, ?)", (id,name,0))
            else:
                c.execute("UPDATE userSettings SET channelName = ? WHERE userID = ?", (name, id))

    @commands.command(name="pv-claim")
    async def claim(self, ctx):
        x = False
        c = self.conn
        channel = ctx.author.voice.channel
        if channel == None:
            await ctx.channel.send(f"{ctx.author.mention} вы не в голосовом канале.")
        else:
            id = ctx.author.id
            voice = c.execute("SELECT userID FROM voiceChannel WHERE voiceID = ?", (channel.id,)).fetchone()
            if voice is None:
                await ctx.channel.send(f"{ctx.author.mention}, вы не можете завладеть этим каналом.")
            else:
                for data in channel.members:
                    if data.id == voice[0]:
                        owner = ctx.guild.get_member(voice[0])
                        await ctx.channel.send(f"{ctx.author.mention}, этим каналом ещё владеет **{owner.name}**.")
                        x = True
                if x == False:
                    await ctx.channel.send(f"{ctx.author.mention}, вы теперь владелец канала.")
                    c.execute("UPDATE voiceChannel SET userID = ? WHERE voiceID = ?", (id, channel.id))


def setup(bot):
    bot.add_cog(voice(bot))
