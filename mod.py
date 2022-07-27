import discord
import time
import psutil
from discord.ext import commands as cmd

import teapot


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
            await ctx.send("Please specify the number of messages you want to delete!")
            await ctx.message.add_reaction(emoji='❌')
        elif amount <= 0:  # lower then 0
            await ctx.send("The number must be bigger than 0!")
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
            await ctx.send(f'{member} has been kicked!')
            await ctx.message.add_reaction(emoji='✅')
        except Exception as failkick:
            await ctx.send("Failed to kick: " + str(failkick))
            await ctx.message.add_reaction(emoji='❌')


def ban(bot):
    @bot.command()
    @cmd.has_permissions(ban_members=True)  # check user permission
    async def ban(ctx, member: discord.Member, *, reason=None):
        try:
            await member.ban(reason=reason)
            await ctx.send(f'{member} has been banned!')
            await ctx.message.add_reaction(emoji='✅')
        except Exception as e:
            await ctx.send("Failed to ban: " + str(e))
            await ctx.message.add_reaction(emoji='❌')
