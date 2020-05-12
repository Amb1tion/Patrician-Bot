import discord, asyncpg, json, asyncio, random, re
from discord.ext import commands
from discord.ext.commands import BucketType

async def output(self,ctx,msg,num,stuff):
        await msg.add_reaction("\u27A1" )#right emoji
        await msg.add_reaction("\u2B05" )#left emoji
        ptr=num-1
        def check(reaction,user):
            return user.id == ctx.message.author.id and (str(reaction.emoji) == '\u2B05' or str(reaction.emoji)=='\u27A1') and reaction.message.id == msg.id
        while True:
            try:
                reaction,user = await self.bot.wait_for("reaction_add",timeout=60,check = check)
                if str(reaction.emoji) == "\u27A1" :
                    ptr=ptr-1
                    try:
                        out='Here\'s one straight from the most brilliant minds this server has to offer: {}  \nvalue: {} '.format(stuff[str(ptr)],str(ptr))
                        await msg.edit(content=out)
                        await reaction.remove(user)
                    except:
                        ptr=ptr+1
                        out='that\'s as far as it goes on this end , try the other arrow: {}  \nvalue: {} '.format(stuff[str(ptr)],str(ptr))
                        await msg.edit(content=out)
                        await reaction.remove(user)
                elif str(reaction.emoji) == '\u2B05':
                    ptr=ptr+1
                    try:
                        out='Here\'s one straight from the most brilliant minds this server has to offer:  {}  \nvalue: {} '.format(stuff[str(ptr)],str(ptr))
                        await msg.edit(content=out)
                        await reaction.remove(user)
                    except:
                        ptr=ptr-1
                        out='that\'s as far as it goes on this end , try the other arrow: {}  \nvalue: {} '.format(stuff[str(ptr)],str(ptr))
                        await msg.edit(content=out)
                        await reaction.remove(user)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                break


class quotes(commands.Cog):
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
                err = await ctx.send('This server hasn\'t added any quotes yet.')
                await asyncio.sleep(3)
                await ctx.message.delete()
                await err.delete()
            elif chrysalis is not None:
                #print(chrysalis)
                stuff = json.loads(chrysalis)
                print(stuff)
                if index in stuff:
                    num= int(index)-1
                    msg=await ctx.send('Here\'s your philosophical gem {}'.format(stuff[index]))
                    await output(self,ctx,msg,num,stuff)
                elif index not in stuff and index is not None:
                    err = await ctx.send('a Quote with that index is not in the database')
                    await asyncio.sleep(3)
                    await err.delete()
                    await ctx.message.delete()

                elif index is None:
                    print('is it here ?')
                    pick = random.choice(list(stuff.keys()))
                    num= int(pick)+1
                    msg=await ctx.send('Here\'s one straight from the most brilliant minds this server has to offer: {}  \nvalue: {} '.format(stuff[pick],pick))
                    await output(self,ctx,msg,num,stuff)

    @quote.command()
    async def latest(self , ctx):
        async with self.pool.acquire() as conn:
            chrysalis = await conn.fetchval('SELECT quotes FROM servers WHERE serverid = $1',ctx.message.guild.id)
            if chrysalis is None:
                err = await ctx.send('This server hasn\'t stored any quotes yet.')
                await asyncio.sleep(5)
                await err.delete()
                await ctx.message.delete()
            else:
                stuff = json.loads(chrysalis)
                print(stuff)
                num = await conn.fetchval('SELECT quote_num FROM servers WHERE serverid = $1',ctx.message.guild.id)
                msg =await ctx.send("Here's the latest of what the bright minds of this server have to offer: {} \nvalue: {}".format(stuff[str(num-1)],str(num-1)))
                await output(self,ctx,msg,num,stuff)

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
                await ctx.send('This server hasn\'t stored any quotes yet')
            else:
                try:
                    stuff = json.loads(chrysalis)
                    if isinstance(index,int) and index in range(0 , num):
                        await ctx.send("Are you sure you want to delete(y/n): {}".format(stuff[str(index)]))
                        answer = await self.bot.wait_for('message',timeout=10.0, check=check)
                        if answer is None:
                            await ctx.send('Operation timed out, make up your mind faster.')
                        else:
                            print('a')
                            stuff.pop(str(index))
                            if index != num-1:
                                for id in range(index+1,num):
                                    stuff[id-1]=stuff[str(id)]
                                stuff.pop(str(num-1))
                            await conn.execute('UPDATE servers SET quotes = $1 WHERE serverid = $2', json.dumps(stuff),
                                               ctx.message.guild.id)
                            await conn.execute('UPDATE servers SET quote_num=$1 WHERE serverid= $2', num-1,ctx.message.guild.id)
                            await ctx.send("Quote deleted.")
                    else:
                        await ctx.send("Index invalid or out of range.")
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
                        stuff = {}
                    else:
                        stuff = json.loads(chrysalis)
                    print(stuff)
                    print('first')
                    if link not in stuff.values():
                        print(num)
                        if num == 1:
                            val = 1
                            stuff[val] = link
                            print('second')
                            print(stuff)
                            await conn.execute('''UPDATE servers SET quote_num = $1 WHERE serverid = $2''', num + 1,
                                               ctx.message.guild.id)
                        else:
                            val = num
                            stuff[val] = link
                            await conn.execute('''UPDATE servers SET quote_num = $1 WHERE serverid = $2''', num + 1,
                                               ctx.message.guild.id)
                        await conn.execute('UPDATE servers SET quotes = $1 WHERE serverid = $2', json.dumps(stuff),
                                           ctx.message.guild.id)
                        conf = await ctx.send(
                            'Your meme...err i meant deep philosophical quote has been added with the assigned value of {} (which you can use to call it with `prefix quote value`)'.format(
                                str(val)))
                    else:
                        err = await ctx.send('This link is already in the database you reposter.')
            elif var is None:
                err = await ctx.messge.channel.send('That\'s an invalid quote link')

        except Exception as e:
            print(e)
            err = await ctx.send('You\'re supposed to give me an image link to your meme...err quote')




def setup(bot):
    bot.add_cog(quotes(bot))
