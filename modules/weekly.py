import discord,os,json,re,aiohttp,async_timeout,io,asyncpg
from discord.ext import commands
from discord.ext.commands import BucketType

class weekly():
	def __init__(self,bot):
		self.bot = bot
		self.pool=bot.pool





	@commands.command(pass_context=True)
	@commands.cooldown(rate=1.0,per=15.0,type=commands.BucketType.channel)
	async def weekly(self,ctx,*,args=None):
		await self.bot.send_typing(ctx.message.channel)
		Regex=re.compile(r'([A-Za-z0-9_\-]{2,15})?\s?([1-9]x[1-9])$')
		try:
			mo=Regex.search(args)
			if mo is None:
				await self.bot.say('You\'re passing invalid args, do `prefix weekly username [3x3,4x4,5x5,2x6] or `prefix weekly` if you have your last.fm username set')
			if mo.group(1):
				user = mo.group(1)
			else:
				async with self.pool.acquire() as conn:
					user = await conn.fetchval('SELECT lastfm FROM users WHERE userid = $1',int(ctx.message.author.id))

			if mo.group(2) in ['3x3','4x4','5x5','2x6']:
				#rows,cols = mo.group(2).split('x')
				size=mo.group(2)
			else:
				await self.bot.say('That\'s an invalid format, try one of these (3x3,4x4,5x5,2x6)')
		except TypeError:
			try:
				async with self.pool.acquire() as conn:
					user = await conn.fetchval('SELECT lastfm FROM users WHERE userid = $1',int(ctx.message.author.id))
				if user is None:
					await self.bot.say('You have to submit your username using `!fm set username')
					raise AttributeError
			except:
				await self.bot.say('You have to submit your plen username using `!fm set usernamehere`')
				size='3x3'
		link="http://tapmusic.net/collage.php?user="+user+"&type=7day&size="+size+"&caption=true"

		with aiohttp.ClientSession() as session:
			async with session.get(link) as resp:
				var = await resp.read()
				f = io.BytesIO(var)
		await self.bot.send_file(ctx.message.channel,f,filename='image.png',content=ctx.message.author.mention + ' here\'s your entry level chart')

	@commands.command(pass_context=True)
	@commands.cooldown(rate=1.0, per=15.0, type=commands.BucketType.channel)
	async def monthly(self, ctx, *, args=None):
		await self.bot.send_typing(ctx.message.channel)
		Regex = re.compile(r'([A-Za-z0-9_\-]{2,15})?\s?([1-9]x[1-9])$')
		try:
			mo = Regex.search(args)
			if mo is None:
				await self.bot.say(
					'You\'re passing invalid args, do `prefix weekly username [3x3,4x4,5x5,2x6] or `prefix weekly` if you have your last.fm username set')
			if mo.group(1):
				user = mo.group(1)
			else:
				async with self.pool.acquire() as conn:
					user = await conn.fetchval('SELECT lastfm FROM users WHERE userid = $1', int(ctx.message.author.id))

			if mo.group(2) in ['3x3', '4x4', '5x5', '2x6']:
				# rows,cols = mo.group(2).split('x')
				size = mo.group(2)
			else:
				await self.bot.say('That\'s an invalid format, try one of these (3x3,4x4,5x5,2x6)')
		except TypeError:
			try:
				async with self.pool.acquire() as conn:
					user = await conn.fetchval('SELECT lastfm FROM users WHERE userid = $1', int(ctx.message.author.id))
				if user is None:
					await self.bot.say('You have to submit your username using `!fm set username')
					raise AttributeError
			except:
				await self.bot.say('You have to submit your plen username using `!fm set usernamehere`')
				size = '3x3'
		link = "http://tapmusic.net/collage.php?user=" + user + "&type=1month&size=" + size + "&caption=true"

		with aiohttp.ClientSession() as session:
			async with session.get(link) as resp:
				var = await resp.read()
				f = io.BytesIO(var)
		await self.bot.send_file(ctx.message.channel, f, filename='image.png',
								 content=ctx.message.author.mention + ' here\'s your entry level chart')
		print(link)


	@commands.command(pass_context=True)
	@commands.cooldown(rate=1.0, per=15.0, type=commands.BucketType.channel)
	async def alltime(self, ctx, *, args=None):
		await self.bot.send_typing(ctx.message.channel)
		Regex = re.compile(r'([A-Za-z0-9_\-]{2,15})?\s?([1-9]x[1-9])$')
		try:
			mo = Regex.search(args)
			if mo is None:
				await self.bot.say(
					'You\'re passing invalid args, do `prefix weekly username [3x3,4x4,5x5,2x6] or `prefix weekly` if you have your last.fm username set')
			if mo.group(1):
				user = mo.group(1)
			else:
				async with self.pool.acquire() as conn:
					user = await conn.fetchval('SELECT lastfm FROM users WHERE userid = $1', int(ctx.message.author.id))

			if mo.group(2) in ['3x3', '4x4', '5x5', '2x6']:
				# rows,cols = mo.group(2).split('x')
				size = mo.group(2)
			else:
				await self.bot.say('That\'s an invalid format, try one of these (3x3,4x4,5x5,2x6)')
		except TypeError:
			try:
				async with self.pool.acquire() as conn:
					user = await conn.fetchval('SELECT lastfm FROM users WHERE userid = $1', int(ctx.message.author.id))
				if user is None:
					await self.bot.say('You have to submit your username using `!fm set username')
					raise AttributeError
			except:
				await self.bot.say('You have to submit your plen username using `!fm set usernamehere`')
				size = '3x3'
		link = "http://tapmusic.net/collage.php?user=" + user + "&type=overall&size=" + size + "&caption=true"
		print(link)

		with aiohttp.ClientSession() as session:
			async with session.get(link) as resp:
				var = await resp.read()
				f = io.BytesIO(var)
		await self.bot.send_file(ctx.message.channel, f, filename='image.png',
								 content=ctx.message.author.mention + ' here\'s your entry level chart')


def setup(bot):
	bot.add_cog(weekly(bot))
