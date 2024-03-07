import discord,configparser,asyncpg,asyncio
from discord.ext import commands

config = configparser.ConfigParser()
config.read('bot_config.ini')
cogs_list = ['weekly',
			'submit',
			'lastfm',
			'charts',
			'countdown']
def is_owner(ctx):  # defining the bot owner check
	return ctx.author.id == 197938114218426370

bot = discord.AutoShardedBot(guild_ids=[1047385465994612836])#server id for personal debuggging server , prevents commands from syncing globally
async def db_init(bot): #creating a pool connection to the database for connecctions
	if not hasattr(bot, 'pool'):
		bot.pool = await asyncpg.create_pool(config['keys']['db'])

	

asyncio.get_event_loop().run_until_complete(db_init(bot)) #creates the db connection so is the first action
@bot.event
async def on_read():
	print(f"We have logged in as {bot.user}")

##OWNER COMMANDS
@bot.slash_command(description="Load cog",guild_ids=[1047385465994612836])
@commands.check(is_owner)
async def load(ctx,name: discord.Option(str,required=True)):
	"""Loads an extension."""
	try:
		bot.load_extension(name)
	except (AttributeError, ImportError) as e:
		await ctx.respond("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
		return
	await ctx.respond("{} loaded.".format(name),ephemeral=True)


@bot.slash_command(description="Unload Cog",guild_ids=[1047385465994612836])
@commands.check(is_owner)
async def unload(ctx,name: discord.Option(str,required=True)):
	"""Removes an extension"""
	bot.unload_extension(name)
	await ctx.respond('Unloaded: ' + name,ephemeral=True)


@bot.slash_command(guild_ids=[1047385465994612836])
@commands.check(is_owner)
async def reload(ctx,name: discord.Option(str,required=True)):
	"""Reloads an extension"""
	try:
		bot.unload_extension(name)
		bot.load_extension(name)
		await ctx.respond('Extension has been reloaded',ephemeral=True)
	except Exception as e:
		await ctx.respond('Something went horribly wrong: ' + str(e),ephemeral=True)



for cog in cogs_list:
	bot.load_extension(f'modules.{cog}')

bot.run(config['keys']['bot_token'])