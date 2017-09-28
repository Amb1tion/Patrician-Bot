import discord,datetime
from discord.ext import commands

class admin():
	def __init__(self,bot):
		self.bot = bot

	#@commands.command(pass_context=True)
	#@commands.has_any_role('admin','king crimson 👑','talking heads 🗣')
	#async def muted(self,ctx,args:discord.Member):
		
		
	
	
	
	
	
	@commands.command(pass_context=True)
	@commands.has_permissions(manage_messages=True) #when removing server based hardcoding think of making a list where user can add mod roles which can use admin commands
	async def clear(self,ctx,*args):
		def check(message):
			return ctx.message.mentions[0].id == message.author.id
		print(args)
		if not ctx.message.mentions:
			try:
				limit = int(args[0])
				await self.bot.purge_from(ctx.message.channel,limit=limit+1)
			except IndexError:
				await self.bot.say('specify the number of messages you wish to delete (the format is `!clear @user 4` or `!clear 4`)')
		else:
			try:
				print(args[1])
				limit = int(args[1])
				print(limit)
				await self.bot.purge_from(ctx.message.channel,limit=limit+1,check=check)
			except IndexError:
				await self.bot.say('specify the number of messages you wish to delete (the format is `!clear @user 4` or `!clear 4`)')
	
	
	
	



def setup(bot):
	bot.add_cog(admin(bot))
