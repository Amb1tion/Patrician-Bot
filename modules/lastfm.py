import discord,aiohttp,asyncio,async_timeout,json,os,configparser,re
from discord.ext import commands
from discord.ext.commands import BucketType



config=configparser.ConfigParser()
config.read('bot_config.ini')


CLIENT_ID = config['client']['lastfm_id']

CLIENT_SECRET = config['client']['lastfm_secret']

API_KEY=config['keys']['lastfm_key']

API_SECRET=config['client']['lastfm_api_secret']

username = 'amb1tion'

class lastfm():
	def __init__(self,bot):
		self.bot=bot
		self.pool=bot.pool
		self.payload={}
		self.payload['api_key']=API_KEY
		self.payload['format']='json'
	async def api_request(self, payload):
		url = 'http://ws.audioscrobbler.com/2.0/'
		headers = {'user-agent': 'Patrician-Bot/1.0'}
		conn = aiohttp.TCPConnector()
		session = aiohttp.ClientSession(connector=conn)
		async with session.get(url, params=payload, headers=headers) as r:
			data = await r.json()
		session.close()
		return data
	
	def output(self,ctx,mess,user,not_author=None):
		check=['remastered','edition','mono','stereo','deluxe','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014','2015','2016']
		if any(test in mess['recenttracks']['track'][0]['album']['#text'].lower() for test in check) or any(test in mess['recenttracks']['track'][1]['name'].lower() for test in check) or any(test in mess['recenttracks']['track'][0]['name'].lower() for test in check) or any(test in mess['recenttracks']['track'][1]['album']['#text'].lower() for test in check):
			Regex=re.compile(r"(.*)(#)(\d{4})")
			if not_author and ctx.message.mentions[0].id:
					mo=Regex.search(str(ctx.message.mentions[0]))
					say="**Current**: "+ mess['recenttracks']['track'][0]['artist']['#text']+' - '+mess['recenttracks']['track'][0]['name']+ ' [' + mess['recenttracks']['track'][0]['album']['#text'] + ']'+'\n**Previous**: '+mess['recenttracks']['track'][1]['artist']['#text'] +' - '+mess['recenttracks']['track'][1]['name'] + ' [' + mess['recenttracks']['track'][1]['album']['#text'] + ']'+'\n<https://www.last.fm/user/'+user+'>'+'\n*fix your god damn tags '+mo.group(1)+ '*'
			elif not_author and not ctx.message.author.mentions[0].id:
				mo=Regex.search(str(ctx.message.author))
				say="**Current**: "+ mess['recenttracks']['track'][0]['artist']['#text']+' - '+mess['recenttracks']['track'][0]['name']+ ' [' + mess['recenttracks']['track'][0]['album']['#text'] + ']'+'\n**Previous**: '+mess['recenttracks']['track'][1]['artist']['#text'] +' - '+mess['recenttracks']['track'][1]['name'] + ' [' + mess['recenttracks']['track'][1]['album']['#text'] + ']'+'\n<https://www.last.fm/user/'+user+'>'+'\n*fix your god damn tags '+mo.group(1)+'*'
			else:
				mo=Regex.search(str(ctx.message.author))
				say="**Current**: "+ mess['recenttracks']['track'][0]['artist']['#text']+' - '+mess['recenttracks']['track'][0]['name']+ ' [' + mess['recenttracks']['track'][0]['album']['#text'] + ']'+'\n**Previous**: '+mess['recenttracks']['track'][1]['artist']['#text'] +' - '+mess['recenttracks']['track'][1]['name'] + ' [' + mess['recenttracks']['track'][1]['album']['#text'] + ']'+'\n<https://www.last.fm/user/'+user+'>'+'\n*fix your god damn tags '+mo.group(1)+'*'
			return say
		else:
			say="**Current**: "+ mess['recenttracks']['track'][0]['artist']['#text']+' - '+mess['recenttracks']['track'][0]['name']+ ' [' + mess['recenttracks']['track'][0]['album']['#text'] + ']'+'\n**Previous**: '+mess['recenttracks']['track'][1]['artist']['#text'] +' - '+mess['recenttracks']['track'][1]['name'] + ' [' + mess['recenttracks']['track'][1]['album']['#text'] + ']'+'\n<https://www.last.fm/user/'+user+'>'
			return say
	
	@commands.group(pass_context=True , description = "Shows your currently playing track.")
	async def fm(self,ctx):
		await self.bot.send_typing(ctx.message.channel)
		if ctx.invoked_subcommand is None: #check if username is present in .json and output songs for it
			async with self.pool.acquire() as conn:
				try:
					user = await conn.fetchval('SELECT lastfm FROM users WHERE userid = $1',int(ctx.message.author.id))
					try:
						payload=self.payload
						payload['method']='user.getRecentTracks'
						payload['username']= user
						payload['limit']=1
						payload['nowplaying']='true'
						mess =await self.api_request(payload)
						var=self.output(ctx,mess,user)
						emo=await self.bot.say(var)
						emojis=['updoot:245233157916327937' , 'downdoot:320678562308816898']
						#await self.bot.add_reaction(emo, emojis[0])
						#await self.bot.add_reaction(emo,emojis[1])
					except IndexError or KeyError:
						payload=self.payload
						payload['method']='user.getRecentTracks'
						payload['username']= user
						payload['limit']=2
						payload['nowplaying']='true'
						mess = await self.api_request(payload)
						var = self.output(ctx,mess,user)
						emo=await self.bot.say(var)
						emojis=['updoot:245233157916327937' , 'downdoot:320678562308816898']
						#await self.bot.add_reaction(emo, emojis[0])
						#await self.bot.add_reaction(emo,emojis[1])
				except:
					await self.bot.say('Something went wrong , maybe you\'re too pleb for a last.fm(fix this by doing `prefix fm set usernamehere` ')
	@fm.command(pass_context=True)
	async def set(self,ctx,args:str):
		await self.bot.send_typing(ctx.message.channel)
		user=args
		try:
			try:
				payload=self.payload
				payload['method']='user.getRecentTracks'
				payload['username']= user
				payload['limit']=1
				payload['nowplaying']='true'
				mess =await self.api_request(payload)
				var=self.output(ctx,mess,user)
				emo=await self.bot.say(var)
				emojis=['updoot:245233157916327937' , 'downdoot:320678562308816898']
				#await self.bot.add_reaction(emo, emojis[0])
				#await self.bot.add_reaction(emo,emojis[1])
			except:
				payload=self.payload
				payload['method']='user.getRecentTracks'
				payload['username']= user
				payload['limit']=2
				payload['nowplaying']='true'
				mess = await self.api_request(payload)
				var = self.output(ctx,mess,user)
				emo=await self.bot.say(var)
				emojis=['updoot:245233157916327937' , 'downdoot:320678562308816898']
				#await self.bot.add_reaction(emo, emojis[0])
				#await self.bot.add_reaction(emo,emojis[1])
			async with self.pool.acquire() as conn:
				try:
					await conn.execute('''INSERT INTO users(userid,lastfm) VALUES($1,$2)''',int(ctx.message.author.id),user)
				except:
					await conn.execute('''UPDATE users SET lastfm = $1 WHERE userid = $2''',user,int(ctx.message.author.id))
		except Exception as e:
			print(e)
			await self.bot.say('That\'s a pleb username, see if it\'s typed right or if you\'ve scrobbled anything yet if it\'s new.')
	
	@fm.command(pass_context=True)
	async def get(self,ctx,args):
		await self.bot.send_typing(ctx.message.channel)
		try:
			not_author=True
			if ctx.message.mentions[0].id:
				try:
					async with self.pool.acquire() as conn:
						user = await conn.fetchval('SELECT lastfm FROM users WHERE userid = $1', int(ctx.message.mentions[0].id))
				except:
					await self.bot.say('Something went wrong , they\'re probably too pleb for a last.fm')
				try:
					payload=self.payload
					payload['method']='user.getRecentTracks'
					payload['username']= user
					payload['limit']=1
					payload['nowplaying']='true'
					mess =await self.api_request(payload)
					var=self.output(ctx,mess,user,not_author)
					emo=await self.bot.say(var)
					emojis=['updoot:245233157916327937' , 'downdoot:320678562308816898']
					#await self.bot.add_reaction(emo, emojis[0])
					#await self.bot.add_reaction(emo,emojis[1])
				except:
					payload=self.payload
					payload['method']='user.getRecentTracks'
					payload['username']= user
					payload['limit']=2
					payload['nowplaying']='true'
					mess = await self.api_request(payload)
					var=self.output(ctx,mess,user,not_author)
					emo=await self.bot.say(var)
					emojis=['updoot:245233157916327937' , 'downdoot:320678562308816898']
						#await self.bot.add_reaction(emo, emojis[0])
						#await self.bot.add_reaction(emo,emojis[1])
			else:
				raise Exception('No member mentioned.')
			#else:
			#	await self.bot.say('They\'re too pleb for a last.fm')
		except:
			user=args
			try:
				try:
					payload=self.payload
					payload['method']='user.getRecentTracks'
					payload['username']= user
					payload['limit']=1
					payload['nowplaying']='true'
					mess =await self.api_request(payload)
					var=self.output(ctx,mess,user,not_author)
					emo=await self.bot.say(var)
					emojis=['updoot:245233157916327937' , 'downdoot:320678562308816898']
					#await self.bot.add_reaction(emo, emojis[0])
					#await self.bot.add_reaction(emo,emojis[1])
				except Exception as e:
					payload=self.payload
					payload['method']='user.getRecentTracks'
					payload['username']= user
					payload['limit']=2
					payload['nowplaying']='true'
					mess = await self.api_request(payload)
					var=self.output(ctx,mess,user,not_author)
					emo=await self.bot.say(var)
					emojis=['updoot:245233157916327937' , 'downdoot:320678562308816898']
					#await self.bot.add_reaction(emo, emojis[0])
					#await self.bot.add_reaction(emo,emojis[1])
			except Exception as e:
				print(e)
				await self.bot.say('That\'s a pleb username')



#	async def on_message(self,message):
#			if message.content.startswith('.fm'):
#				await self.bot.send_message(message.channel,'I know you\'re a pleb but that don\'t mean you shouldn\'t !fm')

def setup(bot):
	bot.add_cog(lastfm(bot))
