import discord
from discord.ext import commands
import os


TOKEN = os.environ['DISCORD_TOKEN']
bot = commands.Bot(command_prefix='.')


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('Type .help for Help'))
    print('Bot is ready.')


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


@bot.command()
async def test(ctx, member: discord.Member, clan):
    clan_tag = member.display_name[:3]
    print(clan_tag)


@bot.command()
async def add(ctx, member: discord.Member, clan):
    clan = clan.lower()
    clan = clan[0].upper() + clan[1:]
    role = discord.utils.get(ctx.guild.roles, name=clan)
    clan_tag = member.display_name[:3]
    print(clan_tag)
    clans = {
        "envy": "ENpR",
        "gluttony": "GLpR",
        "greed": "GRdR",
        "lust": "LUaR",
        "pride": "PDxR",
        "sloth": "SLrR",
        "wrath": "WRhR"
    }
    clan_prefix = ['ENp', 'GLp', 'LUa', 'PDx', 'SLr', 'WRh']
    if clan_tag in clan_prefix:
        await ctx.send("{} is already in a clan, if you want to switch him use the clan change command .clanchange")
    else:
        if "leadership" in [y.name.lower() for y in ctx.message.author.roles]:

            nickname = clans[clan.lower()] + " " + member.display_name.split()[0]
            await member.edit(nick=nickname, roles=[role])
            await  ctx.send(
                "Welcome {}, you are now part of {} clan and you can see your clan chat now".format(nickname, clan)
            )

        else:
            await ctx.send("Contact someone in leadership to add {} to your clan.")


@bot.event
async def on_member_join(member):
    print('Wow you Joined the Server')

bot.run(TOKEN)
