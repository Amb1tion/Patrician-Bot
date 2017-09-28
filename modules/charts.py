import discord,json,os
from discord.ext import commands
from discord.ext.commands import BucketType



class charts():
	def __init__(self,bot):
		self.bot=bot
		self.pool=bot.pool


	@commands.group(pass_context=True)
	@commands.cooldown(rate=1, per=10, type=commands.BucketType.channel)
	async def chart(self,ctx):
		if ctx.invoked_subcommand is None:
			try:
				async with self.pool.acquire() as conn:
					val = await conn.fetchval('SELECT chart FROM users WHERE userid = $1',int(ctx.message.author.id))
				await self.bot.say(val)
			except:
				await self.bot.say('Your chart isn\'t in the database , fix this by doing `!chart submit imagelinkhere`')
			#with open(os.path.join(os.getcwd(),'database','charts.json'),'r') as database:
			#	json_decoded = json.load(database)
			#	if ctx.message.author.id in json_decoded:
			#		await self.bot.say(json_decoded[ctx.message.author.id])
		#else:
		#	await self.bot.say("your chart is not in the database , please submit it by using `!chart submit yourchartlinkhere` in spam-fiesta")
	
	@chart.command(pass_context=True, description = 'Use this to submit your chart')
	async def submit(self,ctx,link:str):
		await self.bot.send_typing(ctx.message.channel)
		async with self.pool.acquire() as conn:
			try:
				await conn.execute('''INSERT INTO users(userid,chart) VALUES($1,$2)''',int(ctx.message.author.id),link)
			except:
				await conn.execute('''UPDATE users SET chart = $1 WHERE userid = $2''',link,int(ctx.message.author.id))
		#with open(os.path.join(os.getcwd(),'database','charts.json'),'r') as database:
		#	json_decoded = json.load(database)
		#	json_decoded[ctx.message.author.id]=link
		#with open(os.path.join(os.getcwd(),'database','charts.json'),'w') as database:
		#	json.dump(json_decoded,database)
		await self.bot.say("Your chart has been submitted, you may call it using !chart")
		#await self.bot.send_message(self.bot.get_channel('246013926163218432'), ctx.message.author.mention+' posted the following chart '+ link)
	
	@chart.command(pass_context=True , description= "Tag whoever's chart you want to judge. example: !chart get @Amb1tion#6969")
	@commands.cooldown(rate=1, per=10, type=commands.BucketType.channel)
	async def get(self,ctx,m:discord.Member):
		await self.bot.send_typing(ctx.message.channel)
		async with self.pool.acquire() as conn:
			try:
				val = await conn.fetchval('SELECT chart FROM users WHERE userid = $1',int(m.id))
				await self.bot.say(val)
			except:
				await self.bot.say('Something went wrong , maybe they\'re too pleb for a chart')  
		#with open(os.path.join(os.getcwd(),'database','charts.json'),'r') as database:
		#	json_decoded = json.load(database)
		#	if m.id in json_decoded:
		#		return await self.bot.say(json_decoded[m.id])
		#	else:
		#		return await self.bot.say("That user has not submitted their topster yet.") 

def setup(bot):
	bot.add_cog(charts(bot))
