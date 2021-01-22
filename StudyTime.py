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

    # move verification pictures to the staff-only channel vp-pending
    if message.channel.id == 782844189456990298:
        if message.attachments != []:
            vpPending = discord.utils.get(message.guild.channels, id=782845929854205994)
            # sends the mention, content, and then the first picture they sent to #vp-pending
            image = await message.attachments[0].to_file()
            await vpPending.send(message.author.mention + ":\n" + message.content, file=image)

        await message.delete(delay=1)

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


async def find_user_vp(member: discord.Member, channel: discord.TextChannel):
    # find the last sent message from {member} in {channel} if one exists
    messages = await channel.history().flatten()  # get the messages in {channel} as :list:
    for message in messages:
        if str(member.mention) in message.content:
            return message
    return None


@bot.command(name='verify')
@commands.has_any_role('Mod', 'Admin')
async def verify_user(ctx, member: discord.Member, nickname):
    if member in ctx.guild.members:
        # get necessary roles and channels
        unverifiedRole = discord.utils.get(ctx.guild.roles, id=752977608060436509)
        memberRole = discord.utils.get(ctx.guild.roles, id=766382355568525376)
        vpPending = discord.utils.get(ctx.guild.channels, id=782845929854205994)
        vpArchive = discord.utils.get(ctx.guild.channels, id=770117019709341716)
        # find {member}'s verification picture in #vp-pending
        vp = await find_user_vp(member, vpPending)

        if vp is not None:
            # move {vp}'s content and image to #vp-archive
            image = await vp.attachments[0].to_file()
            await vpArchive.send(vp.content, file=image)
            await vp.delete(delay=1)

            # verifies {member} by removing Unverified, adding Member, and changing nick to {nickname}
            if unverifiedRole in member.roles:
                await member.add_roles(memberRole)
                await member.remove_roles(unverifiedRole)

            await member.edit(nick=nickname)
            await ctx.send(f'Successfully verified {member} with the nickname "{nickname}"')
        else:
            await ctx.send(f'Unable to verifiy {member}.')
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
