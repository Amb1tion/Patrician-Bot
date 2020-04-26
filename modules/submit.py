import discord,re
from discord.ext import commands

#channel id 587466715407843328 , server id = 448081955221798923
def server_check(ctx):
	return ctx.message.guild.id == 448081955221798923

class submit(commands.Cog):
	def __init__(self,bot):
		self.bot=bot

	@commands.command()
	@commands.check(server_check)
	async def submit(self,ctx):
		msg = "Reply to this conversation with your server invite and (brief) description. Read #how-to-list before applying."
		invalid="Your reply was late or you did not provide a valid discord invite(formatted as https://discord.gg/) use the !submit command again"
		confirm="Your application has been submitted and is being looked over by the mods , expect a reply in a few days"
		await ctx.message.author.send(msg)
		def check(message):
			return message.author.id == ctx.message.author.id and not message.guild
		regex = re.compile("https://(discord\.gg/[^\s]*)")
		reply = await self.bot.wait_for('message',check = check)
		var = regex.search(reply.content)
		if var is None:
			
			await ctx.message.author.send(invalid)
		else:
			thing = await self.bot.fetch_invite(var.group())
			if thing is not None:
				if thing.approximate_member_count > 30:
					say = "Sent by <@" + str(ctx.message.author.id) +">"
					channel = self.bot.get_channel(587466715407843328)
					await channel.send(reply.content)
					await channel.send(say)
					await ctx.message.author.send(confirm)
				else:
					await ctx.message.author.send("Your server does not have enough members to apply for submission , please re-read the #how-to-list channel carefully.")

			else:
				await ctx.message.author.send(invalid)
				
		
def setup(bot):
	bot.add_cog(submit(bot))