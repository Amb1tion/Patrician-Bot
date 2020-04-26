import discord,aiohttp,configparser,json
from discord.ext import commands
from os import remove as f_remove
import functools
import numpy as np
import matplotlib
matplotlib.use("Agg") #because default is tkinter and that doesn't work well outside main thread
import matplotlib.pyplot as plt
from io import BytesIO
config=configparser.ConfigParser()
config.read('bot_config.ini')


CLIENT_ID = config['client']['lastfm_id']

CLIENT_SECRET = config['client']['lastfm_secret']

API_KEY=config['keys']['lastfm_key']

API_SECRET=config['client']['lastfm_api_secret']

class taste(commands.Cog):
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
        except Exception as E:
            raise Exception(E)
    async def fetch(self,ctx, opt, args): #for requesting top artists
        async with self.bot.pool.acquire() as conn:
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

                payload = self.payload
                payload['method'] = 'user.gettopartists'
                payload['username'] = user
                payload['limit'] = 100
                payload['period'] = 'overall'
                mess = await self.api_request(payload)
                return mess

            except Exception as E:
                await ctx.send(E)

    def op(self,artists, user1, user2, name1, name2): #graph generating function
        y = np.arange(len(artists))
        fig, axes = plt.subplots(ncols=2, sharey=True)
        axes[0].barh(y, user1, align='center', color='gray', height=0.3)
        axes[0].set(title=name1)
        axes[0].spines['top'].set_visible(False)
        axes[0].spines['right'].set_visible(False)
        axes[0].spines['bottom'].set_visible(False)
        axes[0].spines['left'].set_visible(False)
        axes[1].barh(y, user2, align='center', color='gray', height=0.3)
        axes[1].set(title=name2)
        axes[1].spines['top'].set_visible(False)
        axes[1].spines['right'].set_visible(False)
        axes[1].spines['bottom'].set_visible(False)
        axes[1].spines['left'].set_visible(False)

        axes[0].invert_xaxis()
        axes[0].set(yticks=y, yticklabels=artists)
        axes[0].yaxis.tick_right()

        for ax in axes.flat:
            ax.margins(0.03)
            ax.grid(False)
            ax.yaxis.set_label_position("right")
        fig.tight_layout()
        fig.subplots_adjust(wspace=0.66)
        plt.gca().invert_yaxis()
        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        return buf



    async def execute(self,artists, user1, user2, name1, name2): #making the blocking matplotlib function async
        thing = functools.partial(self.op, artists, user1, user2, name1, name2)
        some_stuff = await self.bot.loop.run_in_executor(None, thing)
        return some_stuff

    @commands.command()
    async def taste(self, ctx, args):
        await ctx.message.channel.trigger_typing()
        list1 = await self.fetch(ctx, opt=None, args=None)
        try:
            async with self.bot.pool.acquire() as conn:
                user_name1 = await conn.fetchval('SELECT lastfm FROM users WHERE userid = $1',
                                                 ctx.message.author.id)
        except:
            await ctx.send("Have you set your last.fm username ? (`!fm set username`)")
        try:
            if ctx.message.mentions[0].id:

                try:
                    async with self.bot.pool.acquire() as conn:
                        user_name2 = await conn.fetchval('SELECT lastfm FROM users WHERE userid = $1',
                                                         ctx.message.mentions[0].id)

                        if user_name2 is None:
                            raise Exception('no Last.fm')
                    list2 = await self.fetch(ctx, "get", user_name2)

                except Exception as e:
                    print(e)
                    await ctx.send('There\'s something wrong here , maybe they don\'t have a last.fm')
            else:
                raise Exception('No member mentioned.')
        except:
            user_name2 = args
            list2 = await self.fetch(ctx, "get", user_name2)
        result = {}
        for i in range(100): #comparing top 100 , weighting by ratio multiplied by sum of scrobbles on an artist
            artist_1 = list1['topartists']['artist'][i]
            for j in range(100):
                artist_2 = list2['topartists']['artist'][j]
                if artist_1['name'] == artist_2['name']:
                    a = int(artist_1['playcount'])
                    b = int(artist_2['playcount'])
                    result[artist_1['name']] = [a, b, a / b * (a + b) if a < b else b / a * (a + b)]
                    break
        if result is not None:
            final = sorted(result.items(), key=lambda foo: foo[1][2], reverse=True) #sorting by the weights
        else:
            ctx.send("You have no common artists with this user.")
            
        artists = []
        user1 = []
        user2 = []
        for i in range(0, 10):
            try:
                artists.append(final[i][0])
                user1.append(final[i][1][0])
                user2.append(final[i][1][1])
            except:
                break
        image =await self.execute(artists, user1, user2, user_name1, user_name2)
        await ctx.send(file=discord.File(fp=image,filename="{}.png".format(user_name1)))

def setup(bot):
	bot.add_cog(taste(bot))