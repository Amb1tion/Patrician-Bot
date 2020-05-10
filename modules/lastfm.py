import discord,aiohttp,configparser,json
from discord.ext import commands
from discord.ext.commands import BucketType



config=configparser.ConfigParser()
config.read('bot_config.ini')


CLIENT_ID = config['client']['lastfm_id']

CLIENT_SECRET = config['client']['lastfm_secret']

API_KEY=config['keys']['lastfm_key']

API_SECRET=config['client']['lastfm_api_secret']



class lastfm(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        self.pool=bot.pool
        self.payload={}
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
            session.close()
            return data
        except Exception as e:
            raise Exception("Last.fm didn't respond , try again.")
    async def fetch(self,ctx,opt,args):
        async with self.pool.acquire() as conn:
            try:
                if opt is None:
                    user = await conn.fetchval('SELECT lastfm FROM users WHERE userid = $1', ctx.message.author.id)
                    msg = "That doesn't seem right , have you submitted your account ? (use `fm set username`)"
                elif opt == "set":
                    user = args
                    msg = "That doesn't look right , have you scrobbled anything yet ?"
                elif opt == "get":
                    user = args
                    msg = "That doesn't look like an account to me."
                try:
                    payload = self.payload
                    payload['method'] = 'user.getRecentTracks'
                    payload['username'] = user
                    payload['limit'] = 1
                    payload['nowplaying'] = 'true'
                    mess = await self.api_request(payload)
                    var = self.output(ctx, mess, user)
                    emo = await ctx.send(embed=var)
                    emojis = ['updoot:245233157916327937', 'downdoot:320678562308816898']
                # await self.bot.add_reaction(emo, emojis[0])
                # await self.bot.add_reaction(emo,emojis[1])
                except IndexError or KeyError:
                    payload = self.payload
                    payload['method'] = 'user.getRecentTracks'
                    payload['username'] = user
                    payload['limit'] = 2
                    payload['nowplaying'] = 'true'
                    mess = await self.api_request(payload)
                    var = self.output(ctx, mess, user)
                    emo = await ctx.send(content="",embed=var)
                    emojis = ['updoot:245233157916327937', 'downdoot:320678562308816898']
                    # await self.bot.add_reaction(emo, emojis[0])
                    # await self.bot.add_reaction(emo,emojis[1])
            except Exception as e:
                if isinstance(e,IndexError):
                    await ctx.send("There was a problem , either your account has not scrobbled anything yet or last.fm did not respond.")

    def output(self,ctx,mess,user):
        image1=mess['recenttracks']['track'][0]['image'][2]['#text']
        image2=mess['recenttracks']['track'][1]['image'][2]['#text']
        trackname1=mess['recenttracks']['track'][0]['name']
        albumname1=mess['recenttracks']['track'][0]['album']['#text']
        artist1=mess['recenttracks']['track'][0]['artist']['#text']
        temp=artist1+" "+albumname1+" "+ "album rym"
        term=temp.replace(" ","%20")
        albumlink="https://duckduckgo.com/?q=%5Csite%3Arateyourmusic.com+<"+term+">"
        hyperlink = "["+albumname1+"]"+"("+albumlink+")"
        if image1 is "":
            image1 = "https://i.imgur.com/ZneU91v.jpg"
        if image2 is "":
            image2="https://i.imgur.com/ZneU91v.jpg"
        embed = discord.Embed(title=artist1,
                              colour=discord.Colour(0xbe6cf8),
                              url=mess['recenttracks']['track'][0]['url'],
                              description=trackname1+" ["+ hyperlink+"]")

        embed.set_thumbnail(url=image1)
        embed.set_author(name=user
                         , url="https://www.last.fm/"+user,
                         icon_url=ctx.message.author.avatar_url)
        embed.set_footer(text="Previous: "+mess['recenttracks']['track'][1]['artist']['#text']+" - "+mess['recenttracks']['track'][1]['name'],
                          icon_url=image2)
        return embed

    @commands.group(description = "Shows your currently playing track.")
    async def fm(self,ctx):
        await ctx.message.channel.trigger_typing()
        if ctx.invoked_subcommand is None:
            await self.fetch(ctx,opt=None,args=None)

    @fm.command()
    async def set(self,ctx,args:str):
        await ctx.message.channel.trigger_typing()
        user=args
        await self.fetch(ctx,"set",user)
        async with self.pool.acquire() as conn:
            try:
                await conn.execute('''INSERT INTO users(userid,lastfm) VALUES($1,$2)''',ctx.message.author.id,user)
            except:
                await conn.execute('''UPDATE users SET lastfm = $1 WHERE userid = $2''',user,ctx.message.author.id)


    @fm.command()
    async def get(self,ctx,args):
        await ctx.message.channel.trigger_typing()
        try:
            if ctx.message.mentions[0].id:
                try:
                    async with self.pool.acquire() as conn:
                        user = await conn.fetchval('SELECT lastfm FROM users WHERE userid = $1', ctx.message.mentions[0].id)
                        if user is None:
                            raise Exception('no last.fm')
                    await self.fetch(ctx,"get",user)
                except:
                    await ctx.send('There\'s something wrong here , maybe they don\'t have a last.fm')
            else:
                raise Exception('No member mentioned.')
        except:
            user=args
            await self.fetch(ctx,"get",user)

def setup(bot):
    bot.add_cog(lastfm(bot))