import discord, asyncpg, json, asyncio, random, re
from discord.ext import commands
from discord.ext.commands import BucketType


class quotesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pool = bot.pool

    @commands.group(invoke_without_command=True)
    async def quote(self, ctx, index=None):
        async with self.pool.acquire() as conn:
            try:
                chrysalis = await conn.fetchval('SELECT quotes FROM servers WHERE serverid = $1',
                                             ctx.message.guild.id)
            except Exception as e:
                print(e)
            if chrysalis is None:
                err = await ctx.message.channel.send('This server hasn\'t added any quotes yet.')
                await asyncio.sleep(3)
                await ctx.message.delete()
                await err.delete()
            elif chrysalis is not None:
                #print(chrysalis)
                dict = json.loads(chrysalis)
                print(dict)
                if index in dict:
                    await ctx.message.channel.send('Here\'s your philosophical gem {}'.format(dict[index]))
                elif index not in dict and index is not None:
                    err = await ctx.message.channel.send('a Quote with that index is not in the database')
                    await asyncio.sleep(3)
                    await err.delete()
                    await ctx.message.delete()

                elif index is None:
                    print('is it here ?')
                    pick = random.choice(list(dict.keys()))
                    await ctx.message.channel.send('Here\'s one straight from the most brilliant minds this server has to offer: {}  \nvalue: {} '.format(dict[pick],pick))

    @quote.command()
    async def latest(self , ctx):
        async with self.pool.acquire() as conn:
            chrysalis = await conn.fetchval('SELECT quotes FROM servers WHERE serverid = $1',ctx.message.guild.id)
            if chrysalis is None:
                err = await ctx.message.channel.send('This server hasn\'t stored any quotes yet.')
                await asyncio.sleep(5)
                await err.delete()
                await ctx.message.delete()
            else:
                dict = json.loads(chrysalis)
                print(dict)
                num = await conn.fetchval('SELECT quote_num FROM servers WHERE serverid = $1',ctx.message.guild.id)
                await ctx.message.channel.send("Here's the latest of what the bright minds of this server have to offer: {} \nvalue: {}".format(dict[str(num-1)],str(num-1)))

    @quote.command()
    @commands.has_permissions(manage_messages=True)
    async def delete(self,ctx,index:int):
        def check(message):
            if message.content.lower() =='y' and message.channel==ctx.message.channel:
                return True
            elif message.content.lower() =='n'and message.channel==ctx.message.channel:
                return False
        async with self.pool.acquire() as conn:
            chrysalis = await conn.fetchval('SELECT quotes FROM servers WHERE serverid=$1',ctx.message.guild.id)
            num = await conn.fetchval('SELECT quote_num FROM servers WHERE serverid=$1',ctx.message.guild.id)
            if chrysalis is None:
                await ctx.message.channel.send('This server hasn\'t stored any quotes yet')
            else:
                try:
                    dict = json.loads(chrysalis)
                    if isinstance(index,int) and index in range(0 , num):
                        await ctx.message.channel.send("Are you sure you want to delete(y/n): {}".format(dict[str(index)]))
                        answer = await self.bot.wait_for('message',timeout=10.0, check=check)
                        if answer is None:
                            await ctx.message.channel.send('Operation timed out, make up your mind faster.')
                        else:
                            print('a')
                            dict.pop(str(index))
                            if index != num-1:
                                for id in range(index+1,num):
                                    dict[id-1]=dict[str(id)]
                                dict.pop(str(num-1))
                            await conn.execute('UPDATE servers SET quotes = $1 WHERE serverid = $2', json.dumps(dict),
                                               ctx.message.guild.id)
                            await conn.execute('UPDATE servers SET quote_num=$1 WHERE serverid= $2', num-1,ctx.message.guild.id)
                            await ctx.message.channel.send("Quote deleted.")
                    else:
                        await ctx.message.channel.send("Index invalid or out of range.")
                except Exception as e:
                    print(e)



    @quote.command()
    async def add(self, ctx, link: str):
        print('something')
        mo = re.compile(
            '^https://.*\.(com|net)/.*(\.jpg|\.png|\.jpeg)$|^http://.*\.(com|net)/(\.jpg|\.png|\.jpeg)$|.*\.(com|net)/.*(\.jpg|\.png|\.jpeg)$')
        try:
            var = mo.search(link)

            if var is not None:

                async with self.pool.acquire() as conn:
                    chrysalis = await conn.fetchval('SELECT quotes FROM servers WHERE serverid = $1',
                                                    ctx.message.guild.id)

                    num = await conn.fetchval('SELECT quote_num FROM servers WHERE serverid=$1',
                                              ctx.message.guild.id)
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
                                               ctx.message.guild.id)
                        else:
                            val = num
                            dict[val] = link
                            await conn.execute('''UPDATE servers SET quote_num = $1 WHERE serverid = $2''', num + 1,
                                               ctx.message.guild.id)
                        await conn.execute('UPDATE servers SET quotes = $1 WHERE serverid = $2', json.dumps(dict),
                                           ctx.message.guild.id)
                        conf = await ctx.message.channel.send(
                            'Your meme...err i meant deep philosophical quote has been added with the assigned value of {} (which you can use to call it with `prefix quote value`)'.format(
                                str(val)))
                    else:
                        err = await ctx.message.channel.send('This link is already in the database you reposter.')
            elif var is None:
                err = await ctx.messge.channel.send('That\'s an invalid quote link')

        except Exception as e:
            print(e)
            err = await ctx.message.channel.send('You\'re supposed to give me an image link to your meme...err quote')




def setup(bot):
    bot.add_cog(quotesCog(bot))
