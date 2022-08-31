import discord,re,aiohttp,io
from discord.ext import commands

class weekly(commands.Cog):
	def __init__(self,bot):
		self.bot = bot
		self.pool = bot.pool

	@commands.slash_command(guild_ids=[205630530237104128])
	async def weekly(self,ctx: discord.ApplicationContext,
	size: discord.Option(str,"3x3 , 4x4 , 5x5",required=False,default="3x3" )):
		await ctx.defer()
		Regex=re.compile(r'([A-Za-z0-9_\-]{2,15})?\s?([1-9]x[1-9])$')
		try:
			mo=Regex.search(size)
			if mo is None:
				await ctx.respond('You\'re passing invalid args, do `prefix weekly username [3x3,4x4,5x5,2x6] or `prefix weekly` if you have your last.fm username set')
			if mo.group(1):
				user = mo.group(1)
			else:
				async with self.pool.acquire() as conn:
					user = await conn.fetchval('SELECT lastfm FROM users WHERE userid = $1',ctx.author.id)

			if mo.group(2) in ['3x3','4x4','5x5','2x6']:
				size=mo.group(2)
			else:
				await ctx.respond('That\'s an invalid format, try one of these (3x3,4x4,5x5,2x6)')
		except TypeError:
			try:
				async with self.pool.acquire() as conn:
					user = await conn.fetchval('SELECT lastfm FROM users WHERE userid = $1',ctx.author.id)
				if user is None:
					raise AttributeError
				else:
					size ='3x3'
			except:
				await ctx.respond('You have to submit your account using `!fm set usernamehere`')

		link="http://tapmusic.net/collage.php?user="+user+"&type=7day&size="+size+"&caption=true"

		async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
				async with session.get(link) as resp:
					var = await resp.read()
					f = io.BytesIO(var)	
		await ctx.send_followup(file=discord.File(filename='image.png',fp=f),content=ctx.author.mention + ' here\'s your chart')

	@commands.slash_command(guild_ids=[205630530237104128])
	async def monthly(self,ctx: discord.ApplicationContext,
	size: discord.Option(str,"3x3 , 4x4 , 5x5",required=False,default="3x3" )):
		await ctx.defer()
		Regex=re.compile(r'([A-Za-z0-9_\-]{2,15})?\s?([1-9]x[1-9])$')
		try:
			mo=Regex.search(size)
			if mo is None:
				await ctx.respond('You\'re passing invalid args, do `prefix weekly username [3x3,4x4,5x5,2x6] or `prefix weekly` if you have your last.fm username set')
			if mo.group(1):
				user = mo.group(1)
			else:
				async with self.pool.acquire() as conn:
					user = await conn.fetchval('SELECT lastfm FROM users WHERE userid = $1',ctx.author.id)

			if mo.group(2) in ['3x3','4x4','5x5','2x6']:
				size=mo.group(2)
			else:
				await ctx.respond('That\'s an invalid format, try one of these (3x3,4x4,5x5,2x6)')
		except TypeError:
			try:
				async with self.pool.acquire() as conn:
					user = await conn.fetchval('SELECT lastfm FROM users WHERE userid = $1',ctx.author.id)
				if user is None:
					raise AttributeError
				else:
					size ='3x3'
			except:
				await ctx.respond('You have to submit your account using `!fm set usernamehere`')

		link="http://tapmusic.net/collage.php?user="+user+"&type=1month&size="+size+"&caption=true"

		async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
				async with session.get(link) as resp:
					var = await resp.read()
					f = io.BytesIO(var)	
		await ctx.send_followup(file=discord.File(filename='image.png',fp=f),content=ctx.author.mention + ' here\'s your chart')

	@commands.slash_command(guild_ids=[205630530237104128])
	async def yearly(self,ctx: discord.ApplicationContext,
	size: discord.Option(str,"3x3 , 4x4 , 5x5",required=False,default="3x3" )):
		await ctx.defer()
		Regex=re.compile(r'([A-Za-z0-9_\-]{2,15})?\s?([1-9]x[1-9])$')
		try:
			mo=Regex.search(size)
			if mo is None:
				await ctx.respond('You\'re passing invalid args, do `prefix weekly username [3x3,4x4,5x5,2x6] or `prefix weekly` if you have your last.fm username set')
			if mo.group(1):
				user = mo.group(1)
			else:
				async with self.pool.acquire() as conn:
					user = await conn.fetchval('SELECT lastfm FROM users WHERE userid = $1',ctx.author.id)

			if mo.group(2) in ['3x3','4x4','5x5','2x6']:
				size=mo.group(2)
			else:
				await ctx.respond('That\'s an invalid format, try one of these (3x3,4x4,5x5,2x6)')
		except TypeError:
			try:
				async with self.pool.acquire() as conn:
					user = await conn.fetchval('SELECT lastfm FROM users WHERE userid = $1',ctx.author.id)
				if user is None:
					raise AttributeError
				else:
					size ='3x3'
			except:
				await ctx.respond('You have to submit your account using `!fm set usernamehere`')

		link="http://tapmusic.net/collage.php?user="+user+"&type=12month&size="+size+"&caption=true"

		async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
				async with session.get(link) as resp:
					var = await resp.read()
					f = io.BytesIO(var)	
		await ctx.send_followup(file=discord.File(filename='image.png',fp=f),content=ctx.author.mention + ' here\'s your chart')

def setup(bot):
	bot.add_cog(weekly(bot))

