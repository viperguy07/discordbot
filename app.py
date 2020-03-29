import os
import asyncio
import datetime
import discord
import requests
from dotenv import load_dotenv
from discord.ext import commands
load_dotenv()
if os.getenv('SQLITE') == 'dev':
    import sqlite3
else:
    from pysqlite3 import dbapi2 as sqlite3

con = sqlite3.connect('7dsg.db')
create_table = """ CREATE TABLE IF NOT EXISTS activity (
                                        discord_id TEXT PRIMARY KEY,
                                        username TEXT NOT NULL,
                                        last_active TIMESTAMP NULL
                                    ); """
con.execute(create_table)
con.close()

apikey = os.getenv('XBOX_API')
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='.')


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('Type .help for Help'))
    print('Bot is ready.')


@bot.event
async def on_message(message):
    conn = sqlite3.connect('7dsg.db')
    c = conn.cursor()
    display_name = str(message.author.display_name)
    dis_id = str(message.author)
    ctime = str(datetime.datetime.now())
    dont_track = os.getenv('DONT_TRACK').split(',')
    if dis_id not in dont_track:
        q_check = "SELECT EXISTS(SELECT discord_id FROM activity WHERE discord_id=?)"
        c.execute(q_check, (dis_id,))
        record = c.fetchone()
        if record[0] == 1:
            q = "UPDATE activity SET last_active=?, username=? WHERE discord_id=?"
            try:
                c.execute(q, (ctime, display_name, dis_id))
            except sqlite3.Error as e:
                print("An error occurred:", e.args[0])
        else:
            q = "INSERT OR IGNORE INTO activity (discord_id, username, last_active) values (?, ?, ?)"
            c.execute(q, (dis_id, display_name, ctime))
        conn.commit()
        conn.close()
        await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    conn = sqlite3.connect('7dsg.db')
    c = conn.cursor()
    display_name = str(member.display_name)
    dis_id = str(member)
    ctime = str(datetime.datetime.now())
    q = "INSERT INTO activity (discord_id, username, last_active) values (?, ?, ?)"
    c.execute(q, (dis_id, display_name, ctime))
    conn.commit()
    conn.close()


@bot.event
async def on_member_remove(member):
    conn = sqlite3.connect('7dsg.db')
    c = conn.cursor()
    dis_id = str(member)
    q = "DELETE FROM activity WHERE discord_id=?"
    c.execute(q, (dis_id,))
    conn.commit()
    conn.close()
    print("{} has left on been Kicked/Banned".format(member.display_name))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("That command doe not exist type .help for a list of commands")


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


@bot.command(
    brief="Shows last time members were active",
    description="Shows the last time members sent a message in any chat room"
)
async def status(ctx):
    conn = sqlite3.connect('7dsg.db')
    c = conn.cursor()
    c.execute("SELECT * FROM activity ORDER BY last_active")
    records = c.fetchall()
    conn.close()
    totals = []
    for x in records:
        c = datetime.datetime.now() - datetime.datetime.strptime(x[2], '%Y-%m-%d %H:%M:%S.%f')
        days = c.days
        hours = c.seconds // 3600
        minutes = c.seconds // 60
        if days > 7:
            weeks = days // 7
            if weeks == 1:
                last_seen = "1 Week ago"
            else:
                last_seen = "{} Weeks ago".format(weeks)
        elif days > 0:
            if days == 1:
                last_seen = " 1 Day ago"
            else:
                last_seen = "{} Days ago".format(days)
        elif hours > 0:
            if hours == 1:
                last_seen = "1 Hour ago"
            else:
                last_seen = "{} Hours ago".format(hours)
        elif minutes > 0:
            if minutes == 1:
                last_seen = "1 Minute ago"
            else:
                last_seen = "{} Minutes ago".format(minutes)
        else:
            last_seen = "less than a minute ago"
        totals.append("{} - {}".format(x[1], last_seen))
    totals = "\n".join(totals)
    await ctx.send("Members Activity Status\n {}".format(totals))


@bot.command(
    brief="Current member count",
    description="Shows how many member we currently have"
)
async def members(ctx):
    channels = ["bot-test"]
    if str(ctx.channel) in channels:
        x = list([member.display_name for member in ctx.guild.members])
        x.sort()
        x = "\n".join(x)
        await ctx.send(x)
    else:
        total_members = len(ctx.guild.members) - 1
        await ctx.send(
            "7 Deadly Sins Gaming currently has {} members, -- Except me I'm more of a genie :genie:".format(
                total_members
            )
        )


@bot.command(
    brief="Kick a member from the community.",
    description="You must include a member and a reason\n"
                "For Example:\n"
                ".kick @TestMonkey 'Didn't report hours'"
)
async def kick(ctx, member: discord.Member, *, reason):
    authorname = ctx.author.display_name
    username = member.display_name
    channels = ["general", "bot-test", "bot-audit"]
    audit_channel = ctx.guild.get_channel(693025739351785542)
    author_roles = list([role.name.lower() for role in ctx.message.author.roles])

    if "leadership" in author_roles:
        if str(ctx.channel) in channels:
            await ctx.guild.kick(member, reason=reason)
            await ctx.send("{0} got the :boot: - Have a great rest of your day {0}, somewhere else."
                           .format(username))
            await audit_channel.send(
                '**Source_User**: ```ini\n[{}]\n``` **Target_User**: ```ini\n[{}]\n``` |'
                ' **Action**: ```diff\n-Kicked\n``` **Reason**: ```css\n[{}]\n```'.format(
                    authorname,
                    username,
                    reason
                )
            )
        else:
            await ctx.send(
                "You can only use this command in the 'general' chat. and your are in {}".format(
                    ctx.channel
                )
            )
    else:
        await ctx.send("You don't have the rank to execute this command.")


@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You must include a reason for kicking this user like this example: '
                       '.kick @testmonkey "Failed to report hours"')


@bot.command(
    brief="Add new member to a clan",
    description="To use: .add <@newMember> <Clan> Example: .add @TestMonkey Wrath"
)
async def add(ctx, member: discord.Member, xbox='yes'):
    author_name = ctx.author.display_name
    username = member.display_name
    channels = ["general", "bot-test", "bot-audit"]
    audit_channel = ctx.guild.get_channel(693025739351785542)
    author_roles = list([role.name.lower() for role in ctx.message.author.roles])
    role = discord.utils.get(ctx.guild.roles, name="Members")
    nickname = "7DG {}".format(member.display_name)

    if "leadership" in author_roles and xbox == 'yes' and str(ctx.channel) in channels:
        url = "https://xboxapi.com//v2/xuid/{}".format(username)

        payload = {}
        headers = {
            'X-AUTH': apikey
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if isinstance(response, int):
            await member.edit(nick=nickname, roles=[role])
            await ctx.send(
                "@everyone Please welcome {} as an official member of our community ".format(nickname)
            )
            await audit_channel.send(
                '**Source_User**: ```ini\n[{}]\n``` **Target_User**: ```ini\n[{}]\n``` |'
                ' **Action**: ```diff\n-Promotion\n``` **Reason**: ```css\n[{}]\n```'.format(
                    author_name,
                    username,
                    "Promoted to member"
                )
            )
        else:
            await ctx.send('```diff\n-{0} is not a valid GamerTag.\n``` ```diff\n-{0} must change using .gt first '
                           'like this example:\n``` ```css\n.gt RealGamerTag\n```'.format(username))
    else:
        await ctx.send("Contact someone in leadership to make {} a full member.")


@bot.command(
    brief="Changes your nickname to your GamerTag",
    description="Just type .gt <new GamerTage> with out the '<>' example: .gt IlovePopCorn"
)
async def gt(ctx, *, gtag):
    username = ctx.author.display_name
    member = username[5:]
    if "7DSG " == member:
        new_gt = "7DG {}".format(gtag)
    else:
        new_gt = gtag
    await ctx.author.edit(nick=new_gt)
    await ctx.send("Your GamerTag has been updated.")


@bot.command(brief="Promote to leadership", description=".promote <@Member> and they will be promoted to leadership")
async def promote(ctx, member: discord.Member):
    author_name = ctx.author.display_name
    username = member.display_name
    channels = ["general", "bot-test", "bot-audit"]
    audit_channel = ctx.guild.get_channel(693025739351785542)
    author_roles = list([role.name.lower() for role in ctx.message.author.roles])
    role = discord.utils.get(ctx.guild.roles, name="Leadership")

    if "leadership" in author_roles and str(ctx.channel) in channels:
        await member.add_roles(role)
        await audit_channel.send(
            '**Source_User**: ```ini\n[{}]\n``` **Target_User**: ```ini\n[{}]\n``` |'
            ' **Action**: ```diff\n-Promotion\n``` **Reason**: ```css\n[{}]\n```'.format(
                author_name,
                username,
                "Promoted to Leadership"
            )
        )
    else:
        await ctx.send("Only a member of Leadership can preform this action")


@bot.command(brief="schlap a player in the mascara", description="Get owned")
async def schlap(ctx, member: discord.Member):
    author_nic = ctx.author.display_name
    member_nic = member.display_name
    await ctx.send("OOOHH {} SCHLAPED {}!!! ".format(author_nic, member_nic))


@bot.command(brief="Add to Adult Chat", description=".adult <@Member> and member will be added to adult chat")
async def adult(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Adult")
    await member.add_roles(role)


@bot.command(
    brief="Remove from Adult Chat",
    description=".rmadult <@Member> and member will be removed from adult chat"
)
async def rmadult(ctx, member: discord.Member):
    current_roles = member.roles
    new_roles = []
    for r in current_roles:
        if r != discord.utils.get(ctx.guild.roles, name='Adult'):
            new_roles.append(r)
    await member.edit(roles=new_roles)


@bot.command()
async def delete(ctx):
    author = str(ctx.author)
    if author == os.getenv('ADMIN_USER'):
        await ctx.channel.purge(limit=100)


@bot.command()
async def dbadd(ctx, member: discord.Member):
    author = str(ctx.author)
    if author == os.getenv('ADMIN_USER'):
        conn = sqlite3.connect('7dsg.db')
        c = conn.cursor()
        display_name = str(member.display_name)
        dis_id = str(member)
        ctime = str(datetime.datetime.now())
        q = "INSERT INTO activity (discord_id, username, last_active) values (?, ?, ?)"
        c.execute(q, (dis_id, display_name, ctime))
        conn.commit()
        conn.close()
    await ctx.channel.purge(limit=1)


bot.run(TOKEN)
