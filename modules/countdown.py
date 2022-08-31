import discord
from discord.ext import commands
import asyncio
def servercheck(ctx):
    return ctx.message.guild.id == 198621771451072512

class countdown(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def countdown(self, ctx:discord.ApplicationContext):
        await ctx.defer()
        secondint = 6
        title="Listening Party"
        while True:
            secondint = secondint - 1

            if secondint == 0:
                await ctx.send("```Start!```")
                break
            else:
                await ctx.send_followup("```css" + "\n" + "[" + title +"]" + "\nTimer: " + str(secondint) + "```",delete_after=2)
            await asyncio.sleep(1)
            # await interaction.message.delete(delay=2)

    # @commands.command()
    # @commands.check(servercheck)
    # async def lp(self,ctx):
    #     role = discord.utils.get(ctx.message.guild.roles,name='Listening Party')
    #     if role not in ctx.message.author.roles:
    #         await ctx.message.author.add_roles(role)
    #         await ctx.send("You've been given the Listening Party role and will be pinged when community LPs happen.")
    #     else:
    #         await ctx.message.author.remove_roles(role)
    #         await ctx.send("Role has been removed , you will no longer be pinged for community LPs.")

def setup(bot):
    bot.add_cog(countdown(bot))