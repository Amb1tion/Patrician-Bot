import discord,os,json,re
from discord.ext import commands
from discord.ext.commands import BucketType




class rym():
	def __init__(self,bot):
		self.bot=bot
	
	
	@commands.group(pass_context=True)
	@commands.cooldown(rate=2,per=15.0,type=commands.BucketType.channel)
	async def rym(self,ctx):
		if ctx.invoked_subcommand is None:
			with open(os.path.join(os.getcwd(),'database','rym.json'),'r') as database:
				json_decoded=json.load(database)
			if ctx.message.author.id in json_decoded:
				Regex=re.compile(r"(.*)(#)(\d{4})")
				user = ctx.message.server.get_member(ctx.message.author.id)
				print(user)
				mo = Regex.search(str(user))
				print(mo)
				await self.bot.say(mo.group(1)+ "'s pleb tier rym account is: " + json_decoded[ctx.message.author.id])
			else:
				await self.bot.say("Your rym account is too entry level to be in the databse (fix this by `!rym set username` in #spamfiesta)")
 


	@rym.command(pass_context=True)
	async def set(self,ctx,args:str):
		Regex=re.compile('^([A-Za-z_.0-9]{3,24}$)')
		mo=Regex.search(args)
		if mo is not None:
			with open(os.path.join(os.getcwd(),'database','rym.json'),'r') as database:
				json_decoded=json.load(database)
				json_decoded[ctx.message.author.id]='https://rateyourmusic.com/~'+ mo.group(0)
				await self.bot.say('Your entry level account has been saved')
			with open(os.path.join(os.getcwd(),'database','rym.json'),'w') as database:
				json.dump(json_decoded,database)
		else:
			await self.bot.say('That account\'s so entry level it doesn\'t even exist yet!(invalid username).')
	
	@rym.command(pass_context=True)
	@commands.cooldown(rate=2,per=15,type=commands.BucketType.channel)
	async def get(self,ctx,args:discord.Member):
		with open(os.path.join(os.getcwd(),'database','rym.json'),'r') as database:
			json_decoded=json.load(database)
		if args.id in json_decoded:
			await self.bot.say('Here you go you stalker... ' + json_decoded[args.id])
		else:
			await self.bot.say("They're too entry level for a rym(make sure you're tagging a person)")

def setup(bot):
	bot.add_cog(rym(bot))
