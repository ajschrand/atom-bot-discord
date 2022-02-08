import discord
from discord.ext import commands
from discord.ui import Button, View

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='$', intents=intents)
TOKEN = os.getenv("DISCORD_TOKEN")


@bot.event
async def on_ready():
    print("Atom is ready.")


@bot.command(name='cc')
@commands.is_owner()
async def coupon_counter(ctx):
    increment_button = Button(label="++", style=discord.ButtonStyle.green)
    async def ib_callback(interaction):
        message = interaction.message.content
        await interaction.edit_original_message(content=f"{int(message) + 1}")

    increment_button.callback = ib_callback

    decrement_button = Button(label="--", style=discord.ButtonStyle.red)
    async def db_callback(interaction):
        message = interaction.message.content
        await interaction.edit_original_message(content=f"{int(message) - 1}")

    decrement_button.callback = db_callback

    view = View()
    view.add_item(increment_button)
    view.add_item(decrement_button)
    await ctx.send("0", view=view)

bot.run(TOKEN)
