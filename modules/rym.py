import discord,os,re
from discord.ext import commands
from discord.ext.commands import BucketType




class rymCog(commands.Cog):
	def __init__(self,bot):
		self.bot=bot
		self.pool=bot.pool
	
	
	@commands.group()
	async def rym(self,ctx):
		if ctx.invoked_subcommand is None:
			async with self.pool.acquire() as conn:
				try:
					user = await conn.fetchval('SELECT rym FROM users WHERE userid=$1',ctx.message.author.id)
					link = "https://rateyourmusic.com/~"+user
					await ctx.send("Here is your well maintained and organized account! "+link)
				except:
					await ctx.send("Huh? i couldn't find your account try submitting it with `rym set username`")

 


	@rym.command()
	async def set(self,ctx,args:str):
		Regex=re.compile('^([A-Za-z_.0-9]{3,24}$)')
		mo=Regex.search(args)
		if mo is not None:
			async with self.pool.acquire() as conn:
				try:
					await conn.execute('''INSERT INTO users(userid,rym) VALUES($1,$2)''',int(ctx.message.author.id),args)

				except:
					await conn.execute('''UPDATE users SET rym = $1 WHERE userid = $2''',args,int(ctx.message.author.id))
				await ctx.send("Your account has been submitted!")


		else:
			await ctx.send('That does not look like a valid username to me.')

	@rym.command(pass_context=True)

	async def get(self,ctx,args:discord.Member):
		try:
			async with self.pool.acquire() as conn:
				user = await conn.fetchval('SELECT rym FROM users WHERE userid = $1',int(ctx.message.mentions[0].id))
				link = "https://rateyourmusic.com/~" + user
				await ctx.send("Here's the account: "+link)
		except:
			await ctx.send("Something went wrong, maybe they don't have a rym.")



def setup(bot):
	bot.add_cog(rymCog(bot))
