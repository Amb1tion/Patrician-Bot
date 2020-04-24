import discord,datetime
from discord.ext import commands

class adminCog(commands.Cog):
	def __init__(self,bot):
		self.bot = bot	
	
	@commands.command()
	@commands.has_permissions(manage_messages = True)
	async def clear(self,ctx,*args):
		def check(message):
			return ctx.message.mentions[0].id == message.author.id
		print(args)
		if not ctx.message.mentions:
			try:
				limit = int(args[0])
				await ctx.message.channel.purge(limit=limit+1)
			except IndexError:
				await ctx.message.channel.send('specify the number of messages you wish to delete (the format is `!clear @user 4` or `!clear 4`)')
		else:
			try:
				print(args[1])
				limit = int(args[1])
				print(limit)
				await ctx.message.channel.purge(limit=limit+1,check=check)
			except IndexError:
				await ctx.message.channel.send('specify the number of messages you wish to delete (the format is `!clear @user 4` or `!clear 4`)')
	
	
	
	



def setup(bot):
	bot.add_cog(adminCog(bot))
