import discord
from discord.ext import commands
import asyncio
def servercheck(ctx):
    return ctx.message.server.id == "198621771451072512"

class countdown():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context = True)
    async def countdown(self, ctx):
        secondint = 10
        title="Listening Party"
        message = await self.bot.say("```css" + "\n" + "[" + title +"]" + "\nTimer: " + str(secondint) + "```")
        while True:
            secondint = secondint - 1
            if secondint == 0:
                await self.bot.edit_message(message, new_content=("```Ended!```"))
                break
            await self.bot.edit_message(message, new_content=("```css" + "\n" + "[" + title + "]" + "\nTimer: {0}```".format(secondint)))
            await asyncio.sleep(1)
    @commands.command(pass_context=True)
    @commands.check(servercheck)
    async def lp(self,ctx):
        role = discord.utils.get(ctx.message.server.roles,name='Listening Party')
        if role not in ctx.message.author.roles:
            await self.bot.add_roles(ctx.message.author,role)
            await self.bot.say("You've been given the Listening Party role and will be pinged when community LPs happen.")
        else:
            await self.bot.remove_roles(ctx.message.author,role)
            await self.bot.say("Role has been removed , you will no longer be pinged for community LPs.")

def setup(bot):
    bot.add_cog(countdown(bot))