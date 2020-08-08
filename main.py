import random
import discord
from discord.ext import commands

# Split logger to log to console and file
import logging
logging.basicConfig(level=logging.INFO)
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()

fileHandler = logging.FileHandler("logs.log")
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

# Raidboss Ids
queue_na_role_id = 719620287129321502
queue_eu_role_id = 719620470621863956
lastgame_role_id = 719625580596691054
lastgame_role_ready_id = 719625720581718055
tenman_role_id = 698350963395788870
captain_role_id = 698343215119597669
queue_na_id = 698323056484941914
queue_eu_id = 698323700025524345
queue_last_id = 698371067336589313
queue_teams_ids = [698323152836493312, 698323212773228584,
                   698323976895725608, 698324016762454126]
channel_id = 698328368676077698

bot = commands.Bot(command_prefix='!', description='Vice Volerant 10man bot. Type \'!help\' for help.')


@bot.event
async def on_ready():
    logging.info("Vice Volerant 10man is ready!")


@bot.event
async def on_voice_state_update(member, before, after):
    if tenman_role_id in [x.id for x in member.roles]:

        # Member joined a channel
        if before.channel is None and after.channel is not None:

            # Queue #1
            if after.channel.id == queue_na_id:
                await check_ready(member, queue_na_role_id, after)

            # Queue #2
            elif after.channel.id == queue_eu_id:
                await check_ready(member, queue_eu_role_id, after)

            # Queue teams
            elif after.channel.id in queue_teams_ids:
                await add_role(member, lastgame_role_ready_id)

            # Queue last
            elif after.channel.id == queue_last_id:
                await check_ready(member, lastgame_role_ready_id, after)

        # Member left a channel
        elif before.channel is not None and after.channel is None:

            # Queue #1
            if before.channel.id == queue_na_id:
                await remove_role(member, queue_na_role_id)

            # Queue #2
            elif before.channel.id == queue_eu_id:
                await remove_role(member, queue_eu_role_id)

            # Queue teams
            elif before.channel.id in queue_teams_ids:
                await remove_role(member, lastgame_role_id)

            # Queue last
            elif before.channel.id == queue_last_id:
                await remove_role(member, lastgame_role_ready_id)

        # Member switched channels
        elif before.channel.id != after.channel.id:

            # Left queue #1
            if before.channel.id == queue_na_id:
                await remove_role(member, queue_na_role_id)

            # Left queue #2
            elif before.channel.id == queue_eu_id:
                await remove_role(member, queue_eu_role_id)

            # Left queue last
            elif before.channel.id == queue_last_id:
                await remove_role(member, lastgame_role_ready_id)

            # Left queue teams
            elif before.channel.id in queue_teams_ids:
                await remove_role(member, lastgame_role_id)

            # Joined queue #1
            if after.channel.id == queue_na_id:
                await check_ready(member, queue_na_role_id, after)

            # Joined queue #2
            elif after.channel.id == queue_eu_id:
                await check_ready(member, queue_eu_role_id, after)

            # Joined queue teams
            elif after.channel.id in queue_teams_ids:
                await add_role(member, lastgame_role_id)

            # Joined queue last
            if after.channel.id == queue_last_id:
                await check_ready(member, lastgame_role_ready_id, after)


def get_role(member, role_id):
    return discord.utils.get(member.guild.roles, id=role_id)


def member_name(member):
    return f'{member.nick} - {member.mention}'


async def remove_role(member, role_id):
    logging.info(f'Attempting to remove role \"{role_id}\" from member \"{member_name(member)}\"')
    role = get_role(member, role_id)
    await member.remove_roles(role)


async def add_role(member, role_id):
    logging.info(f'Attempting to add role \"{role_id}\" to member \"{member_name(member)}\"')
    role = get_role(member, role_id)
    await member.add_roles(role)


async def check_ready(member, role_id, after):
    logging.info(f'Member \"{member_name(member)}\" joined queue: \"{after.channel.name}\"')
    role = get_role(member, role_id)
    await member.add_roles(role)

    if len(after.channel.members) == after.channel.user_limit:
        captains = await choose_captains(role, after)

        channel = bot.get_channel(channel_id)
        bot_avatar = bot.user.avatar_url
        embed = discord.Embed()
        embed.set_thumbnail(url=bot_avatar)
        embed.add_field(name="**Queue Filled**",
                        value=f'{after.channel.name} has reached 10 players. Captains will start adding players on VALORANT to fill the party.',
                        inline=False)
        embed.add_field(name="**Captains**", value=f'{captains[0].mention} and {captains[1].mention}', inline=False)

        if random.randint(0, 1):
            captains.reverse()
        
        embed.add_field(name="**Captain Selections**",
                        value=f'{captains[0].mention} has been chosen for first pick and will add players to join the party.\n{captains[1].mention} has been chosen for map and side.',
                        inline=False)
        embed.set_footer(text='Vice Valorant 10mans/Scrims', icon_url=bot_avatar)
        await channel.send(content=f'{role.mention}', embed=embed)


async def choose_captains(role, after):
    logging.info(f'Attempting to choose captains from the members of the role \"{role.id}\"')
    members = after.channel.members
    members_copy = list(members)
    captain_roles = []
    for member in members:
        if any([captain_role_id == x.id for x in member.roles]):
            captain_roles.append(member)
            members_copy.remove(member)

    num_captains = len(captain_roles)
    if num_captains == 0:
        return random.sample(members, 2)
    elif num_captains == 1:
        captains = list(captain_roles)
        captains.append(random.choice(members_copy))
        return captains
    else:
        return random.sample(captain_roles, 2)
        


bot.run('TOKEN')
