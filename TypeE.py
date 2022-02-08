import os
import discord
from discord.ext import commands

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='$', intents=intents)
TOKEN = os.getenv("DISCORD_TOKEN")


@bot.event
async def on_ready():
    print("Atom is ready.")

@bot.command(name='cc')
@commands.is_owner()
async def coupon_counter(ctx, start_num=0):
    await ctx.send(f"{start_num}")

bot.run(TOKEN)
