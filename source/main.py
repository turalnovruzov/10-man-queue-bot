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
queue1_role_id = 541193531327381504
queue2_role_id = 541193637246009345
queue3_role_id = 611111814285230100
lastgame_role_id = 591599057269555230
lastgame_role_ready_id = 636617033815162880
tenman_role_id = 563707849784426506
queue1_id = 245832221900931073
queue2_id = 486205232066461711
queue3_id = 600733232614604830
queue_last_id = 548840744207777792
queue_teams_ids = [610259790043807754, 610259814790070321, 486219099890778113,
                   417316349480796160, 600733600471711774, 600733689672106004]
channel_id = 397912711524253696

bot = commands.Bot(command_prefix='!', description='10 man queue bot. Type \'!help\' for help.')


@bot.event
async def on_ready():
    logging.info("10manqueuebot is ready!")


@bot.event
async def on_voice_state_update(member, before, after):
    if tenman_role_id in [x.id for x in member.roles]:

        # Member joined a channel
        if before.channel is None and after.channel is not None:

            # Queue #1
            if after.channel.id == queue1_id:
                await check_ready(member, queue1_role_id, after)

            # Queue #2
            elif after.channel.id == queue2_id:
                await check_ready(member, queue2_role_id, after)

            # Queue #3
            elif after.channel.id == queue3_id:
                await check_ready(member, queue3_role_id, after)

            # Queue teams
            elif after.channel.id in queue_teams_ids:
                await add_role(member, lastgame_role_ready_id)

            # Queue last
            elif after.channel.id == queue_last_id:
                await check_ready(member, lastgame_role_ready_id, after)

        # Member left a channel
        elif before.channel is not None and after.channel is None:

            # Queue #1
            if before.channel.id == queue1_id:
                await remove_role(member, queue1_role_id)

            # Queue #2
            elif before.channel.id == queue2_id:
                await remove_role(member, queue2_role_id)

            # Queue #3
            elif before.channel.id == queue3_id:
                await remove_role(member, queue3_role_id)

            # Queue teams
            elif before.channel.id in queue_teams_ids:
                await remove_role(member, lastgame_role_id)

            # Queue last
            elif before.channel.id == queue_last_id:
                await remove_role(member, lastgame_role_ready_id)

        # Member switched channels
        elif before.channel.id != after.channel.id:

            # Left queue #1
            if before.channel.id == queue1_id:
                await remove_role(member, queue1_role_id)

            # Left queue #2
            elif before.channel.id == queue2_id:
                await remove_role(member, queue2_role_id)

            # Left queue #3
            elif before.channel.id == queue3_id:
                await remove_role(member, queue3_role_id)

            # Left queue last
            elif before.channel.id == queue_last_id:
                await remove_role(member, lastgame_role_ready_id)

            # Left queue teams
            elif before.channel.id in queue_teams_ids:
                await remove_role(member, lastgame_role_id)

            # Joined queue #1
            if after.channel.id == queue1_id:
                await check_ready(member, queue1_id, after)

            # Joined queue #2
            elif after.channel.id == queue2_id:
                await check_ready(member, queue2_role_id, after)

            # Joined queue #3
            elif after.channel.id == queue3_id:
                await check_ready(member, queue3_role_id, after)

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
        channel = bot.get_channel(channel_id)
        await channel.send(f'{role.mention} your queue is ready, join the server within 5 minutes.')


bot.run('NjY5MTQ2ODYwNzgyNjE2NjI3.XiblvQ.NkBFNI8pDkhIYjhWqagTfBo5gB8')
