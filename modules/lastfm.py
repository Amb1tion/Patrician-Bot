
import discord,configparser,aiohttp,urllib.parse,traceback
from discord.commands import SlashCommandGroup
from discord.ext import commands
from discord import option

config = configparser.ConfigParser()
config.read('bot_config.ini')

CLIENT_ID = config['client']['lastfm_id']

CLIENT_SECRET = config['client']['lastfm_secret']

API_KEY=config['keys']['lastfm_key']

API_SECRET=config['client']['lastfm_api_secret']


class lastfm(commands.Cog):
	def __init__(self,bot):
		self.bot = bot
		self.pool = bot.pool
		self.payload = {}
		self.payload['api_key']=API_KEY
		self.payload['format']='json'
	async def api_request(self, payload):
		try:
			url = 'http://ws.audioscrobbler.com/2.0/'
			headers = {'user-agent': 'Patrician-Bot/1.0'}
			conn = aiohttp.TCPConnector()
			session = aiohttp.ClientSession(connector=conn)
			async with session.get(url, params=payload, headers=headers) as r:
				data = await r.json()
			await session.close()
			return data
		except Exception as e:
			print(e)
	async def fetch(self,ctx,opt,args):
		async with self.pool.acquire() as conn:
			try:
				if opt is None:
					user = await conn.fetchval('SELECT lastfm FROM users WHERE userid = $1', ctx.author.id)
					msg = "That doesn't seem right , have you submitted your account ? (use `fm set username`)"
				elif opt == "set":
					user = args
					msg = "That doesn't look right , have you scrobbled anything yet ?"

				try:
					payload = self.payload
					payload['method'] = 'user.getRecentTracks'
					payload['username'] = user
					payload['limit'] = 1
					payload['nowplaying'] = 'true'
					mess = await self.api_request(payload)
					var = self.output(ctx, mess, user)
					emo = await ctx.send_followup(embed=var)
					emojis = ['updoot:245233157916327937', 'downdoot:320678562308816898']
					await emo.add_reaction(emojis[0])
					await emo.add_reaction(emojis[1])
				except IndexError or KeyError:
					payload = self.payload
					payload['method'] = 'user.getRecentTracks'
					payload['username'] = user
					payload['limit'] = 2
					payload['nowplaying'] = 'true'
					mess = await self.api_request(payload)
					var = self.output(ctx, mess, user)
					emo = await ctx.send_followup(content="",embed=var)
					emojis = ['updoot:245233157916327937', 'downdoot:320678562308816898']
					await emo.add_reaction(emojis[0])
					await emo.add_reaction(emojis[1])
			except Exception as e:
				if isinstance(e,IndexError):
					await ctx.send_followup("There was a problem , either your account has not scrobbled anything yet or last.fm did not respond.")
	def output(self,ctx,mess,user):
		image1=mess['recenttracks']['track'][0]['image'][2]['#text']
		image2=mess['recenttracks']['track'][1]['image'][2]['#text']
		trackname1=mess['recenttracks']['track'][0]['name']
		albumname1=mess['recenttracks']['track'][0]['album']['#text']
		artist1=mess['recenttracks']['track'][0]['artist']['#text']
		temp=artist1+" "+albumname1+" "+ "album rym"
		term=urllib.parse.quote(temp)
		albumlink="https://duckduckgo.com/?q=%5Csite%3Arateyourmusic.com+<"+term+">"
		hyperlink = "["+albumname1+"]"+"("+albumlink+")"
		if image1 == "":
			image1 = "https://i.imgur.com/ZneU91v.jpg"
		if image2 == "":
			image2="https://i.imgur.com/ZneU91v.jpg"
		embed = discord.Embed(title=artist1,
								colour=discord.Colour(0xbe6cf8),
								url=mess['recenttracks']['track'][0]['url'],
								description=trackname1+" ["+ hyperlink+"]")

		embed.set_thumbnail(url=image1)
		embed.set_author(name=user
							, url="https://www.last.fm/user/"+user,
							icon_url=ctx.author.display_avatar)
		embed.set_footer(text="Previous: "+mess['recenttracks']['track'][1]['artist']['#text']+" - "+mess['recenttracks']['track'][1]['name'],
							icon_url=image2)
		return embed

	# fm = SlashCommandGroup("fm","Various last.fm commands")
	@commands.slash_command(name="fm",description="Shows your currently playing or last played last.fm scrobble",guild_ids=[205630530237104128])
	@option("username",description="Set your username via this field",default=None)
	async def now_playing(self,ctx:discord.ApplicationContext,username:str):
	# username: discord.Option(str,name="username",description="Set your username via this field",default=None,required=False)):
		await ctx.defer()
		# if username is not None:
		# 	option = "set"
		# else:
		# 	option = None

		async with self.pool.acquire() as conn:
			try:
				if username == None:
					user = await conn.fetchval('SELECT lastfm FROM users WHERE userid = $1', ctx.author.id)
					msg = "That doesn't seem right , have you submitted your account ? (use `fm set username`)"
				else :
					user=username
					try:
						await conn.execute('''INSERT INTO users(userid,lastfm) VALUES($1,$2)''',ctx.author.id,username)
					except:
						await conn.execute('''UPDATE users SET lastfm = $1 WHERE userid = $2''',user,ctx.author.id)
					
				try:
					payload = self.payload
					payload['method'] = 'user.getRecentTracks'
					payload['username'] = user
					payload['limit'] = 1
					payload['nowplaying'] = 'true'
					mess = await self.api_request(payload)
					var = self.output(ctx, mess, user)
					emo = await ctx.send_followup(embed=var)
					emojis = ['updoot:245233157916327937', 'downdoot:320678562308816898']
					await emo.add_reaction(emojis[0])
					await emo.add_reaction(emojis[1])
				except IndexError or KeyError:
					payload = self.payload
					payload['method'] = 'user.getRecentTracks'
					payload['username'] = user
					payload['limit'] = 2
					payload['nowplaying'] = 'true'
					mess = await self.api_request(payload)
					var = self.output(ctx, mess, user)
					emo = await ctx.send_followup(content="",embed=var)
					emojis = ['updoot:245233157916327937', 'downdoot:320678562308816898']
					await emo.add_reaction(emojis[0])
					await emo.add_reaction(emojis[1])
			except Exception as e:
				traceback.print_exception(e)
				if isinstance(e,IndexError):
					await ctx.send_followup("There was a problem , either your account is wrong/has not scrobbled anything yet or last.fm did not respond.")
		# await self.fetch(ctx,opt=None,args=None)
		# await ctx.respond("test")

def setup(bot):
	bot.add_cog(lastfm(bot))



