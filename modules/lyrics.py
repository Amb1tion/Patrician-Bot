import discord,json,random,operator,os
from discord.ext import commands
from discord.ext.commands import BucketType

class lyrics():
	def __init__(self,bot):
		self.bot=bot



	def leaderboard(self,num1,num2,num3,ctx):
		with open(os.path.join(os.getcwd(),'database','score_lyrics.json'),'r') as database:
			json_decoded=json.load(database)
			scores = sorted(json_decoded.items(),key = operator.itemgetter(1),reverse=True)
		array=[]
		i=num3
		for score in scores[num1:num2]:
			i+=1
			var = ctx.message.server.get_member(score[0])
			if var is not None:
				array.append('\n[' + str(i) +']:\t' + str(var)  + '\n\t\t\tTotal Score:\t\t\t' + str(score[1])+'\n')
			else:
				array.append('\n['+str(i)+']:\tUser Left Guild, Member #id:'+score[0]+'\n\t\t\tTotal Score:\t\t\t'+str(score[1])+'\n')
		test=''
		for score in array:
			test+=score
		return test,json_decoded
	
	@commands.group(pass_context=True)
	@commands.cooldown(rate=1, per=3, type=commands.BucketType.channel)
	async def lyrics(self,ctx):
		def check(message):
			return message.content.lower() == line[1].lower()
		if ctx.invoked_subcommand is None:
			with open(os.path.join(os.getcwd(),'database','lines.json'),'r') as database:
				json_decoded = json.load(database)
				line = random.choice(list(json_decoded.items()))
				await self.bot.say("```"+line[0]+"```" + '\n\n Guess the artist behind this gem .')
				answer = await self.bot.wait_for_message(timeout = 10.0,channel = ctx.message.channel, check=check)
				if answer is None:
					return await self.bot.say("You weren't quick enough , the answer is: " + line[1])
				
				else:
					await self.bot.say("You got it right, "+ answer.author.mention)
					with open(os.path.join(os.getcwd(),'database','score_lyrics.json'),'r') as database:#check if answer.author.id already in databse ; if already in database add 1 to their score
						json_decoded = json.load(database)
						if answer.author.id in json_decoded:
							json_decoded[answer.author.id]+=1
						else:
							json_decoded[answer.author.id]=1
						with open(os.path.join(os.getcwd(),'database','score_lyrics.json'),'w') as database:
							json.dump(json_decoded,database)
	
	
	
	@lyrics.command(pass_context=True)
	async def top(self,ctx,args=None):
		if args is None:
			var=self.leaderboard(0,10,0,ctx)
			await self.bot.say('```json\n------🏆👑THE TOP 10 PEOPLE VERSED IN BAD MUSIC👑🏆------'+var[0]+'\nᵉᵛᵉʳʸᵒᶰᵉᵒᶰᵗʰᶦˢᶫᶦˢᵗᶰᵉᵉᵈˢᵗᵒʳᵉᵉᵛᵃᶫᵘᵃᵗᵉᵗʰᵉᶦʳᶫᶦᶠᵉᵈᵉᶜᶦˢᶦᵒᶰˢ```')
		elif args == '2':
			var = self.leaderboard(10,19,10,ctx)
			await self.bot.say('```json\n------🏆👑#20-10 OF PEOPLE VERSED IN BAD MUSIC👑🏆------'+var[0]+'\nᵉᵛᵉʳʸᵒᶰᵉᵒᶰᵗʰᶦˢᶫᶦˢᵗᶰᵉᵉᵈˢᵗᵒʳᵉᵉᵛᵃᶫᵘᵃᵗᵉᵗʰᵉᶦʳᶫᶦᶠᵉᵈᵉᶜᶦˢᶦᵒᶰˢ```')
		elif '@' in ctx.message.content:
			var=self.leaderboard(0,10,0,ctx)
			if ctx.message.mentions[0].id in var[1]:
				await self.bot.say('```json\n'+ str(ctx.message.mentions[0]) + ' has no lifed a score of: ' + str(var[1][ctx.message.mentions[0].id]) +'```') 
				
				

	@commands.command(pass_context = True)
	async def add(self,ctx,*,args:str):
		test = "-"
		test2='"'
		if test in args and test2 in args:
			await self.bot.send_typing(ctx.message.channel)
			line,author = args.split('-')
			line = line.strip()
			author = author.strip()
			with open(os.path.join(os.getcwd(),'database','lines.json'),'r') as database:
				json_decoded = json.load(database)
			if line not in json_decoded.keys():
				json_decoded[line]=author
				print(len(json_decoded.keys()))
				with open(os.path.join(os.getcwd(),'database','lines.json'),'w') as something:
					json.dump(json_decoded,something)
				await self.bot.say("keep em comin bois it worked")
			else:
					await self.bot.say("line already in database.")
		else:
			await self.bot.say('Format your line as so `"your line here"-artist`')


def setup(bot):
	bot.add_cog(lyrics(bot))
