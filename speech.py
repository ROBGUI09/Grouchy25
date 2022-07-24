import json
import requests
from datetime import datetime
from discord.ext import commands, tasks
import discord

class Speech(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.iam = ""
        self.exp_iam = None
        self.oauth_token = "AQAAAABH8f8VAATuwXyHYoECNkhegmbqqpCT30o"
        self.create_token()
        self.folder = "b1gq0nnj5ikj3j7opj3a"
        
    def create_token(self):
        params = {'yandexPassportOauthToken': self.oauth_token}
        response = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens', params=params)                                                   
        decode_response = response.content.decode('UTF-8')
        text = json.loads(decode_response) 
        self.iam_token = text.get('iamToken')
        self.exp_iam_token = datetime.fromisoformat(text.get('expiresAt').split(".")[0])
        
    def check_token(self):
        if datetime.now() < self.exp_iam_token:
            self.create_token(oauth_token)

    def speak(self, text):
        self.check_token()
        h = {"Authorization": f"Bearer {self.iam}"}
        data = {
            "text":text,
            "lang":"ru-RU",
            "folderId":self.folder
        }
        raw = requests.post("https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize",headers=h,data=data)
        return raw.content
        
    def is_connected(self, ctx):
        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        return voice_client and voice_client.is_connected()
    
    @commands.command(name="speak")
    async def _speak(self, ctx, text):
        destination = ctx.author.voice.channel

        client = await destination.connect()
        
        if client.is_playing():
            await ctx.send("Я уже что-то проигрываю в этом канале...")
            return
        
        audio = discord.FFmpegPCMAudio(self.speak(text))
        await client.play(audio)
        
    
