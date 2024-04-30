from discord.ext import commands
import discord
from queue import Queue
import random
from player import Player
from custombuffqueue import CustomBuffQueue
from custombuffqueuetypes import CustomBuffQueueTypes
import json


player_blacklist = [""]


welcome_messages = ["Hello!", "Hello there!", "Sup!", "Howdy!", "Please, no more work! I'm drowning..."]

# Get bot config
def get_conf(file_name):
    with open(file_name, 'r') as f:
        config = json.load(f)
    return config

conf = get_conf("conf/bot.json")



# Define command prefix/es
bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())


# Define queues
firstQueue = CustomBuffQueue(CustomBuffQueueTypes.FIRST_LADY)
strategyQueue = CustomBuffQueue(CustomBuffQueueTypes.SECRETARY_OF_STRATEGY)
securityQueue = CustomBuffQueue(CustomBuffQueueTypes.SECRETARY_OF_SECURITY)
developmentQueue = CustomBuffQueue(CustomBuffQueueTypes.SECRETARY_OF_DEVELOPMENT)
scienceQueue = CustomBuffQueue(CustomBuffQueueTypes.SECRETARY_OF_SCIENCE)
interiorQueue = CustomBuffQueue(CustomBuffQueueTypes.SECRETARY_OF_INTERIOR)


# Define dictionnary
buff_dict = {
    'c': developmentQueue,
    'con': developmentQueue,
    'construction': developmentQueue,
    'd': developmentQueue,
    'dev': developmentQueue,
    'development': developmentQueue,
    'r': scienceQueue,
    'res': scienceQueue,
    'research': scienceQueue,
    's': scienceQueue,
    'science': scienceQueue
}


# Resolve queue name
def get_queue(name):
    if name in buff_dict:
        print (buff_dict[name])
        return buff_dict[name]
    else:
        print("Unable to resolve queue name '" + str(name) + "'.")
        return None



@bot.event
async def on_ready():
    
    # Get channel
    channel = bot.get_channel(conf['channel_id'])

    # Respond in channel
    await channel.send("Hi there! I'm back up and running.")


@bot.command()
async def hello(ctx):
    print("Sending random hello message...")
    await ctx.send(random.choice(welcome_messages))


@bot.command()
async def buff(ctx, buff_name, player_name):

    print("Trying to set buff '" + str(buff_name) + "'...")

    # Set queue
    queue = get_queue(buff_name)

    # Validate data
    if (queue == None):
        await ctx.send("The buff abbreviation'" + str(buff_name) + "' is currently not supported. Write to the devs at " + str(conf['mail_dev']) + "!")
        return
    
    # Check blacklist
    if (player_name in player_blacklist):
        await ctx.send("Player '" + str(player_name) + "' is currently not eligable for buff. Write to the devs at " + str(conf['mail_dev']) + "!")
        return

    # Check queue
    if (queue.full() == True):
        await ctx.send("The queue is currently full. Try again later...")
    else:
        # Create player
        player = Player(ctx, player_name)

        # Add to queue
        queue.put(player)
        await ctx.send("Player '" + str(player_name) + "' has been added. I'll keep you up posted!")


@bot.command()
async def show(ctx, buff_name):

    # Set queue
    queue = get_queue(buff_name)

    if (queue != None):       
        if (queue.empty() == True):
            await ctx.send("The queue for '" + str(buff_name) + "' buff is currently empty. Use the favor of the moment and queue up with `!buff_`!")
        else:
            await ctx.send(list(queue.queue))


@bot.command()
async def clear(ctx, buff_name):

    # Set queue
    queue = get_queue(buff_name)

    if (queue != None):       
        if (queue.empty() == True):
            await ctx.send("The queue for '" + str(buff_name) + "' buff is already empty. Skipping command...")
        else:
            await ctx.send("The queue for '" + str(buff_name) + "' buff contains " + str(queue.qsize()) + " entries.")
            queue.clear()
            if (queue.qsize() == 0):
                await ctx.send("The queue for '" + str(buff_name) + "' buff has been cleared.")
            else:
                raise Exception("Couldn't clear queue.")


@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.bot.close()


bot.run( BOT_TOKEN )


# Initialize custom help command (TBD)
class CustomHelpCommand(commands.HelpCommand):

    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        #for cog in mapping:
        #    await self.get_destination().send(f'{cog.qualified_name}: {[command.name for command in mapping[cog]]}')
        #return await super().send_bot_help(mapping)
            
        await self.get_destination().send("New here? Don't worry, I'll help you! I'm a simple bot with the task to keep track of all the buffs for Server #391.")
        await self.get_destination().send("Type `!buff` followed by the type of buff you'd like to receive. As soon as the first lady has time, you'll receive the buff in game!")
        await self.get_destination().send("Type `!show` followed by the type of buff you'd like to see the queue for.")
    
    async def send_cog_help(self, cog):
        return await super().send_cog_help(cog)
    
    async def send_group_help(self, group):
        return await super().send_group_help(group)
    
    async def send_command_help(self, command):
        return await super().send_command_help(command)