from discord.ext import commands
import discord
from queue import Queue
import random
from player import Player
from datetime import datetime
from custombuffqueue import CustomBuffQueue
from custombuffqueuetypes import CustomBuffQueueTypes
import json
import settings
import logging


# Initialize logger
#logger = settings.logging.getLogger("bot")

player_blacklist = [""]


welcome_messages = ["Hello!", "Hello there!", "Sup!", "Howdy!", "Please, no more work! I'm drowning..."]

# Get bot config
def get_conf(file_name):
    with open(file_name, 'r') as f:
        config = json.load(f)
    return config

conf = get_conf("conf/bot.json")


# Define queues
firstQueue = CustomBuffQueue(CustomBuffQueueTypes.FIRST_LADY)
strategyQueue = CustomBuffQueue(CustomBuffQueueTypes.SECRETARY_OF_STRATEGY)
securityQueue = CustomBuffQueue(CustomBuffQueueTypes.SECRETARY_OF_SECURITY)
developmentQueue = CustomBuffQueue(CustomBuffQueueTypes.SECRETARY_OF_DEVELOPMENT)
scienceQueue = CustomBuffQueue(CustomBuffQueueTypes.SECRETARY_OF_SCIENCE)
interiorQueue = CustomBuffQueue(CustomBuffQueueTypes.SECRETARY_OF_INTERIOR)


# Define alias dictionnary for buffs
buff_dict = {

    # FIRST_LADY
    'f': firstQueue,
    'first': firstQueue,

    # SECRETARY_OF_STRATEGY
    'str': strategyQueue,
    'strat': strategyQueue,
    'strategy': strategyQueue,

    # SECRETARY_OF_SECURITY
    'sec': securityQueue,
    'security': securityQueue,

    # SECRETARY_OF_DEVELOPMENT
    'c': developmentQueue,
    'con': developmentQueue,
    'construction': developmentQueue,
    'd': developmentQueue,
    'dev': developmentQueue,
    'development': developmentQueue,

    # SECRETARY_OF_SCIENCE
    'r': scienceQueue,
    'res': scienceQueue,
    'research': scienceQueue,
    'sci': scienceQueue,
    'science': scienceQueue,

    # SECRETARY_OF_INTERIOR
    'i': interiorQueue,
    'int': interiorQueue,
    'interior': interiorQueue
}


# Resolve queue name by aliases
def get_queue(name):
    if name in buff_dict:
        return buff_dict[name]
    else:
        print("Unable to resolve queue name '" + str(name) + "'.")
        return None
    

# Initialize custom help command
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


def run():

    # Initialize bot
    command_prefix = conf['command_prefix']
    intents = discord.Intents.all()

    bot = commands.Bot(command_prefix=command_prefix
                     , intents=intents
                     , help_command=CustomHelpCommand())


    @bot.event
    async def on_ready():
        # Get channel
        channel = bot.get_channel(conf['channel_id'])

        # Respond in channel
        await channel.send("Hi there! I'm up and running. Feed me your commands!")
        #logger.info(f"User: {bot.user} (ID: {bot.user.id})")


    @bot.command()
    async def hello(ctx):
        print("Sending random hello message...")
        await ctx.send(random.choice(welcome_messages))


    @bot.command()
    async def buff(ctx, buff_name, player_name):

        print(f"Trying to queue player {str(player_name)} for buff {str(buff_name)}...")

        # Set queue
        queue = get_queue(buff_name)

        # Validate data
        if (queue == None):
            await ctx.send(f"The buff abbreviation {str(buff_name)} is currently not supported. Write to the devs at {str(conf['mail_dev'])}!")
            return
        
        # Check blacklist: TBD
        #if (player_name in player_blacklist):
        #    await ctx.send("Player '" + str(player_name) + "' is currently not eligable for buff. Write to the devs at " + str(conf['mail_dev']) + "!")
        #    return

        # Check queue
        if (queue.full() == True):
            await ctx.send("The queue is currently full. Try again later...")
        else:
            # Create player
            player = Player(ctx, player_name)

            # Determine queue position
            position = queue.qsize()

            # Add to queue
            queue.put(player)

            await ctx.send(f"Player {str(player_name)} has been added at position {str(position)}.\n" +
                           f"Estimated waiting time: {str(position * 10)} minutes.\n" +
                           f"Estimated start time: {str(queue.estimate_start_time(position).strftime('%Y-%m-%d %H:%M:%S'))}\n" + 
                           "I'll keep you posted!")
            print(f"Added player {str(player_name)} to buff {str(buff_name)} at position {str(position)}.")


    @bot.command()
    async def show(ctx, buff_name):

        # Set queue
        queue = get_queue(buff_name)

        if (queue != None):       
            if (queue.empty() == True):
                await ctx.send(f"The queue for {str(buff_name)} buff is currently empty. Use the favor of the moment and queue up with `!buff_`!")
            else:
                queue_list = queue.list()
                queue_info = ""

                for entry in queue_list:
                    queue_info += f"Position: {entry['position']}, Player: {entry['player']}, Added by: {entry['added by']}\n"

                for key, player_name, discord_user_name in queue_list:
                    await ctx.send(queue_info)
                

    # ADMIN-Commands, TBD: implement role-level concept and check permissions!
    @bot.command()
    async def clear(ctx, buff_name):

        print("Trying to clear queue...")
        queue = get_queue(buff_name)

        if (queue != None):       
            if (queue.empty() == True):
                await ctx.send(f"The queue for {str(buff_name)} buff is already empty. Skipping command...")
            else:
                await ctx.send(f"The queue for {str(buff_name)} buff contains {str(queue.qsize())} entries.")
                queue.clear()
                if (queue.qsize() == 0):
                    await ctx.send(f"The queue for {str(buff_name)} buff has been cleared.")
                else:
                    raise Exception("Couldn't clear queue.")


    @bot.command()
    async def remove(ctx, buff_name, player_name):
        print("Trying to remove player from queue...")
        queue = get_queue(buff_name)

        if (queue != None):         
            if (queue.empty() == True):
                await ctx.send(f"The queue for {str(buff_name)} buff is already empty. Skipping command...")
            else:
                await ctx.send(f"The queue for {str(buff_name)} buff contains {str(queue.qsize())} entries.")
                
                if (queue.remove(player_name) == True):
                    await ctx.send(f"The player {str(player_name)} has been removed from queue {str(buff_name)}.")
                else:
                    raise Exception(f"Couldn't remove player {str(player_name)} from queue {str(buff_name)}.")


    @bot.command()
    async def pop(ctx, buff_name):
        print("Trying to hand out buff to next candidate...")
        queue = get_queue(buff_name)

        if (queue != None):         
            if (queue.empty() == True):
                await ctx.send(f'The queue for {str(buff_name)} buff is already empty. Skipping command...')
            else:
                await ctx.send(f'The queue for {str(buff_name)} buff contains {str(queue.qsize())} entries.')

                player = queue.get()
                queue.last_popped = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                disc_user = bot.get_user(player.disc_user_id)
                await ctx.user.send(f'Player {str(player.lw_user_name)} has received buff {str(buff)} for the next 10 minutes!')






    @bot.command()
    @commands.is_owner()
    async def shutdown(ctx):
        await ctx.bot.close()


    bot.run(conf['token']) #, root_logger=True


