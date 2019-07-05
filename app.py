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
async def add(ctx, member : discord.Member):
    author = ctx.author.display_name.split()[0]
    usr = member
    # id = test.mentions[0].id
    await ctx.send('What do your want {}? and you smell like {}'.format(author, usr))


@bot.event
async def on_member_join(member):
    print('Wow you Joined the Server')

bot.run(TOKEN)
