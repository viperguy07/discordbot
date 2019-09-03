import discord
from discord.ext import commands
import os


TOKEN = os.environ['DISCORD_TOKEN']
bot = commands.Bot(command_prefix='.')

clans = {
        "envy": "EN-",
        "gluttony": "GLp",
        "greed": "GRd",
        "lust": "LUa",
        "pride": "PDx",
        "sloth": "SLr",
        "wrath": "WRh"
}
clan_prefix = {
    'EN-': 'Envy',
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


@bot.command(
    brief="Add new member to a clan",
    description="To use: .add <@newMember> <Clan> Example: .add @Viperguy07 Wrath"
)
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

    if clan.lower() in clans:
        if clan_tag in clan_prefix:
            await ctx.send("{} is already in a clan, if you want to switch him use the clan change command "
                           ".clanchange".format(member.display_name))
        elif author_rank in rank_allowed or "leadership" in [y.name.lower() for y in ctx.message.author.roles]:
            nickname = clans[clan.lower()] + "R " + member.display_name
            await member.edit(nick=nickname, roles=[role])
            await ctx.send(
                "Welcome {}, you are now part of {} clan and you can see your clan chat now".format(nickname, clan)
            )
        else:
            await ctx.send("Contact someone in leadership or the Captain/Lieutenant of the clan to "
                           "add {} to this clan.")
    else:
        await ctx.send("{} is not the name of any of our clans please try again".format(clan))


@bot.command(
    brief="Change a member to a different clan",
    description=""
                "To use type: "
                ".clanchange <Clan> <@newMember> "
                "Example: .clanchange Wrath @Viperguy07"
)
async def clanchange(ctx, clan, member: discord.Member):
    member_nic = member.display_name
    print(member)
    c_rank = member_nic[3:4]
    c_gt = member_nic[5:]
    c_clan = member_nic[:3]
    clan = clan.lower()
    clan = clan[0].upper() + clan[1:]
    new_nic = "{}{} {}".format(clans[clan], c_rank, c_gt)
    role = discord.utils.get(ctx.guild.roles, name=clan)
    old_clan_role = discord.utils.get(ctx.guild.roles, name=c_clan)

    if "leadership" in [y.name.lower() for y in ctx.message.author.roles]:
        # await member.remove_roles(member, old_clan_role)
        print('here')
        await member.edit(nick=new_nic, roles=[role])
        await ctx.send(
            "The request to change {} clans has been approve, Welcome {} the {} clan".format(c_gt, c_gt, clan)
        )
    else:
        await ctx.send("Contact someone in leadership to request this change.")


@bot.command(
    brief="Changes your GamerTag on this server",
    description="Just type .gt <new GamerTage> with out the '<>' example: .gt IlovePopCorn"
)
async def gt(ctx, *, gtag):
    author_nic = ctx.author.display_name
    author_clan = author_nic[:3]
    if author_clan in clan_prefix:
        new_gt = author_nic[:4] + " " + gtag
    else:
        new_gt = gtag
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


@bot.command(brief="Assign member to a squad", description=".squad <@Member> <squad>")
async def squad(ctx, member: discord.Member, r_squad):
    author_nic = ctx.author.display_name

    author_rank = author_nic[3:4]
    author_clan = author_nic[:2]

    member_nic = member.display_name
    member_clan = member_nic[:2]

    rank_allowed = ["C", "L"]

    squads = {
        'a': 'a',
        'A': 'a',
        'alpha': 'a',
        'Alpha': 'a',
        'b': 'b',
        'B': 'b',
        'bravo': 'b',
        'Bravo': 'b',
        'c': 'c',
        'C': 'c',
        'charlie': 'c',
        'Charlie': 'c',
        'd': 'd',
        'D': 'd',
        'delta': 'd',
        'Delta': 'd'
    }
    new_squad = squads[r_squad]

    nic_li = list(member_nic)
    nic_li[2] = new_squad
    new_nic = "".join(nic_li)

    # If Author is a Captain or Lieutenant and author is in the same clan as member. Or if author is leadership then
    # grant the request.
    if author_rank in rank_allowed and author_clan == member_clan or "leadership" \
            in [y.name.lower() for y in ctx.message.author.roles]:
        await member.edit(nick=new_nic)
        await ctx.send("Congrats {} you have been assign your new squad!".format(new_nic))
    else:
        await ctx.send("You don't have permissions to assign members to squads please ask your captain or leadership")


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
    author_nic = ctx.author.display_name
    author_rank = author_nic[3:4]
    rank_allowed = ["C", "L"]
    role = discord.utils.get(ctx.guild.roles, name="Adult")

    if author_rank in rank_allowed or "leadership" in [y.name.lower() for y in ctx.message.author.roles]:
        await member.add_roles(role)


@bot.event
async def on_member_join(member):
    print('Wow you Joined the Server')

bot.run(TOKEN)
