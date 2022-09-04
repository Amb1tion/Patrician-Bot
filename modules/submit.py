import discord,re
from discord.ext import commands

def server_check(ctx):
	return ctx.guild_id == 448081955221798923
def channel_check(ctx):
	return ctx.channel_id == 318685903331655680

class MyModal(discord.ui.Modal):
	def __init__(self,msg:discord.Message,recipient,pool,decision,server,channel,*args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		self.decision = decision
		self.server = server
		self.message = msg
		self.author=recipient
		self.pool = pool
		self.channel=channel
		
		# self.add_item(discord.ui.InputText(label="Short Input"))
		self.add_item(discord.ui.InputText(label=self.decision, style=discord.InputTextStyle.long))

	async def callback(self, interaction: discord.Interaction):
		embed = discord.Embed(title=self.server)
		
		# embed.add_field(name="Short Input", value=self.children[0].value)
		embed.add_field(name=self.decision+": ", value=self.children[0].value)
		embed.add_field(name="Submitted By",value = "<@"+str(self.message.mentions[0].id)+">",inline=False)
		embed.set_footer(text="Music Server Portal Application Status")
		# await interaction.response.send_message(embeds=[embed])
		if self.decision == "Rejected":
			await self.message.mentions[0].send(embeds=[embed])
		embed.add_field(name="Evaluated By: ",value = "<@"+str(interaction.user.id)+">")

		await self.channel.send(embeds=[embed])
		async with self.pool.acquire() as conn:	
				await conn.execute('''DELETE FROM submissions WHERE msgid=$1''',self.message.id)
		await self.message.delete()
		await interaction.response.send_message(self.decision+": "+self.server ,ephemeral=True)

class submit(commands.Cog):
	def __init__(self,bot):
		self.bot = bot
		self.pool = bot.pool
		self.applications_channel=587466715407843328
		self.processed_channel=457979407253110797
	
	@commands.slash_command(guild_ids=[448081955221798923])
	@commands.check(server_check)
	async def submit(self,ctx: discord.ApplicationContext):
		msg = "Reply to this conversation with your server invite and (brief) description. Read #how-to-list before applying."
		invalid="Your reply was late or you did not provide a valid discord invite(formatted as https://discord.gg/) use the !submit command again"
		confirm="Your application has been submitted and is being looked over by the mods , expect a reply in a few days"
		await ctx.author.send(msg)
		await ctx.respond("Please check your DMs",ephemeral=True)
		def check(message):
			return message.author.id == ctx.author.id and not message.guild
		regex = re.compile("https://(discord\.gg/[^\s]*)")
		reply = await self.bot.wait_for('message',check = check)
		var = regex.search(reply.content)
		if var is None:
			
			await ctx.author.send(invalid)
		else:
			try:
				thing = await self.bot.fetch_invite(var.group())
				guild_id=thing.guild.id
				if thing is not None:
					if thing.approximate_member_count >= 50:
						try:
							async with self.pool.acquire() as conn:
								temp=await conn.fetchval('''SELECT msgid FROM submissions WHERE serverid=$1''',guild_id)# this block only executes to indicate that the server is already submitted
								if temp:
									await ctx.author.send("This server has already been submitted earlier and is pending approval by the mod team.")
								else:
									raise Exception("Next Block")
						except Exception as e:
							say = "Sent by <@" + str(ctx.author.id) +">"
							channel = self.bot.get_channel(self.applications_channel)
							final=await channel.send(reply.content+"""\n\n"""+say)
							await ctx.author.send(confirm) 
							async with self.pool.acquire() as conn:
								await conn.execute('''INSERT INTO submissions(msgid,message,userid,serverid) VALUES($1,$2,$3,$4)''',final.id,reply.content,reply.author.id,guild_id)
					else:
						await ctx.author.send("Your server does not have enough members to apply for submission , please re-read the #how-to-list channel carefully.")

				else:
					await ctx.author.send(invalid)
			except:
				await ctx.author.send(invalid)
	@commands.message_command(name="Reject Application",guild_ids=[448081955221798923]) 
	@commands.has_permissions(manage_channels=True)
	async def reject(self,ctx:discord.ApplicationContext, message: discord.Message):
		regex = re.compile("https://(discord\.gg/[^\s]*)")
		var = regex.search(message.content)
		channel = self.bot.get_channel(self.processed_channel)
		try:
			thing = await self.bot.fetch_invite(var.group())
			server_name = thing.guild.name
			async with self.pool.acquire() as conn:
				recipient = await conn.fetchval('''SELECT userid FROM submissions WHERE msgid =$1''',message.id)
			author=self.bot.get_user(recipient)
			modal = MyModal(title=server_name,msg=message,recipient=author,pool=self.pool,decision="Rejected",server=server_name,channel=channel)
			await ctx.send_modal(modal)
		except discord.NotFound:
			await ctx.respond('This has an expired invite , please use the delete option from the menu')

	
	@commands.message_command(name="Delete Application",guild_ids=[448081955221798923]) 
	@commands.has_role('Portal Manager')
	async def Delete(self,ctx:discord.ApplicationContext, message: discord.Message):

		try:
			async with self.pool.acquire() as conn:
			# recipient = await conn.fetchval('''SELECT userid FROM submissions WHERE msgid =$1''',message.id)
				await conn.execute('''DELETE FROM submissions WHERE msgid=$1''',message.id)
				await message.delete()
				await ctx.respond("Message Deleted",ephemeral=True)
		except:
			await ctx.respond("invalid message selection")

	
	@commands.message_command(name="Accept Application",guild_ids=[448081955221798923]) 
	@commands.has_role('Portal Manager')
	async def Accept(self,ctx:discord.ApplicationContext, message: discord.Message):
		regex = re.compile("https://(discord\.gg/[^\s]*)")
		var = regex.search(message.content)
		channel = self.bot.get_channel(self.processed_channel)
		thing = await self.bot.fetch_invite(var.group())
		server_name = thing.guild.name
		async with self.pool.acquire() as conn:
			recipient = await conn.fetchval('''SELECT userid FROM submissions WHERE msgid =$1''',message.id)
		author=self.bot.get_user(recipient)
		modal = MyModal(title=server_name,msg=message,recipient=author,pool=self.pool,decision="Accepted",server=server_name,channel=channel)
		await ctx.send_modal(modal)
# handle dead server invite errors and members left the server errors

def setup(bot):
	bot.add_cog(submit(bot))