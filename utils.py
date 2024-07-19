import sqlite3
import time, os, data

db = sqlite3.connect(os.path.join(data.DATABASES_FOLDER,'grouchy.db'))
cur = db.cursor()
    
def check_for_vip(guild_id):
    cur.execute('SELECT vip_status FROM guilds WHERE id=?', (guild_id,))
    if row := cur.fetchone():
        return row[0]
    cur.execute("INSERT INTO guilds (id, vip_status) VALUES (?,0)", (guild_id,))
    db.commit()
    return 0


import os
import sys
import json
import shlex
import re
import datetime
import functools
from discord import Guild, Message
from discord.ext.commands import Context, Bot

def set_prefixes(guild: Guild, prefixes):
    guilds = get_guilds()
    guilds[str(guild.id)]['prefixes'] = prefixes
    set_guilds(guilds)


def get_channels(guild: Guild):
    return get_guilds().get(str(guild.id), {}).get('channels', [])


def set_channels(guild: Guild, channels):
    guilds = get_guilds()
    guilds[str(guild.id)]['channels'] = channels
    set_guilds(guilds)


def is_channel_bound(ctx: Context):
    channels = get_channels(ctx.guild)
    return ctx.channel.id in channels or not channels


def update_guilds(bot: Bot):
    guilds = get_guilds()
    guild_ids = list(guilds.keys())
    if 'default' in guild_ids:
        guild_ids.remove('default')
    for guild_id in guild_ids:
        if guild_obj := bot.get_guild(int(guild_id)):
            guilds[guild_id]['name'] = guild_obj.name
        else:
            guilds.pop(guild_id)
    for guild_obj in bot.guilds:
        if str(guild_obj.id) not in guild_ids:
            guilds[str(guild_obj.id)] = {
                'name': guild_obj.name,
                'prefixes': DEFAULT_PREFIXES,
                'channels': [],
                'games': {}
            }
    set_guilds(guilds)


def parse_time(time_string: str, regex: str = None):
    if regex:  
        regex: re.Pattern = re.compile(regex)  
    else:  
        regex: re.Pattern = re.compile(r'^((?P<days>[\.\d]+?)d)?((?P<hours>[\.\d]+?)h)?((?P<minutes>[\.\d]+?)m)?((?P<seconds>[\.\d]+?)s)?$')  
    parts = regex.match(time_string)  
    assert parts is not None, f"Could not parse any time information from '{time_string}'.  Examples of valid strings: '16h', '2d8h5m20s', '7m4s'"  
    time_params = {name: float(param) for name, param in parts.groupdict().items() if param}  
    try:  
        return datetime.timedelta(**time_params)  
    except Exception:  
        return None  


def parse_command(command: str):
    args = shlex.split(command)  
    values = []  
    keys = [arg for arg in args if arg.endswith(':')]  
    if not keys:  
        return {}  
    x = []  
    for arg in args[args.index(keys[0]) + 1:]:  
        if arg not in keys:  
            x.append(arg)  
        if arg in keys or args.index(arg) == len(args) - 1:  
            if x:  
                values.append(x)  
                x = []  
    return {k.strip(':'): v for k, v in zip(keys, values)}  


def channel_bound(func):
    @functools.wraps(func)
    async def decorator(*args, **kwargs):
        for arg in args:
            if isinstance(arg, Context):
                if is_channel_bound(arg):
                    await func(*args, **kwargs)
                return
    return decorator


def preview_command(func):
    @functools.wraps(func)
    async def decorator(*args, **kwargs):
        if PREVIEW:
            await func(*args, **kwargs)
    return decorator

