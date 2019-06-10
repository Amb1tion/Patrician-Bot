import discord,re
from discord.ext import commands
def server_check(ctx):
	return ctx.message.server.id == "448081955221798923"

class submit():
	def __init__(self,bot):
		self.bot=bot

	@commands.command(pass_context=True)
	@commands.check(server_check)
	async def submit(self,ctx):
		msg = "Reply to this conversation with your server invite and (brief) description. Read #how-to-list before applying."
		invalid="Your reply was late or you did not provide a valid discord invite(formatted as https://discord.gg/) use the !submit command again"
		case1="var is none"
		await self.bot.send_message(ctx.message.author,msg)
		def check(message):
			return True
		regex = re.compile("https://(discord\.gg/[^\s]*)")
		reply = await self.bot.wait_for_message(author = ctx.message.author,check = check)
		var = regex.search(reply.content)
		if var is None:
			
			await self.bot.send_message(ctx.message.author,invalid)
		else:
			
			thing = await self.bot.get_invite(var.group())
			if thing is not None:
				say = "Sent by <@" + ctx.message.author.id +">"
				await self.bot.send_message(discord.Object("587466715407843328"),reply.content)
				await self.bot.send_message(discord.Object("587466715407843328"),say)

			else:
				await self.bot.send_message(ctx.message.author,invalid)
				
	@commands.command(pass_context=True)
	async def regex(self,ctx,msg:str):
		regex = re.compile(r'discord\.gg/[^\s]*')
		var = regex.search(msg)
		if var is None:
			await self.bot.say("none")
		else:
			await self.bot.say(var.group())
		
def setup(bot):
	bot.add_cog(submit(bot))