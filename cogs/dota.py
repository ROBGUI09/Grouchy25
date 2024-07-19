import requests
import random
import discord
from discord.ext import commands

class DotaInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.idata = requests.get("https://github.com/odota/dotaconstants/raw/master/build/items.json").json()

    def get_items_by_id(self, data, id):
        for key, value in data.items():
            if value['id'] == id:
                return value

    def get_top_items(self, items, arg):
        total_count = sum(items.values())
        sorted_items = sorted(items.items(), key=lambda x: x[1], reverse=True)[:arg]

        top_items = []
        for item_id, count in sorted_items:
            percent = (count / total_count) * 100
            itinfo = self.get_items_by_id(self.idata, int(item_id))
            top_items.append((item_id, itinfo['dname'], "https://cdn.cloudflare.steamstatic.com" + itinfo['img'], count, f"{percent:.2f}%"))

        return top_items

    def stringify(self, item):
        return f"{item[1]} ({item[4]}, {item[3]})"

    @commands.command(name='hotd')
    async def dota_hero_info(self, ctx):
        hero = random.choice(requests.get("https://api.opendota.com/api/heroStats").json())

        embed = discord.Embed(title=f"{hero['localized_name']}, {hero['attack_type']}")
        embed.add_field(name="Роли", value=", ".join(hero['roles']), inline=False)
        embed.add_field(name="Паб (7дн)", value=f"{hero['pub_win']}/{hero['pub_pick']} ({'{:.2f}%'.format((hero['pub_win'] / hero['pub_pick'])*100)})", inline=True)
        pro_win_rate = (hero['pro_win'] / hero['pro_pick']) * 100
        pro_win_rate_str = f"{pro_win_rate:.2f}%"
        embed.add_field(name="Про (7дн)", value=f"{hero['pro_win']}/{hero['pro_pick']} ({pro_win_rate_str})", inline=True)
        embed.set_thumbnail(url="https://cdn.cloudflare.steamstatic.com" + hero['img'])

        items = requests.get(f"https://api.opendota.com/api/heroes/{hero['id']}/itemPopularity").json()

        start = ", ".join([self.stringify(item) for item in self.get_top_items(items['start_game_items'], 3)])
        early = ", ".join([self.stringify(item) for item in self.get_top_items(items['early_game_items'], 3)])
        mid = ", ".join([self.stringify(item) for item in self.get_top_items(items['mid_game_items'], 3)])
        late = ", ".join([self.stringify(item) for item in self.get_top_items(items['late_game_items'], 3)])

        embed.add_field(name="Часто покупают (7дн):", value=f"Старт: {start}\nРанняя: {early}\nСередина: {mid}\nПоздняя: {late}", inline=False)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(DotaInfo(bot))
