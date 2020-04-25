import discord,datetime,configparser,asyncpg,asyncio,re,json,logging
from discord.ext import commands
config = configparser.ConfigParser()
config.read('bot_config.ini')
startup_extensions = ['modules.youtube'
					, 'modules.rym'
					, 'modules.admin'
					, 'modules.charts'
					, 'modules.countdown'
					, 'modules.general'
					, 'modules.lastfm'
					, 'modules.quotes'
					, 'modules.submit'
					, 'modules.taste'
					, 'modules.weekly']
prefix_cache = {}
conditions_cache = {}
non_removable = ['help', 'prefix', 'remove', 'info', 'ball_add', 'hug_add']
logging.basicConfig(level=logging.ERROR)

def is_owner(ctx):  # defining the bot owner check
	return ctx.message.author.id == 197938114218426370

async def get_pre(bot, message):
	# try:
	if message.guild.id in prefix_cache and message.guild.id is not None:
		return prefix_cache[message.guild.id]
	# except AttributeError: #this will occur if in a pm where message.guild will be a None Type
	# 	return "!"
bot = commands.AutoShardedBot(command_prefix=get_pre,fetch_offline_members=False)

async def stuff(bot): #creating a pool connection to the database for connecctions
	if not hasattr(bot, 'pool'):
		bot.pool = await asyncpg.create_pool(config['keys']['db'])

asyncio.get_event_loop().run_until_complete(stuff(bot))  #creates the db connection so is the first action


async def conditions_fetch():
	if conditions_cache == {}:  # runs at bot start
		async with bot.pool.acquire() as conn:
			async with conn.transaction():
				async for serverid, conditions in conn.cursor('SELECT serverid,conditions FROM servers'):
					try:
						conditions_cache[serverid] = json.loads(conditions)
					except TypeError:
						conditions_cache[serverid]=conditions

asyncio.get_event_loop().run_until_complete(conditions_fetch())

async def prefix_fetch():#establishing prefix cache for all servers (possibly inefficient ?)
	if prefix_cache == {}:  # should run when the bot starts
		async with bot.pool.acquire() as conn:  # getting values to append to prefix_cache
			async with conn.transaction():
				async for serverid, prefix in conn.cursor('SELECT serverid,prefix FROM servers'):
					prefix_cache[serverid] = prefix

asyncio.get_event_loop().run_until_complete(prefix_fetch())

@bot.command()
@commands.has_permissions(manage_guild=True)
async def prefix(ctx, args: str):
	"""Set the bot's prefix"""
	Regex = re.compile(r'[$!@#$%^&*\(\)_\-=+./,\|?`~][$!@#$%^&*\(\)_\-=+./,\|?`~]?')
	try:  # i do a try except block over these instead of just the if else is because if no args are passed discord passes a None statement instead of a string which triggers an error when using Regex.match()
		mo = Regex.match(args)
		if mo:
			async with bot.pool.acquire() as conn:
				try:
					await conn.execute('''INSERT INTO servers(serverid,prefix) VALUES($1,$2)''',
									   int(ctx.message.guild.id), mo.group(0))
				except:
					await conn.execute('''UPDATE servers SET prefix = $1 WHERE serverid = $2''', mo.group(0),
									   int(ctx.message.guild.id))
			await ctx.send('Your prefix has been updated to: ' + mo.group(0))
			prefix_cache[int(ctx.message.guild.id)] = mo.group(0)
		else:
			await ctx.send(
				'Invalid args , you can set anything from these \n```$!@#$%^&*()_-=+./,\|?`~``` \n You may also use any two value combination of these')
	except Exception as e:
		print(e)
		await ctx.send(
			'Invalid args , you can set anything from these \n```$!@#$%^&*()_-=+./,\|?`~``` \n You may also use any two value combination of these')


@bot.event
async def on_guild_join(guild):  # message for when it joins a server
	greeting = "Hey! I'm a bot with good taste in music ,use !help for info;You can enable or disable commands using !enable/disable and can change prefix using! prefix. Enjoy!"

	async with bot.pool.acquire() as conn:
		try:
			await conn.execute('''INSERT INTO servers(serverid,prefix) VALUES($1,$2)''',guild.id,'!')

		except asyncpg.exceptions.UniqueViolationError:
			await conn.execute('''UPDATE servers SET prefix = $1 WHERE serverid = $2''','!',guild.id)
		prefix_cache[int(guild.id)]='!'
	await guild.default_channel.send(greeting)


@bot.event
async def on_command_error(ctx,error):
	if isinstance(error,commands.errors.MissingRequiredArgument):
		mess = await ctx.send("This command requires an input.")
	elif isinstance(error,commands.errors.CommandOnCooldown):
		mess = await ctx.send("Slow down.")
		await asyncio.sleep(2)
		await bot.delete_message(mess)


@bot.event
async def on_ready():
	print("Connection Established")
	print(bot.user.name)
	print(bot.user.id)
	print('-----')
	membernum=len(list(bot.get_all_members()))
	print("Serving: "+str(membernum))
	await bot.change_presence(activity=discord.Game('patrician music'))

@bot.command()
@commands.has_permissions(manage_guild=True)
async def disable(ctx, args: str):
	"""remove a command from channel"""
	value = args.lower()
	things = []

	for command in list(bot.all_commands.keys()):
		if command not in non_removable:
			things.append(command)

	if value in things and ctx.message.guild.id in conditions_cache:
		if conditions_cache[ctx.message.guild.id] is None:
			conditions_cache[ctx.message.guild.id]={}
			conditions_cache[ctx.message.guild.id][value]=[ctx.message.channel.id]
			async with bot.pool.acquire() as conn:
				await conn.execute('''UPDATE servers SET conditions = $1 WHERE serverid = $2''',
								   json.dumps(conditions_cache[ctx.message.guild.id]),ctx.message.guild.id)
			await ctx.send(value + ' has been removed from this channel, you may re-enable by using the enable command')
		elif value not in conditions_cache[ctx.message.guild.id]:
			conditions_cache[ctx.message.guild.id][value]=[ctx.message.channel.id]
			print(conditions_cache)
			async with bot.pool.acquire() as conn:
				await conn.execute('''UPDATE servers SET conditions =$1 WHERE serverid = $2''',
							   json.dumps(conditions_cache[ctx.message.guild.id]),ctx.message.guild.id)
			await ctx.send(value + ' has been removed from this channel, you may re-enable by using the allow command')
		elif value in conditions_cache[ctx.message.guild.id] and ctx.message.channel.id not in conditions_cache[ctx.message.guild.id][value]:
			conditions_cache[ctx.message.guild.id][value].append(ctx.message.channel.id)
			async with bot.pool.acquire() as conn:
				await conn.execute('''UPDATE servers SET conditions =$1 WHERE serverid=$2''',
								   json.dumps(conditions_cache[ctx.message.guild.id]),ctx.message.guild.id)
			await ctx.send(value + ' has been removed from this channel, you may re-enable by using the allow command')

	else:
		await ctx.send('You can disable the following:\n'+str(things).strip('[]'))

@bot.command()
@commands.has_permissions(manage_guild=True)
async def enable(ctx,value:str):
	try:
		check = conditions_cache[ctx.message.guild.id][value]
		chann = int(ctx.message.channel.id)
		if chann in check:
			check.remove(chann)
			async with bot.pool.acquire() as conn:
				await conn.execute('''UPDATE servers SET conditions = $1 WHERE serverid = $2''',json.dumps(conditions_cache[ctx.message.guild.id]),ctx.message.guild.id)
				await ctx.send('The following command has been enabled in this channel: ' + value)
		else:
			await ctx.send('This command isn\'t disabled in this channel.')
	except (KeyError,TypeError) as e:
		await ctx.send('Something went wrong,you may have tried to enable a command that\'s already enabled.')


##OWNER COMMANDS
@bot.command()
@commands.check(is_owner)
async def load(ctx,name: str):
	"""Loads an extension."""
	try:
		bot.load_extension(name)
	except (AttributeError, ImportError) as e:
		await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
		return
	await ctx.send("{} loaded.".format(name))


@bot.command()
@commands.check(is_owner)
async def unload(ctx,name: str):
	"""Removes an extension"""
	bot.unload_extension(name)
	await ctx.send('Unloaded: ' + name)


@bot.command()
@commands.check(is_owner)
async def reload(ctx,name: str):
	"""Reloads an extension"""
	try:
		bot.unload_extension(name)
		bot.load_extension(name)
		await ctx.send('Extension has been reloaded')
	except Exception as e:
		await ctx.send('Something went horribly wrong: ' + str(e))


##loading extensions on startup
if __name__ == '__main__':
	for extension in startup_extensions:
		try:
			bot.load_extension(extension)
		except Exception as e:
			error = '{}:{}'.format(type(e).__name__, e)
			print('Loading extensions failed {}\n{}'.format(extension, error))

def conditions_check(ctx):#  I'm getting the nonetype is not subscriptable because the event to load db serverid and stuff is empty fields so it's adding None to the dict.
	#  it is possible that conditions_cache[serverid][command] just doesn't exist so it might flop out and give index error
	try:
		check = conditions_cache[ctx.message.guild.id][str(ctx.command)]
		channel = ctx.message.channel.id
		return channel not in check
	except:
		return True

bot.add_check(conditions_check)
bot.run(config['keys']['bot_token'])