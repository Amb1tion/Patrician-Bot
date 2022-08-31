import discord,re
from discord.ext import commands
from discord.ext.commands import BucketType



class charts(commands.Cog):
	def __init__(self,bot):
		self.bot=bot
		self.pool=bot.pool


	@commands.slash_command(name="chart",description="save and recall an image link to your topster chart.")
	async def chart(self,ctx:discord.ApplicationContext,chart:discord.Option(str,name="chart_link",description="a link to your chart png,jpg or jpeg", default=None,Required=False)):
		if chart == None:
			try:
				async with self.pool.acquire() as conn:
					val = await conn.fetchval('SELECT chart FROM users WHERE userid = $1',ctx.author.id)
				await ctx.respond(val)
			except:
				await ctx.respond('Your chart isn\'t in the database , fix this by add the link in the optional parameter')
		else:
			Regex = re.compile(
			'^https://.*\.(com|net)/.+(\.jpg|\.png|\.jpeg)$|^http://.*\.(com|net)/.+(\.jpg|\.png|\.jpeg)$|.*\.(com|net)/.+(\.jpg|\.png|\.jpeg)$')
			try:
				var = Regex.search(chart)
				if var is not None:
					async with self.pool.acquire() as conn:
						try:
							await conn.execute('''INSERT INTO users(userid,chart) VALUES($1,$2)''',ctx.author.id,chart)
						except:
							await conn.execute('''UPDATE users SET chart = $1 WHERE userid = $2''',chart,ctx.author.id)
						await ctx.respond("Your chart has been submitted, you may call it using /chart",ephemeral=True)
				elif var is None:
					await ctx.respond("Invalid Input.",ephemeral=True)

			except Exception as e:
				print(e)
				await ctx.respond("Invalid Input",ephemeral=True)

	# @chart.command(description = 'Use this to submit your chart')
	# async def submit(self,ctx,link:str):
	# 	await ctx.message.channel.trigger_typing()
	# 	Regex = re.compile(
	# 		'^https://.*\.(com|net)/.+(\.jpg|\.png|\.jpeg)$|^http://.*\.(com|net)/.+(\.jpg|\.png|\.jpeg)$|.*\.(com|net)/.+(\.jpg|\.png|\.jpeg)$')
	# 	try:
	# 		var = Regex.search(link)
	# 		if var is not None:
	# 			async with self.pool.acquire() as conn:
	# 				try:
	# 					await conn.execute('''INSERT INTO users(userid,chart) VALUES($1,$2)''',ctx.message.author.id,link)
	# 				except:
	# 					await conn.execute('''UPDATE users SET chart = $1 WHERE userid = $2''',link,ctx.message.author.id)
	# 				await ctx.send("Your chart has been submitted, you may call it using !chart")
	# 		elif var is None:
	# 			await ctx.send("Invalid Input.")

	# 	except Exception as e:
	# 		print(e)
	# 		await ctx.send("Invalid Input")


	
	# @chart.command(pass_context=True , description= "Tag whoever's chart you want to judge. example: !chart get @Amb1tion#6969")
	# async def get(self,ctx,m:discord.Member):
	# 	await ctx.message.channel.trigger_typing()
	# 	async with self.pool.acquire() as conn:
	# 		try:
	# 			val = await conn.fetchval('SELECT chart FROM users WHERE userid = $1',m.id)
	# 			await ctx.send(val)
	# 		except:
	# 			await ctx.send('Something went wrong , maybe they haven\'t submitted a chart yet?')

def setup(bot):
	bot.add_cog(charts(bot))
