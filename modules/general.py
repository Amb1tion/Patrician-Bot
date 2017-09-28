import discord,os,json,re,random
from discord.ext import commands
from discord.ext.commands import BucketType
import discord.utils


def testing_check(ctx):
	return ctx.message.channel.id == '198702690191147009'


class general():
	def __init__(self,bot):
		self.bot=bot

	@commands.command(pass_context=True)
	@commands.cooldown(rate=2,per=15.0,type=commands.BucketType.channel)
	async def joindate(self,ctx,member=None):
		if member is not None:
			await self.bot.say("{0.name} joined in {0.joined_at}".format(ctx.message.mentions[0]))
		else:
			await self.bot.say("{0.name} joined in {0.joined_at}".format(ctx.message.author))

	@commands.command()
	@commands.cooldown(rate=2,per=10.0,type=commands.BucketType.channel)
	async def choose(self,*choices:str):
		print(choices)
		if len(choices) < 2:
			return await self.bot.say("weren't choices between *multiple* things ??")
		else:
			return await self.bot.say(random.choice(choices))
	
	@commands.command(pass_context=True)
	@commands.check(testing_check)
	async def ball(self,ctx,*,args=None):
		Regex=re.compile(r'.+\?$')
		mo=Regex.search(args)
		print(mo)
		if mo is not None:
			with open(os.path.join(os.getcwd(),'database','8ball.json'),'r') as database:
				json_decoded = json.load(database)
			await self.bot.say(random.choice(json_decoded))
		else:
			await self.bot.say('So do you plan on asking anything or what?')
	
	@commands.command(pass_context=True)
	@commands.has_any_role('admin','king crimson 👑','talking heads 🗣')
	async def ball_add(self,ctx,*,args:str):
		with open(os.path.join(os.getcwd(),'database','8ball.json'),'r') as database:
			json_decoded=json.load(database)
			json_decoded.append(args)
		with open(os.path.join(os.getcwd(),'database','8ball.json'),'w') as datbase:
			json.dump(json_decoded,database)
		await self.bot.say('You just added the following as a response `'+args+'`')

	@commands.command(pass_context=True)
	async def brave(self,ctx):
		role = discord.utils.get(ctx.message.server.roles,name='brave soul')
		if role not in ctx.message.author.roles:
			await self.bot.add_roles(ctx.message.author,role)
			await self.bot.say('I don\'t know why you\'d want to go to that hive of scum and villainy.... but take the role you masochist..')
		else:
			await self.bot.say('I ain\'t touching that role u keep it...')

	#@commands.command(pass_context=True)
	#@commands.check(spam_check)
	#async def hug(self,ctx,member:discord.Member):
	#	with open(os.path.join(os.getcwd(),'database','gifs'),'r') as database:
	#		json_decoded=json.load(database)
	#		print(json_decoded['hugs'])
	#		print(ctx.message.author.nick)
	#		print(member.name)
	#	await self.bot.say(random.choice(json_decoded['hugs'])+'\n*' +ctx.message.author.nick + ' hugs ' + str(member.name))

	#@commands.command(pass_context=True)
	#@commands.has_any_role('admin','king crimson 👑','talking heads 🗣')
	#async def hug_add(self,ctx,*,args:str):
	#	with open(os.path.join(os.getcwd(),'database','gifs'),'r') as database:
	#		json_decoded=json.load(database)
	#	json_decoded['hugs'].append(args)
	#	with open(os.path.join(os.getcwd(),'database','gifs'),'w') as database:
	#		json.dump(json_decoded,database)
	#	await self.bot.say('worked')

def setup(bot):
	bot.add_cog(general(bot))
