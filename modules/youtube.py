import discord, aiohttp, asyncio, async_timeout, configparser
from discord.ext import commands

config = configparser.ConfigParser()
config.read('bot_config.ini')
API_KEY = config['keys']['youtube_key']


class Youtube():
    def __init__(self, bot):
        self.bot = bot
        self.payload = {} #defining dict to use for paramater passing
        self.payload['key'] = API_KEY #passing api key as a param

    @commands.command(pass_context=True, description="Returns the first search result on youtube for your term",
                 alias='youtube')  #uses youtube api to get the first search result
    async def yt(self, context, *args: str):
        search = '+'.join(
            args)  # stores elements of the list obtained from user input using * modifier as a single string with words seperated by +
        payload = self.payload #passing further parameters
        payload['part']='snippet'
        payload['q']=search
        payload['maxResults']=2
        payload['type']='video'
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://www.googleapis.com/youtube/v3/search?",params=payload) as r:
                    data = await r.json()
                    link = "https://www.youtube.com/watch?v={}".format(data['items'][0]['id']['videoId'])
                    await self.bot.say(link)
        except:
            await self.bot.say("What kind of pleb stuff are you searching for ?")



def setup(bot):
    bot.add_cog(Youtube(bot))

