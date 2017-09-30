import discord, asyncpg, json, asyncio, random, re
from discord.ext import commands
from discord.ext.commands import BucketType


class quotes():
    def __init__(self, bot):
        self.bot = bot
        self.pool = bot.pool

    @commands.group(pass_context=True, invoke_without_command=True)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.channel)
    async def quote(self, ctx, index=None):
        async with self.pool.acquire() as conn:
            try:
                chrysalis = await conn.fetchval('SELECT quotes FROM servers WHERE serverid = $1',
                                             int(ctx.message.server.id))
            except Exception as e:
                print(e)
            if chrysalis is None:
                err = await self.bot.say('This server hasn\'t added any quotes yet.')
                await asyncio.sleep(3)
                await self.bot.delete_message(ctx.message)
                await self.bot.delete_message(err)
            elif chrysalis is not None:
                #print(chrysalis)
                dict = json.loads(chrysalis)
                print(dict)
                if index in dict:
                    await self.bot.say('Here\'s your philosophical gem {}'.format(dict[index]))
                elif index not in dict and index is not None:
                    err = await self.bot.say('a Quote with that index is not in the database')
                    await asyncio.sleep(3)
                    await self.bot.delete_message(err)
                    await self.bot.delete_message(ctx.message)

                elif index is None:
                    print('is it here ?')
                    pick = random.choice(list(dict.keys()))
                    await self.bot.say('Here\'s one straight from the most brilliant minds this server has to offer: {}  \nvalue: {} '.format(dict[pick],pick))

    @quote.command(pass_context=True)
    @commands.cooldown(rate=1,per=10,type=commands.BucketType.channel)
    async def latest(self , ctx):
        async with self.pool.acquire() as conn:
            chrysalis = await conn.fetchval('SELECT quotes FROM servers WHERE serverid = $1',int(ctx.message.server.id))
            if chrysalis is None:
                err = await self.bot.say('This server hasn\'t stored any quotes yet.')
                await asyncio.sleep(5)
                await self.bot.delete_message(err)
                await self.bot.delete_message(ctx.message)
            else:
                dict = json.loads(chrysalis)
                print(dict)
                num = await conn.fetchval('SELECT quote_num FROM servers WHERE serverid = $1',int(ctx.message.server.id))
                await self.bot.say("Here's the latest of what the bright minds of this server have to offer: {} \nvalue: {}".format(dict[str(num-1)],str(num-1)))

    @quote.command(pass_context=True)
    @commands.cooldown(rate=1,per=5,type=commands.BucketType.channel)
    @commands.has_permissions(manage_messages=True)
    async def delete(self,ctx,index:int):
        def check(message):
            if message.content.lower() =='y':
                return True
            elif message.content.lower() =='n':
                return False
        async with self.pool.acquire() as conn:
            chrysalis = await conn.fetchval('SELECT quotes FROM servers WHERE serverid=$1',int(ctx.message.server.id))
            num = await conn.fetchval('SELECT quote_num FROM servers WHERE serverid=$1',int(ctx.message.server.id))
            if chrysalis is None:
                await self.bot.say('This server hasn\'t stored any quotes yet')
            else:
                try:
                    dict = json.loads(chrysalis)
                    if isinstance(index,int) and index in range(0 , num):
                        await self.bot.say("Are you sure you want to delete(y/n): {}".format(dict[str(index)]))
                        answer = await self.bot.wait_for_message(timeout=10.0, channel=ctx.message.channel, check=check)
                        if answer is None:
                            await self.bot.say('Operation timed out, make up your mind faster.')
                        else:
                            print('a')
                            dict.pop(str(index))
                            if index != num-1:
                                for id in range(index+1,num):
                                    dict[id-1]=dict[str(id)]
                                dict.pop(str(num-1))
                            await conn.execute('UPDATE servers SET quotes = $1 WHERE serverid = $2', json.dumps(dict),
                                               int(ctx.message.server.id))
                            await conn.execute('UPDATE servers SET quote_num=$1 WHERE serverid= $2', num-1,int(ctx.message.server.id))
                            await self.bot.say("Quote deleted.")
                    else:
                        await self.bot.say("Index invalid or out of range.")
                except Exception as e:
                    print(e)



    @quote.command(pass_context=True)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.channel)
    async def add(self, ctx, link: str):
        print('something')
        mo = re.compile(
            '^https://.*\.com/.*(\.jpg|\.png|\.jpeg)$|^http://.*\.com/(\.jpg|\.png|\.jpeg)$|.*\.com/.*(\.jpg|\.png|\.jpeg)$')
        try:
            var = mo.search(link)

            if var is not None:

                async with self.pool.acquire() as conn:
                    chrysalis = await conn.fetchval('SELECT quotes FROM servers WHERE serverid = $1',
                                                    int(ctx.message.server.id))

                    num = await conn.fetchval('SELECT quote_num FROM servers WHERE serverid=$1',
                                              int(ctx.message.server.id))
                    if chrysalis is None:
                        dict = {}
                    else:
                        dict = json.loads(chrysalis)
                    print(dict)
                    print('first')
                    if link not in dict.values():
                        print(num)
                        if num == 1:
                            val = 1
                            dict[val] = link
                            print('second')
                            print(dict)
                            await conn.execute('''UPDATE servers SET quote_num = $1 WHERE serverid = $2''', num + 1,
                                               int(ctx.message.server.id))
                        else:
                            val = num
                            dict[val] = link
                            await conn.execute('''UPDATE servers SET quote_num = $1 WHERE serverid = $2''', num + 1,
                                               int(ctx.message.server.id))
                        await conn.execute('UPDATE servers SET quotes = $1 WHERE serverid = $2', json.dumps(dict),
                                           int(ctx.message.server.id))
                        conf = await self.bot.say(
                            'Your meme...err i meant deep philosophical quote has been added with the assigned value of {} (which you can use to call it with `prefix quote value`)'.format(
                                str(val)))
                        await asyncio.sleep(3)
                        await self.bot.delete_message(conf)
                        await self.bot.delete_message(ctx.message)
                    else:
                        err = await self.bot.say('This link is already in the database you reposter.')
                        await asyncio.sleep(3)
                        await self.bot.delet_message(err)
                        await self.bot.delete_message(ctx.message)
            elif var is None:
                err = await self.bot.say('That\'s an invalid quote link')
                await asyncio.sleep(3)
                await self.bot.delete_message(err)
                await self.bot.delete_message(ctx.message)
        except Exception as e:
            print(e)
            err = await self.bot.say('You\'re supposed to give me an image link to your meme...err quote')
            await asyncio.sleep(3)
            await self.bot.delete_message(err)
            await self.bot.delete_message(ctx.message)
            # add delete quote functionality



def setup(bot):
    bot.add_cog(quotes(bot))
