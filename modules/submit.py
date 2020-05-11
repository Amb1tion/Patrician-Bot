import discord,re,asyncpg,aiohttp
from discord.ext import commands
from discord import errors
#channel id 587466715407843328 , server id = 448081955221798923
def server_check(ctx):
	return ctx.message.guild.id == 448081955221798923 

class submit(commands.Cog):
	def __init__(self,bot):
		self.bot=bot
		self.pool = bot.pool
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
			try:
				thing = await self.bot.fetch_invite(var.group())
				guild_id=thing.guild.id
				if thing is not None:
					if thing.approximate_member_count > 30:
						try:
							async with self.pool.acquire() as conn:
								temp=await conn.fetchval('''SELECT msgid FROM submissions WHERE serverid=$1''',guild_id)# this block only executes to indicate that the server is already submitted
								if temp:
									await ctx.author.send("This server has already been submitted earlier and is pending approval by the mod team.")
								else:
									raise Exception("Next Block")
						except Exception as e:
							say = "Sent by <@" + str(ctx.message.author.id) +">"
							channel = self.bot.get_channel(587466715407843328)
							final=await channel.send(reply.content+"""\n\n"""+say)
							await ctx.message.author.send(confirm) 
							async with self.pool.acquire() as conn:
								await conn.execute('''INSERT INTO submissions(msgid,message,userid,serverid) VALUES($1,$2,$3,$4)''',final.id,reply.content,reply.author.id,guild_id)
					else:
						await ctx.message.author.send("Your server does not have enough members to apply for submission , please re-read the #how-to-list channel carefully.")

				else:
					await ctx.message.author.send(invalid)
			except:
				await ctx.message.author.send(invalid)
	# @commands.command()
	# @commands.check(server_check)
	# @commands.has_role('Manager')
	# async def dbadd(self,ctx):#add column for server name and insertion on read by using the invite and invite.servername or something 
	# 	channel = self.bot.get_channel(587466715407843328)
	# 	regex = re.compile("https://(discord\.gg/[^\s]*)")
	# 	async for elem in channel.history(oldest_first=True):
	# 		try:
	# 			if elem.mentions == []:
	# 				var = regex.search(elem.content)
	# 				guild_invite = await self.bot.fetch_invite(var.group())
	# 				guild_id=guild_invite.guild.id
	# 				async with self.pool.acquire() as conn:
	# 					await conn.execute('''INSERT INTO submissions(msgid,message,serverid) VALUES($1,$2,$3)''',elem.id,elem.content,guild_id)
	# 					message_id = elem.id
	# 			else:
	# 				async with self.pool.acquire() as conn:
	# 					await conn.execute('''UPDATE submissions SET userid = $1,msg=$2 WHERE msgid =$3''',elem.mentions[0].id,elem.id,message_id)
	# 		except Exception as e:
	# 			raise(e)
	@commands.command()
	@commands.check(server_check)
	@commands.has_role('Manager')
	async def decline(self,ctx,msgid:int):
		channel = self.bot.get_channel(587466715407843328)
		processed_channel=self.bot.get_channel(457979407253110797)
		regex = re.compile("https://(discord\.gg/[^\s]*)")
		try:
			message = await channel.fetch_message(msgid)
			async with self.pool.acquire() as conn:
				invite = await conn.fetchval('''SELECT message FROM submissions WHERE msgid = $1''',msgid)
				ques = await ctx.message.author.send("""Are you sure you want to decline this invite ?(yes/no) \n ```"""+invite+ """```""")
				def check(message):
					return message.author.id == ctx.message.author.id and not message.guild 
				reply = await self.bot.wait_for('message',check=check)
				if reply.content.lower() == 'yes':
					await ctx.message.author.send("What is the reason for the rejection? (explain in one message)")
					reason = await self.bot.wait_for('message',check=check)
					recipient = await conn.fetchval('''SELECT userid FROM submissions WHERE msgid =$1''',msgid)
					var = regex.search(invite)
					try:
						guild_invite = await self.bot.fetch_invite(var.group())
						guild_name = str(guild_invite.guild)
						recipient_user= self.bot.get_user(recipient)
						await message.delete()
						try:
							msg2_id = await conn.fetchval('''SELECT msg FROM submissions WHERE msgid=$1''',msgid)
							# await ctx.message.author.send(msg2_id)
							msg2=await channel.fetch_message(msg2_id)
							await msg2.delete()
						except Exception as e:
							pass
						await conn.execute('''DELETE FROM submissions WHERE msgid=$1''',msgid)
						await processed_channel.send("DECLINED: "+guild_name+"""\nREASON: """+reason.content+"""\nDecision By: <@"""+str(ctx.message.author.id)+">"+"""\nSubmitted By: <@"""+str(recipient)+">")
						try:
							await recipient_user.send("""Your server submission to MSP for  """+guild_name+""" has been rejected with the following reason given:\n ``` """+reason.content+""" ```""")
							await ctx.message.author.send("The submission has been declined and deleted from the submissions channel.")
						except:
							await ctx.message.author.send("The submission has been deleted from the submissions channel but the submitter could not be notified , they are most likely not a member of MSP at the moment.")
					except:
						await ctx.message.author.send("the submission has an expired invitation , please use the !delete command to delete it as it can not be declined.")
		except discord.DiscordException as e:
			await ctx.author.send("that's an invalid message id.")


	@commands.command()
	@commands.check(server_check)
	@commands.has_role('Manager')
	async def delete(self,ctx,msgid:int):
		channel = self.bot.get_channel(587466715407843328)
		try:
			message = await channel.fetch_message(msgid)
			async with self.pool.acquire() as conn:
				invite = await conn.fetchval('''SELECT message FROM submissions WHERE msgid = $1''',msgid)
			if invite:
				ques = await ctx.message.author.send("""Are you sure you want to delete this invite ?(yes/no) This will not inform the submitter just delete from the submissions channel. \n ```"""+invite+ """```""")
				def check(message):
					return message.author.id == ctx.message.author.id and not message.guild 
				reply = await self.bot.wait_for('message',check=check)
				if reply.content.lower() == 'yes':
					async with self.pool.acquire() as conn:
						await message.delete()
						try:
							msg2_id = await conn.fetchval('''SELECT msg FROM submissions WHERE msgid=$1''',msgid)
							msg2=await channel.fetch_message(msg2_id)
							await msg2.delete()
						except:
							pass
						await conn.execute('''DELETE FROM submissions WHERE msgid=$1''',msgid)
						await ctx.message.author.send('The submission has been deleted.')
			else:
				await ctx.message.author.send("that's an invalid message id.")

		except:
			await ctx.message.author.send("that's an invalid message id.")

	@commands.command()
	@commands.check(server_check)
	@commands.has_role('Manager')
	async def accept(self,ctx,msgid:int):
		channel = self.bot.get_channel(587466715407843328)
		processed_channel=self.bot.get_channel(457979407253110797)
		regex = re.compile("https://(discord\.gg/[^\s]*)")
		try:
			message = await channel.fetch_message(msgid)
			async with self.pool.acquire() as conn:
				invite = await conn.fetchval('''SELECT message FROM submissions WHERE msgid=$1''',msgid)
				recipient = await conn.fetchval('''SELECT userid FROM submissions WHERE msgid=$1''',msgid)
				ques = await ctx.message.author.send('''Are you sure you want to accept this invite? (yes/no) This will not inform the submitter just list the server as accepted in #processed-servers \n ```'''+invite+'```')
				def check(message):
					return message.author.id == ctx.message.author.id and not message.guild
				reply = await self.bot.wait_for('message',check=check)
				var = regex.search(invite)
				if reply.content.lower() == 'yes':
					await message.delete()
					try:
						msg2_id = await conn.fetchval('''SELECT msg FROM submissions WHERE msgid=$1''',msgid)
						msg2=await channel.fetch_message(msg2_id)
						await msg2.delete()
					except:
						pass
					guild_invite = await self.bot.fetch_invite(var.group())
					guild_name = str(guild_invite.guild)
					await conn.execute('''DELETE FROM submissions WHERE msgid=$1''',msgid)
					await processed_channel.send("ACCEPTED: "+guild_name+"""\nDecision By: <@"""+str(ctx.message.author.id)+">"+"""\nSubmitted By: <@"""+str(recipient)+">")
					await ctx.message.author.send('The submission has been removed from #server-submissions and listed as accepted in #processed-servers.')

					
		except Exception as e:
			await ctx.message.author.send(e)

def setup(bot):
	bot.add_cog(submit(bot))