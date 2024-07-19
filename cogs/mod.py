import discord
import time
import psutil
from discord.ext import commands as cmd


def setup(bot):
    """ Initialize commands """
    prune(bot)
    kick(bot)
    ban(bot)


def prune(bot):
    @bot.command(aliases=['purge', 'clear', 'cls'])
    @cmd.has_permissions(manage_messages=True)
    async def prune(ctx, amount=0):
        if amount == 0:
            await ctx.send("Укажите количество сообщений для удаления.")
            await ctx.message.add_reaction(emoji='❌')
        elif amount <= 0:  # lower then 0
            await ctx.send("Количество сообщений для удаления должно быть больше 0.")
            await ctx.message.add_reaction(emoji='❌')
        else:
            await ctx.message.add_reaction(emoji='✅')
            await ctx.channel.purge(limit=amount + 1)


def kick(bot):
    @bot.command()
    @cmd.has_permissions(kick_members=True)  # check user permission
    async def kick(ctx, member: discord.Member, *, reason=None):
        try:
            await member.kick(reason=reason)
            await ctx.send(f'{member} был кикнут с сервера.')
            await ctx.message.add_reaction(emoji='✅')
        except Exception as failkick:
            await ctx.send("Не удалось кикнуть: " + str(failkick))
            await ctx.message.add_reaction(emoji='❌')


def ban(bot):
    @bot.command()
    @cmd.has_permissions(ban_members=True)  # check user permission
    async def ban(ctx, member: discord.Member, *, reason=None):
        try:
            await member.ban(reason=reason)
            await ctx.send(f'{member} был забанен.')
            await ctx.message.add_reaction(emoji='✅')
        except Exception as e:
            await ctx.send("Не удалось забанить: " + str(e))
            await ctx.message.add_reaction(emoji='❌')
