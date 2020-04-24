import discord,os,json,re,random
from discord.ext import commands
from discord.ext.commands import BucketType
import discord.utils


def testing_check(ctx):
	return ctx.message.channel.id == 198702690191147009
def server_check(ctx):
	return ctx.message.server.id == 198621771451072512

class generalCog(commands.Cog):
	def __init__(self,bot):
		self.bot=bot

	@commands.command()
	async def joindate(self,ctx,member=None):
		if member is not None:
			await ctx.message.channel.send("{0.name} joined in {0.joined_at}".format(ctx.message.mentions[0]))
		else:
			await ctx.message.channel.send("{0.name} joined in {0.joined_at}".format(ctx.message.author))

	@commands.command()
	async def choose(self,*choices:str):
		#rewrite this to have an array where the input string goes then split it with multiple choice for characters to split on
		if len(choices) < 2:
			return await ctx.message.channel.send("weren't choices between *multiple* things ??")
		else:
			return await ctx.message.channel.send(random.choice(choices))
	
	@commands.command(pass_context=True)
	@commands.check(server_check)
	async def brave(self,ctx):
		role = discord.utils.get(ctx.message.server.roles,name='brave soul')
		if role not in ctx.message.author.roles:
			await ctx.message.author.add_roles(role)
			await self.bot.say('I don\'t know why you\'d want to go to that hive of scum and villainy.... but take the role you masochist..')
		else:
			await self.bot.say('I ain\'t touching that role u keep it...')
			await ctx.message.author.remove_roles(role)

def setup(bot):
	bot.add_cog(generalCog(bot))
