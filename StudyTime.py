import os
import discord
from discord.ext import commands

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='$', intents=intents)
TOKEN = os.getenv("DISCORD_TOKEN")


@bot.event
async def on_ready():
    print("Atom is ready.")


async def give_remove_role(member: discord.Member, role: discord.Role):
    if role in member.roles:
        await member.remove_roles(role)
    elif role not in member.roles:
        await member.add_roles(role)


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    # do not process the bot's own messages
    if message.author == bot.user:
        return

    # assign major roles
    if message.channel.id == 781280160828751902:
        if message.content.isnumeric():
            roleNumber = int(message.content)
            roles = message.guild.roles

            # limit usage to roles in between "Agricultural Business Management" and "Textile Technology"
            lowerBound = roles.index(discord.utils.get(message.guild.roles, id=781388693322858546))
            upperBound = roles.index(discord.utils.get(message.guild.roles, id=781388300149587989))

            if upperBound >= upperBound - roleNumber >= lowerBound:
                # get role based on position index
                # starts from top role, Agricultural Business Management, and moves to bottom role, Textile Technology
                requestedRole = roles[upperBound-roleNumber]
                await give_remove_role(message.author, requestedRole)
                await message.channel.send(f'Changed {message.author.nick}\'s status for the role "{requestedRole}"',
                                           delete_after=3)
            else:
                await message.channel.send(f'Index "{roleNumber}" is out of range.', delete_after=3)

        await message.delete(delay=3)
    else:
        return


async def find_last_user_message(member: discord.Member, channel: discord.TextChannel):
    # find the last sent message from {member} in {channel} if one exists
    messages = await channel.history(limit=25).flatten()  # get the last 25 messages in {channel} as :list:
    for message in messages:
        if message.author is member:
            return message
    return None


@bot.command(name='verify')
@commands.has_any_role('Helper', 'Manager', 'Corporate', 'CEO')
async def verify_user(ctx, member: discord.Member, nickname):
    if member in ctx.guild.members:

        unverifiedRole = discord.utils.get(ctx.guild.roles, name='Unverified')
        memberRole = discord.utils.get(ctx.guild.roles, name='Member')

        if unverifiedRole in member.roles:
            # add Member role, remove Unverified role, change nickname to {nickname}
            await member.add_roles(memberRole)
            await member.remove_roles(unverifiedRole)
            await member.edit(nick=nickname)

            # get vP as :TextChannel:, find last sent message by {member} in vP
            verificationPictures = discord.utils.get(ctx.guild.channels, id=770117019709341716)
            lastMessage = await find_last_user_message(member, verificationPictures)

            # react to {lastMessage} with a thumbs up if it exists
            # otherwise, notify user that {lastMessage} does not exist
            if lastMessage is not None:
                await lastMessage.add_reaction('👍')
            else:
                await ctx.send(f'Unable to find a message to react to from {member} in {verificationPictures}')

            await ctx.send(f'Successfully verified {member} with the nickname "{nickname}"')
        else:
            await ctx.send(f'{member.display_name} is already verified.')
    else:
        await ctx.send(f'{member} does not exist or is not a member of {ctx.guild.name}.')


async def find_category(ctx, categoryName):
    # try to match {categoryName} to a category in {ctx.guild}
    for category in ctx.guild.categories:
        if categoryName.lower() == category.name.lower():
            return category
    return None


@bot.command(name='archive')
@commands.is_owner()
async def archive_text_category(ctx, categoryName, appendText):
    category = await find_category(ctx, categoryName)

    if category is not None:
        for channel in category.channels:
            # create new channel and sync its permissions to its {category}'s
            await ctx.guild.create_text_channel(name=channel.name, category=category, sync_permissions=True)

            # move to (archived) sC, rename, and sync permissions of original channel
            studyChannels = discord.utils.get(ctx.guild.categories, id=773996462262190090)
            await channel.edit(category=studyChannels, name=f'{appendText} - {channel.name}', sync_permissions=True)

        await ctx.send(f'Successfully archived the category "{category}"')
    else:
        await ctx.send(f'The category "{categoryName}" does not exist.')


bot.run(TOKEN)
