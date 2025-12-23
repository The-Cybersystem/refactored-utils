import discord
from discord.ext import commands

class UtilityCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ping", description="Pong!")
    async def ping(self, ctx: commands.Context):
        """Pong!"""
        await ctx.send(f"Pong! In {round(self.bot.latency * 1000)}ms")

async def setup(bot):
    await bot.add_cog(UtilityCommands(bot))
