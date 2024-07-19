import asyncio
import functools
import itertools
import math
import traceback
import random
import logging
import discord
import os
import yt_dlp as youtube_dl
from async_timeout import timeout
from discord.ext import commands
import vkauth
from dotenv import load_dotenv

load_dotenv()
vks = vkauth.VkAndroidApi(token=os.environ.get("VK_TOKEN"),secret=os.environ.get("VK_SECRET"))

# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''


class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass

import configparser

config = configparser.ConfigParser()
config.read('config.ini')

audio_filter = config.get('AudioSettings', 'filter', fallback='bass=g=-10')


class YTDLSource:
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {
      'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
      'options': f'-af "{audio_filter}" -vn'
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: commands.Context, data: dict):
        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        if date and len(date) == 8 and date.isdigit():
            self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        else:
            self.upload_date = 'Unknown'
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return f'**{self.title}** от **{self.uploader}**'

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError(f'По запросу `{search}` ничего не найдено.')

        if 'entries' not in data:
            process_info = data
        else:
            process_info = next((entry for entry in data if entry), None)

            if process_info is None:
                raise YTDLError(f'По запросу `{search}` ничего не найдено.')

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError(f'Не удалось разобрать страницу `{webpage_url}`')

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError(f'Запрос `{webpage_url}` ничего не нашел.')

        return cls(ctx, info)

    async def get_stream(source, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(source.ytdl.extract_info, source.url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError(f'Не удалось разобрать страницу `{webpage_url}`')

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError(f'Запрос `{webpage_url}` ничего не нашел.')

        return info['url']

    @classmethod
    async def _search(cls, search: str, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError(f'По запросу `{search}` ничего не найдено.')

        if 'entries' not in data:
            data = {"entries":data}

        return [
            [
                process_info['title'],
                process_info['uploader'],
                process_info['webpage_url'],
            ]
            for process_info in data['entries']
        ]

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append(f'{days} days')
        if hours > 0:
            duration.append(f'{hours} hours')
        if minutes > 0:
            duration.append(f'{minutes} minutes')
        if seconds > 0:
            duration.append(f'{seconds} seconds')

        return ', '.join(duration)

class VKError(Exception):
    pass


class VKSource:
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -http_persistent 0',
        'options': f'-af "{audio_filter}" -vn'
    }

    def __init__(self, ctx: commands.Context, data: dict):
        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = f"<t:{date}> (<t:{date}:R>)"
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return f'**{self.title}** от **{self.uploader}**'

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
#        loop = loop or asyncio.get_event_loop()
        if search.startswith("audio"):
            data = vks.method("audio.getById", audios=search.split("audio")[1]).get('response',[])
        else:
            data = vks.method("audio.search", q=search, count=1, auto_complete=1).get('response',{}).get('items',[])

        if len(data) == 0:
            raise VKError(f'По запросу `{search}` ничего не найдено.')

        audio = data[0]

        return await cls._parse_audio(ctx, audio)

    async def get_stream(self, loop: asyncio.BaseEventLoop = None):
#        loop = loop or asyncio.get_event_loop()
        return self.stream_url

    @classmethod
    async def _search(cls, search: str, loop = None):
        data = vks.method("audio.search", q=search, count=25, auto_complete=1)

        if len(data.get("response",{}).get('items',[])) == 0:
            raise VKError(f'По запросу `{search}` ничего не найдено.')

        return [
            [
                audio['title'],
                audio['artist'],
                f"audio{audio['owner_id']}_{audio['id']}_{audio['access_key']}",
            ]
            for audio in data['response']['items']
        ]

    @classmethod
    async def _parse_audio(cls, ctx: commands.Context, audio: dict):
        if audio['url'] == "":
            return None

        info = {
            'uploader':audio['artist'],
            'uploader_url':"https://vk.com/music/artist/"+audio['main_artists'][0]['domain'] if 'main_artists' in audio.keys() else "https://youtu.be/f-tLr7vONmc",
            'upload_date': audio['date'],
            'title': audio['title'],
            'thumbnail': audio.get('thumb',{}).get(
              "photo_{}".format(audio.get('thumb',{}).get('width',"300"))
            ),
            'description':"",
            'duration':audio['duration'],
            'tags':'',
            'webpage_url':"https://vk.com/audio{}_{}_{}".format(audio["owner_id"],audio["id"],audio["access_key"]),
            'views':0,
            'likes':0,
            'dislikes':0,
            'url':audio['url']
        }

        return cls(ctx, data=info)

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append(f'{days} days')
        if hours > 0:
            duration.append(f'{hours} hours')
        if minutes > 0:
            duration.append(f'{minutes} minutes')
        if seconds > 0:
            duration.append(f'{seconds} seconds')

        return ', '.join(duration)


class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        embed = (discord.Embed(title='Сейчас играет',
                               description=f'```css\n{self.source.title}\n```',
                               color=16734003)
                 .add_field(name='Длительность', value=self.source.duration)
                 .add_field(name='Запрошено', value=self.requester.mention)
                 .add_field(name='Автор', value=f'[{self.source.uploader}]({self.source.uploader_url})')
                 .add_field(name='Ссылка', value=f'[Ссылка]({self.source.url})')
                 .set_thumbnail(url=self.source.thumbnail))

        return embed

def crop(text):
    return text[:100] if len(text) > 100 else text

class SongPicker(discord.ui.Select):
    def __init__(self, ctx, provider, results):
        options=[discord.SelectOption(label=crop(result[0]),description=crop(result[1]),value=result[2]) for result in results]
        super().__init__(placeholder="только не баратрума, ну пожалуйста",max_values=1,min_values=1,options=options)
        self._ctx = ctx
        self._provider = provider

    async def callback(self, interaction: discord.Interaction):
        ctx = self._ctx
        provider = self._provider
        try:
            source = await provider.create_source(ctx, self.values[0])
        except (YTDLError, VKError) as e:
            await ctx.send(f'Во время обработки запроса произошла ошибка: {e}')
        else:
            song = Song(source)

            await ctx.voice_state.songs.put(song)
            await interaction.response.edit_message(content=f'Добавлено в очередь: {source}',view=None)

class SongPickerView(discord.ui.View):
    def __init__(self, ctx,provider,results, *, timeout = 180):
        super().__init__(timeout=timeout)
        self.add_item(SongPicker(ctx,provider,results))

class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]

def buttonfactory(ctx):
    loopem = "🔂" if ctx.voice_state.loop == "one" else "➡️" if ctx.voice_state.loop == "off" else "🔁"
    playem = "⏸" if ctx.voice_state.voice.is_paused() else "▶"

    class PlayerButtons(discord.ui.View):
        def __init__(self, ctx: commands.Context, *, timeout=300):
            super().__init__(timeout=timeout)
            self.ctx = ctx

        @discord.ui.button(style=discord.ButtonStyle.gray,emoji=loopem)
        async def loop(self,interaction:discord.Interaction,button:discord.ui.Button):
            if self.ctx.voice_state.loop == "off":
                self.ctx.voice_state.loop = "all"
            elif self.ctx.voice_state.loop == "all":
                self.ctx.voice_state.loop = "one"
            elif self.ctx.voice_state.loop == "one":
                self.ctx.voice_state.loop = "off"
            else:
                self.ctx.voice_state.loop = "off"
            await interaction.response.edit_message(embed=self.ctx.voice_state.current.create_embed(),view=buttonfactory(self.ctx))

        @discord.ui.button(style=discord.ButtonStyle.gray,emoji="🔀")
        async def shuffle(self,interaction:discord.Interaction,button:discord.ui.Button):
            self.ctx.voice_state.songs.shuffle()
            await interaction.response.edit_message(embed=self.ctx.voice_state.current.create_embed(),view=buttonfactory(self.ctx))

        @discord.ui.button(style=discord.ButtonStyle.gray,emoji=playem)
        async def play(self,interaction:discord.Interaction,button:discord.ui.Button):
            if self.ctx.voice_state.voice.is_playing():
                self.ctx.voice_state.voice.pause()
            else:
                self.ctx.voice_state.voice.resume()
            await interaction.response.edit_message(embed=self.ctx.voice_state.current.create_embed(),view=buttonfactory(self.ctx))

        @discord.ui.button(style=discord.ButtonStyle.gray,emoji="⏭️")
        async def next(self,interaction:discord.Interaction,button:discord.ui.Button):
            self.ctx.voice_state.skip()
            await interaction.response.edit_message(embed=self.ctx.voice_state.current.create_embed(),view=buttonfactory(self.ctx))

    return PlayerButtons(ctx)

class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx

        self.controlmsg = None
        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()
        self.terminate = False

        self.loop = "off"
        self.skip_votes = set()

        self.audio_player = bot.loop.create_task(self.audio_player_task())
        self.audio_player.add_done_callback(self.check_exceptions)

    def check_exceptions(self, task):
        try:
            _ = task.result()
        except Exception as e:
            traceback.print_exception(e)

    def __del__(self):
        self.audio_player.cancel()

    @property
    def is_playing(self):
        return self.voice and self.current

    async def getnext(self):
        return self.current if self.loop == "one" else await self.songs.get()

    async def audio_player_task(self):
        while True:
            self.next.clear()

            # Try to get the next song within 3 minutes.
            # If no song will be added to the queue in time,
            # the player will disconnect due to performance
            # reasons.
            try:
                async with timeout(180):  # 3 minutes
                    self.current = await self.getnext()
            except asyncio.TimeoutError:
                if self.controlmsg != None:
                    await self.controlmsg.edit(view=None)
                self.bot.loop.create_task(self.stop())
                return

            self.voice.play(discord.FFmpegOpusAudio(await self.current.source.get_stream(loop=self.bot.loop), **self.current.source.FFMPEG_OPTIONS), after=self.play_next_song)
            if self.controlmsg != None:
                await self.controlmsg.edit(view=None)
            self.controlmsg = await self.current.source.channel.send(embed=self.current.create_embed(),view=buttonfactory(self._ctx))
            if self.loop == "all":
                await self.songs.put(self.current)

            self.terminate = False

            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

        self.next.set()

    def skip(self):
        self.skip_votes.clear()

        if self.is_playing:
            self.voice.stop()
            self.terminate = True

    async def stop(self):
        self.songs.clear()
        self.loop = "off"

        if self.voice:
            await self.voice.disconnect()
            if self.controlmsg != None:
                await self.controlmsg.edit(view=None)
            self.voice = None
            self.terminate = True


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage('Эта команда недоступна в лс.')

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send(f'An error occurred: {error}')
        traceback.print_exception(error)

    @commands.command(name='join', invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context):
        """Joins a voice channel."""

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='summon')
    async def _summon(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
        """Summons the bot to a voice channel.
        If no channel was specified, it joins your channel.
        """

        if not channel and not ctx.author.voice:
            raise VoiceError('Вы не подключены к войс каналу и не выбрали канал для подключения')

        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member == self.bot.user:
            if before.channel is not None and after.channel is None:
                del self.voice_states[member.guild.id]
            elif before.channel is None and after.channel is not None:
                await member.guild.change_voice_state(channel=after.channel, self_mute=False, self_deaf=True)

    @commands.command(name='leave', aliases=['disconnect'])
    async def _leave(self, ctx: commands.Context):
        """Clears the queue and leaves the voice channel."""

        if not ctx.voice_state.voice:
            return await ctx.send('Not connected to any voice channel.')

        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]

    @commands.command(name='now', aliases=['current', 'playing'])
    async def _now(self, ctx: commands.Context):
        """Displays the currently playing song."""

        if ctx.voice_state.controlmsg:
            await ctx.voice_state.controlmsg.edit(view=None)
        ctx.voice_state.controlmsg = await ctx.send(embed=ctx.voice_state.current.create_embed(),view=buttonfactory(ctx))

    @commands.command(name='pause')
    async def _pause(self, ctx: commands.Context):
        """Pauses the currently playing song."""

        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.message.add_reaction('⏯')


    @commands.command(name='resume')
    async def _resume(self, ctx: commands.Context):
        """Resumes a currently paused song."""

        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='stop')
    async def _stop(self, ctx: commands.Context):
        """Stops playing song and clears the queue."""

        ctx.voice_state.songs.clear()

        if ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            await ctx.message.add_reaction('⏹')

    @commands.command(name='skip')
    async def _skip(self, ctx: commands.Context):
        """Vote to skip a song. The requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('Not playing any music right now...')

        voter = ctx.message.author
        if voter == ctx.voice_state.current.requester:
            await ctx.message.add_reaction('⏭')
            ctx.voice_state.skip()

        elif voter.id not in ctx.voice_state.skip_votes:
            ctx.voice_state.skip_votes.add(voter.id)
            total_votes = len(ctx.voice_state.skip_votes)

            if total_votes >= 3:
                await ctx.message.add_reaction('⏭')
                ctx.voice_state.skip()
            else:
                await ctx.send(f'Голос за пропуск добавлен, сейчас **{total_votes}/3** голосов.')

        else:
            await ctx.send('Вы уже голосовали за пропуск этой песни.')

    @commands.command(name='queue')
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        """Shows the player's queue.
        You can optionally specify the page to show. Each page contains 10 elements.
        """

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Empty queue.')

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

        embed = (discord.Embed(description=f'**{len(ctx.voice_state.songs)} tracks:**\n\n{queue}')
                 .set_footer(text=f'Просматриваем страницу {page}/{pages}'))
        await ctx.send(embed=embed)

    @commands.command(name='shuffle')
    async def _shuffle(self, ctx: commands.Context):
        """Shuffles the queue."""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Пустая очередь.')

        ctx.voice_state.songs.shuffle()
        await ctx.message.add_reaction('✅')

    @commands.command(name='remove')
    async def _remove(self, ctx: commands.Context, index: int):
        """Removes a song from the queue at a given index."""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Пустая очередь.')

        ctx.voice_state.songs.remove(index - 1)
        await ctx.message.add_reaction('✅')

    @commands.command(name='loop')
    async def _loop(self, ctx: commands.Context, mode: str = None):
        """Loops the currently playing song.
        Invoke this command again to unloop the song.
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('Ничего не играет в данный момент.')

        if mode == None:
            await ctx.send(ctx.voice_state.loop)

        # Inverse boolean value to loop and unloop.
        if mode in ["off","one","all"]:
            ctx.voice_state.loop = mode
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('❌')

    @commands.command(name='search')
    async def _search(self, ctx: commands.Context, *, search: str):
        """search for songs to add."""

        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)

        provider = YTDLSource

        if search.startswith("vk+"):
            provider = VKSource
            search = search[3:]

        async with ctx.typing():
            results = await provider._search(search)
            await ctx.send("у тебя три минуты",view=SongPickerView(ctx,provider,results))

    @commands.command(name='play')
    async def _play(self, ctx: commands.Context, *, search: str):
        """Plays a song.
        If there are songs in the queue, this will be queued until the
        other songs finished playing.
        This command automatically searches from various sites if no URL is provided.
        A list of these sites can be found here: https://rg3.github.io/youtube-dl/supportedsites.html
        """

        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)

        provider = YTDLSource

        if search.startswith("vk+"):
            provider = VKSource
            search = search[3:]

        async with ctx.typing():
            try:
                source = await provider.create_source(ctx, search, loop=self.bot.loop)
            except (YTDLError, VKError) as e:
                await ctx.send(f'Во время обработки запроса произошла ошибка: {e}')
            else:
                song = Song(source)

                await ctx.voice_state.songs.put(song)
                await ctx.send(f'Добавлено в очередь: {source}')

    @commands.command(name='playlist')
    async def _playlist(self, ctx: commands.Context, *, url: str):
        """Добавить ВК плейлист (альбом) в очередь по ссылке
        """

        if not url.startswith("https://vk.com"):
            await ctx.send('Поддерживается только импорт плейлистов.')

        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)

        async with ctx.typing():
            owner_id, playlist_id, access_key = url.split('/')[-1].split("_")
            pl = vks.method("audio.getPlaylistById",owner_id=owner_id,playlist_id=playlist_id,access_key=access_key)['response']
            songs = []
            while len(songs) < pl['count']:
                songs += vks.method("audio.get", owner_id=owner_id, album_id=playlist_id, access_key=access_key, offset = len(songs))['response']['items']

            dead = False

            for audio in songs:
                try:
                    source = await VKSource._parse_audio(ctx,audio)
                except VKError as e:
                    await ctx.send(f'Во время обработки запроса произошла ошибка: {e}')
                else:
                    if source == None:
                        dead = True
                        continue
                    song = Song(source)

                    await ctx.voice_state.songs.put(song)

            warn = "\n⚠️ Один (или несколько) треков в плейлисте (альбоме) были отозваны или заблокированы, они были автоматически пропущены при импорте." if dead else ""
            await ctx.send(f'Добавлено в очередь: **+{len(songs)}**{warn}')

    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError('Вы не находитесь в голосовом каналею')

        if ctx.voice_client and ctx.voice_client.channel != ctx.author.voice.channel:
            raise commands.CommandError('Бот уже в канале.')

