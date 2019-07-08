import discord
from discord.ext import commands
import os


TOKEN = os.environ['DISCORD_TOKEN']
bot = commands.Bot(command_prefix='.')

clans = {
        "envy": "ENpR",
        "gluttony": "GLpR",
        "greed": "GRdR",
        "lust": "LUaR",
        "pride": "PDxR",
        "sloth": "SLrR",
        "wrath": "WRhR"
    }
clan_prefix = {
    'ENp': 'Envy', 
    'GLp': 'Gluttony', 
    'LUa': 'Lust', 
    'PDx': 'Pride', 
    'SLr': 'Sloth', 
    'WRh': 'Wrath'
}
promo_rank = {
    'R': 'P',
    'P': 'S',
    'S': 'L'
}
demote_rank = {
    'L': 'S',
    'S': 'P',
    'P': 'R'
}


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('Type .help for Help'))
    print('Bot is ready.')


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


@bot.command()
async def test(ctx, member: discord.Member, clan):
    clan_tag = member.display_name
    author = ctx.author.display_name
    print(clan_tag)
    print(author)


@bot.command(brief="Add new member to a clan", description="To use: .add <@newMember> <Clan> Example: .add "
                                                           "@Viperguy07 Wrath")
async def add(ctx, member: discord.Member, clan):
    author_nic = ctx.author.display_name
    author_rank = author_nic[3:4]
    author_clan = author_nic[:3]
    member_nic = member.display_name
    
    clan = clan.lower()
    clan = clan[0].upper() + clan[1:]
    role = discord.utils.get(ctx.guild.roles, name=clan)
    clan_tag = member_nic[:3]
    rank_allowed = ["C", "L"]
    if clan in clan_prefix:
        if clan_tag in clan_prefix:
            await ctx.send("{} is already in a clan, if you want to switch him use the clan change command "
                           ".clanchange".format(member.display_name))
        elif author_rank in rank_allowed and clan_prefix[author_clan] == clan \
                or "leadership" in [y.name.lower() for y in ctx.message.author.roles]:
                nickname = clans[clan.lower()] + " " + member.display_name.split()[0]
                await member.edit(nick=nickname, roles=[role])
                await  ctx.send(
                    "Welcome {}, you are now part of {} clan and you can see your clan chat now".format(nickname, clan)
                )
        else:
            await ctx.send("Contact someone in leadership or the Captain/Lieutenant of the clan to "
                           "add {} to this clan.")
    else:
        await ctx.send("{} is not the name of any of our clans please try again".format(clan))


@bot.command(brief="Changes your GamerTag on this server", description="Just type .gt <new GamerTage> with out the "
                                                                       "'<>' example: .gt IlovePopCorn")
async def gt(ctx, *, gt):
    author_nic = ctx.author.display_name
    author_clan = author_nic[:3]
    if author_clan in clan_prefix:
        new_gt = author_nic[:4] + " " + gt
    else:
        new_gt = gt
    await ctx.author.edit(nick=new_gt)
    await ctx.send("Your GamerTag has been updated.")


@bot.command(brief="Promote Player", description=".promote <@Member> and they will be promoted")
async def promote(ctx, member: discord.Member):
    author_nic = ctx.author.display_name
    author_rank = author_nic[3:4]
    author_clan = author_nic[:3]

    member_nic = member.display_name
    member_clan = member_nic[:3]
    member_rank = member_nic[3:4]

    rank_allowed = ["C", "L"]

    # If Author is a Captain or Lieutenant and author is in the same clan as member. Or if author is leadership then
    # grant the request.
    if author_rank in rank_allowed and author_clan == member_clan or "leadership" \
            in [y.name.lower() for y in ctx.message.author.roles]:
        if member_rank in promo_rank:
            new_rank = list(member_nic)
            new_rank[3] = promo_rank[member_rank]
            new_rank = "".join(new_rank)
            await member.edit(nick=new_rank)
            await ctx.send("Congrats {} you have been promoted!".format(new_rank))
        else:
            await ctx.send("You can't promote anyone to Captain, Please contact leadership")
    else:
        await ctx.send("You don't have permissions to promote {}".format(member))


@bot.command(brief="Demote Player", description=".demote <@Member> and they will be demoted")
async def demote(ctx, member: discord.Member):
    author_nic = ctx.author.display_name
    author_rank = author_nic[3:4]
    author_clan = author_nic[:3]

    member_nic = member.display_name
    member_clan = member_nic[:3]
    member_rank = member_nic[3:4]

    rank_allowed = ["C", "L"]

    # If Author is a Captain or Lieutenant and author is in the same clan as member. Or if author is leadership then
    # grant the request.
    if author_rank in rank_allowed and author_clan == member_clan \
            or "leadership" in [y.name.lower() for y in ctx.message.author.roles]:
        if member_rank in demote_rank:
            new_rank = list(member_nic)
            new_rank[3] = demote_rank[member_rank]
            new_rank = "".join(new_rank)
            await member.edit(nick=new_rank)
            await ctx.send("{} you have been demoted!".format(new_rank))
        else:
            await ctx.send("Recruite is the lowest rank, you might want to think of "
                           "kicking {} if it's that bad".format(member))
    else:
        await ctx.send("You don't have permissions to demote {} contact leadership".format(member))


@bot.command(brief="Add to Adult Chat", description=".adult <@Member> and member will be added to adult chat")
async def adult(ctx, member: discord.Member):
    print(ctx.author)
    print(member)
    role = discord.utils.get(ctx.guild.roles, name="Adult")
    if "leadership" in [y.name.lower() for y in ctx.message.author.roles]:
        await member.add_roles(role)


@bot.event
async def on_member_join(member):
    print('Wow you Joined the Server')

bot.run(TOKEN)
