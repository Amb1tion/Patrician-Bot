import re,json, discord, logging, datetime, configparser, asyncpg, asyncio
from discord.ext import commands

config = configparser.ConfigParser()
config.read('bot_config.ini')
startup_extensions = ['modules.youtube',
					  'modules.charts',
					  'modules.lyrics',
					  'modules.lastfm',
					  'modules.admin',
					  'modules.rym',
					  'modules.general',
					  'modules.weekly',
					  'modules.quotes']

prefix_cache = {}

conditions_cache = {}

non_removable = ['help', 'prefix', 'remove', 'info', 'ball_add', 'hug_add']

async def get_pre(bot, message):
	if int(message.server.id) in prefix_cache and int(message.server.id) is not None:
		return prefix_cache[int(message.server.id)]


bot = commands.Bot(command_prefix=get_pre)
# setting up logging
# logger = logging.getLogger('discord')
# logger.setLevel(logging.DEBUG)
# handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
# handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
# logger.addHandler(handler)


def is_owner(ctx):  # defining the bot owner check
	return ctx.message.author.id == '197938114218426370'

async def stuff(bot): #creating a pool connection to the database for connecctions
	if not hasattr(bot, 'pool'):
		bot.pool = await asyncpg.create_pool(config['keys']['db'])


asyncio.get_event_loop().run_until_complete(stuff(bot))



async def prefix_fetch():#establishing prefix cache for all servers (possibly inefficient ?)
	if prefix_cache == {}:  # should run when the bot starts
		async with bot.pool.acquire() as conn:  # getting values to append to prefix_cache
			async with conn.transaction():
				async for serverid, prefix in conn.cursor('SELECT serverid,prefix FROM servers'):
					prefix_cache[serverid] = prefix


asyncio.get_event_loop().run_until_complete(prefix_fetch())


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
print(conditions_cache)

# async def invite_task():
#	server=await bot.get_server('198621771451072512')
#	if boolean:
#		oginvite_list= await bot.invites_from(server)
#		boolean = False
#	await asyncio.sleep(60)
#	compar_invite_list=await bot.invites_from(server)
#	if oginvite_list != compar_invite_list:
#		modchat=await bot.get_channel('198688286485512193')
#		message ='The following invite/s has/have been made: ' +  set(compar_invite_list) - set(oginvite_list)
#		await bot.send_message(modchat,message)
# bot.loop.create_task(invite_task())
#prototype code , doesn't work yet


@bot.event
async def on_ready():  # print the following in console to indicate bot has started
	print("Connection Established")
	print(bot.user.name)
	print(bot.user.id)
	print('-----')
	await bot.change_presence(game=discord.Game(name='patrician music'))
	if not hasattr(bot, 'uptime'):
		bot.uptime = datetime.datetime.utcnow()


@bot.event
async def on_member_update(before, after):  # fixes a friend's nickname to stop him from changing it
	if before.id == '168058699275960320':
		await bot.change_nickname(after, 'NoFace')


@bot.event
async def on_server_join(server):  # message for when it joins a server
	greeting = "Hey! I'm a bot with good taste in music ,use !help for info;You can enable or disable commands using !enable/disable and can change prefix using! prefix. Enjoy!"

	async with bot.pool.acquire() as conn:
		try:
			await conn.execute('''INSERT INTO servers(serverid,prefix) VALUES($1,$2)''',int(server.id),'!')

		except asyncpg.exceptions.UniqueViolationError:
			await conn.execute('''UPDATE servers SET prefix = $1 WHERE serverid = $2''','!',int(server.id))
		prefix_cache[int(server.id)]='!'
	await bot.send_message(server.default_channel, content=greeting)

@bot.event
async def on_command_error(error, ctx):  # message for cooldown error
	if isinstance(error, commands.errors.CommandOnCooldown):
		mess = await bot.send_message(ctx.message.channel, "Slow down you turbo pleb")
		await bot.delete_message(ctx.message)  # delete message that caused cooldown
		await asyncio.sleep(2)
		await bot.delete_message(mess)  # delete bot message after 2 second delay


@bot.command(pass_context=True)
@commands.has_permissions(manage_server=True)
async def prefix(ctx, args: str):
	"""Set the bot's prefix"""
	Regex = re.compile(r'[$!@#$%^&*\(\)_\-=+./,\|?`~][$!@#$%^&*\(\)_\-=+./,\|?`~]?')
	try:  # i do a try except block over these instead of just the if else is because if no args are passed discord passes a None statement instead of a string which triggers an error when using Regex.match()
		mo = Regex.match(args)
		if mo:
			async with bot.pool.acquire() as conn:
				try:
					await conn.execute('''INSERT INTO servers(serverid,prefix) VALUES($1,$2)''',
									   int(ctx.message.server.id), mo.group(0))
				except:
					await conn.execute('''UPDATE servers SET prefix = $1 WHERE serverid = $2''', mo.group(0),
									   int(ctx.message.server.id))
			await bot.say('Your prefix has been updated to: ' + mo.group(0))
			prefix_cache[int(ctx.message.server.id)] = mo.group(0)
		else:
			await bot.say(
				'Invalid args , you can set anything from these \n```$!@#$%^&*()_-=+./,\|?`~``` \n You may also use any two value combination of these')
	except Exception as e:
		print(e)
		await bot.say(
			'Invalid args , you can set anything from these \n```$!@#$%^&*()_-=+./,\|?`~``` \n You may also use any two value combination of these')




@bot.command(pass_context=True)
@commands.has_permissions(manage_server=True)
async def disable(ctx, args: str):
	"""remove a command from channel"""
	value = args.lower()
	things = []

	for command in list(bot.commands.keys()):
		if command not in non_removable:
			things.append(command)

	if value in things and int(ctx.message.server.id) in conditions_cache:
		if conditions_cache[int(ctx.message.server.id)] is None:
			conditions_cache[int(ctx.message.server.id)]={}
			conditions_cache[int(ctx.message.server.id)][value]=[int(ctx.message.channel.id)]
			async with bot.pool.acquire() as conn:
				await conn.execute('''UPDATE servers SET conditions = $1 WHERE serverid = $2''',
								   json.dumps(conditions_cache[int(ctx.message.server.id)]),int(ctx.message.server.id))
			await bot.say(value + ' has been removed from this channel, you may re-enable by using the allow command')
		elif value not in conditions_cache[int(ctx.message.server.id)]:
			conditions_cache[int(ctx.message.server.id)][value]=[int(ctx.message.channel.id)]
			print(conditions_cache)
			async with bot.pool.acquire() as conn:
				await conn.execute('''UPDATE servers SET conditions =$1 WHERE serverid = $2''',
							   json.dumps(conditions_cache[int(ctx.message.server.id)]),int(ctx.message.server.id))
			await bot.say(value + ' has been removed from this channel, you may re-enable by using the allow command')
		elif value in conditions_cache[int(ctx.message.server.id)] and int(ctx.message.channel.id) not in conditions_cache[int(ctx.message.server.id)][value]:
			conditions_cache[int(ctx.message.server.id)][value].append(int(ctx.message.channel.id))
			async with bot.pool.acquire() as conn:
				await conn.execute('''UPDATE servers SET conditions =$1 WHERE serverid=$2''',
								   json.dumps(conditions_cache[int(ctx.message.server.id)]),int(ctx.message.server.id))
			await bot.say(value + ' has been removed from this channel, you may re-enable by using the allow command')

	else:
		await bot.say('You can disable the following:\n'+str(things).strip('[]'))

@bot.command(pass_context=True)
@commands.has_permissions(manage_server=True)
async def enable(ctx,value:str):
	try:
		check = conditions_cache[int(ctx.message.server.id)][value]
		chann = int(ctx.message.channel.id)
		if chann in check:
			check.remove(chann)
			async with bot.pool.acquire() as conn:
				await conn.execute('''UPDATE servers SET conditions = $1 WHERE serverid = $2''',json.dumps(conditions_cache[int(ctx.message.server.id)]),int(ctx.message.server.id))
				await bot.say('The following command has been enabled in this channel: ' + value)
		else:
			await bot.say('This command isn\'t disabled in this channel.')
	except (KeyError,TypeError) as e:
		await bot.say('Something went wrong,you may have tried to enable a command that\'s already enabled.')
@bot.command()  # bot info command
async def info(*args):
	return await bot.say("My code is currently under construction." +
						 "\nMy prefix is '!' and working commands so far are `yt`,`lyrics`,`fm`,`chart` and`choose` , use `!help` to learn more for each command")


@bot.command()
@commands.check(is_owner)
async def load(name: str):
	"""Loads an extension."""
	try:
		bot.load_extension(name)
	except (AttributeError, ImportError) as e:
		await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
		return
	await bot.say("{} loaded.".format(name))


@bot.command()
@commands.check(is_owner)
async def unload(name: str):
	"""Removes an extension"""
	bot.unload_extension(name)
	await bot.say('Unloaded: ' + name)


@bot.command()
@commands.check(is_owner)
async def reload(name: str):
	"""Reloads an extension"""
	try:
		bot.unload_extension(name)
		bot.load_extension(name)
		await bot.say('Extension has been reloaded')
	except Exception as e:
		await bot.say('Something went horribly wrong: ' + str(e))


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
		check = conditions_cache[int(ctx.message.server.id)][str(ctx.command)]
		channel = int(ctx.message.channel.id)
		return channel not in check
	except:
		return True


bot.add_check(conditions_check)#help,prefix,remove,load,unload,reload,ball_add,hug_add,info
bot.run(config['keys']['bot_token'])
