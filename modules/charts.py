import discord,re
from discord.ext import commands
from discord.ext.commands import BucketType



class chartsCog(commands.Cog):
	def __init__(self,bot):
		self.bot=bot
		self.pool=bot.pool


	@commands.group()
	async def chart(self,ctx):
		if ctx.invoked_subcommand is None:
			try:
				async with self.pool.acquire() as conn:
					val = await conn.fetchval('SELECT chart FROM users WHERE userid = $1',ctx.message.author.id)
				await ctx.message.channel.send(val)
			except:
				await ctx.message.channel.send('Your chart isn\'t in the database , fix this by doing `!chart submit imagelinkhere`')
	
	@chart.command(description = 'Use this to submit your chart')
	async def submit(self,ctx,link:str):
		await ctx.message.channel.trigger_typing()
		Regex = re.compile(
			'^https://.*\.(com|net)/.+(\.jpg|\.png|\.jpeg)$|^http://.*\.(com|net)/.+(\.jpg|\.png|\.jpeg)$|.*\.(com|net)/.+(\.jpg|\.png|\.jpeg)$')
		try:
			var = Regex.search(link)
			if var is not None:
				async with self.pool.acquire() as conn:
					try:
						await conn.execute('''INSERT INTO users(userid,chart) VALUES($1,$2)''',ctx.message.author.id,link)
					except:
						await conn.execute('''UPDATE users SET chart = $1 WHERE userid = $2''',link,ctx.message.author.id)
					await ctx.message.channel.send("Your chart has been submitted, you may call it using !chart")
			elif var is None:
				await ctx.message.channel.send("Invalid Input.")

		except Exception as e:
			print(e)
			await ctx.message.channel.send("Invalid Input")


	
	@chart.command(pass_context=True , description= "Tag whoever's chart you want to judge. example: !chart get @Amb1tion#6969")
	async def get(self,ctx,m:discord.Member):
		await ctx.message.channel.trigger_typing()
		async with self.pool.acquire() as conn:
			try:
				val = await conn.fetchval('SELECT chart FROM users WHERE userid = $1',m.id)
				await ctx.message.channel.send(val)
			except:
				await ctx.message.channel.send('Something went wrong , maybe they haven\'t submitted a chart yet?')

def setup(bot):
	bot.add_cog(chartsCog(bot))
