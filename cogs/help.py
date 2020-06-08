# Lib

# Site
from discord.ext import commands
from discord.ext.commands.cog import Cog

# Local
from utils.classes import Bot

class Misc_Commands(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.bot_has_permissions(send_messages=True, manage_channels=True, manage_messages=True)
    async def invite(self, ctx):
        await ctx.send("Here: https://discord.com/oauth2/authorize?client_id=698965636432265227&permissions=268479504&scope=bot")

     
    @commands.command(name="help")
    @commands.bot_has_permissions(send_messages=True)
    async def bhelp(self, ctx, section="directory", subsection=None):
        BOT_PREFIX = self.bot.command_prefix
        if section.lower() == "directory":
            await ctx.send(f"""
New? Try these commands in your server:
```
{BOT_PREFIX}setup
{BOT_PREFIX}new_channel "root" "Front Yard"
{BOT_PREFIX}new_category "root" "Big House"
{BOT_PREFIX}new_channel "root//Big House" "Livingroom"
```
Required Permissions:
```
"Manage Roles"    - To set the directory channel so that only the server owner may use it until further permissions are set.
"Manage Channels" - To create new channels.
"Manage Messages" - To manage the directory channel so that it's kept clean.
"Read Messages"   - To read commands.
"Send Messages"   - To send notifications/messages for warnings, confirmations, etc.
"Attach Files"    - To send the requested file from the command {BOT_PREFIX}save_directory.
```
To see important announcements and command changes, Type and enter `{BOT_PREFIX}help updates`
Use this if you think a command isn't working the same way it did last time you used it.

--------------------------------------------------

Type `{BOT_PREFIX}help <directory>`, where `directory` is one of the following:
**Details**
**Commands**
""")

        elif section.lower() == "details":
            owner = await self.bot.fetch_user(self.bot.owner_id)
            await ctx.send(f"""
**Details:**
Command prefix: `{BOT_PREFIX}`
Create a custom directory to better organize your channels.

This bot was created by: {owner.name+"#"+owner.discriminator}
Support Server invite: https://discord.gg/j2y7jxQ
Warning: Support server may contain swearing in open channels.
*Consider DMing the developer instead for questions/information.

Number of servers this bot is in now: {len(self.bot.guilds)}
:asterisk: Number of servers using the new directory system: {len(self.bot.univ.Directories.keys())}
""")
            
        elif section.lower() == "commands":
            if subsection == None:
                await ctx.send(f"""
**Commands**
Type `{BOT_PREFIX}help commands <command>`, where `command` is one of the following:
```
Directory -- Control the directory setup
    setup             - You require the "Manage Server" and "M/Channels" permissions.
    teardown          - You require the "Manage Server" and "M/Channels" permissions.

Channels -- Manage channels in the directory
    create_channel    - You require the "Manage Channels" permission.
    create_category   - You require the "Manage Channels" permission.
    delete_category   - You require the "Manage Channels" permission.
    rename_channel    - You require the "Manage Channels" permission.
    move_channel      - You require the "Manage Channels" permission.
    import_channel    - You require the "Manage Channels" permission.
    hide_channel      - You require the "Manage Channels" permission.
    save_directory    - No Limits
    update            - You require the "Manage Channels" permission.

General -- General commands
    help              - No Limits
    invite            - No Limits
```
""")
            elif subsection.lower() == "setup":
                await ctx.send(f"""
**SETUP**; Aliases: "su"
`{BOT_PREFIX}setup`
------------------------------
Set up your new custom directory system.
**--** Attaching a cdr_directory.pkl file with proper contents generated by the `{BOT_PREFIX}save_directory` command will load an existing directory based on that file.
**--** You should never delete the category created by the bot. Doing this will disorganize potentially hundreds of channels under it.
**----** Do prevent these inconveniences that I should be worried about, use the `{BOT_PREFIX}teardown` command. I'll handle everything.
""")

            elif subsection.lower() == "teardown":
                await ctx.send(f"""
**TEARDOWN**; Aliases: "td"
`{BOT_PREFIX}teardown`
------------------------------
Deconstruct the custom directory system added to your server, provided by me.
**--** IMPORTANT! Use this command especially if you have a lot of channels under the category that I created.
""")

            elif subsection.lower() == "new_channel":
                await ctx.send(f"""
**CREATE_CHANNEL**; Aliases: "new_ch"
`{BOT_PREFIX}create_channel <directory> <name>`
------------------------------
Create a new channel under `directory` with the name `name`.
**--** It is recommended not to make 2 channels with the same name in the same directory! (This is not allowed by the bot anymore)
**--** To delete a channel, simply nagivate to the channel using the directory (or manually), channel options, and click Delete Channel. The bot will automatically update the directory. If not, use this command:
**----** `{BOT_PREFIX}update`
""")

            elif subsection.lower() == "create_channel":
                await ctx.send(f"""
**CREATE_CATEGORY**; Aliases: "new_cat"
`{BOT_PREFIX}create_category <directory> <name>`
------------------------------
Create a new category under `directory` with the name `name`.
**--** It is recommended not to make 2 categories with the same name in the same directory! (This is not allowed by the bot anymore)
""")

            elif subsection.lower() == "delete_category":
                await ctx.send(f"""
**DELETE_CATEGORY**; Aliases: "del_cat"
`{BOT_PREFIX}delete_category <directory> <name>`
------------------------------
Delete a category, along with all channels within it.
**-- THIS ACTION CANNOT BE UNDONE.**
""")

            elif subsection.lower() == "rename_channel":
                await ctx.send(f"""
**RENAME_CHANNEL**; Aliases: "rn_ch"
`{BOT_PREFIX}rename_channel <directory> <name> <rename>`
------------------------------
Rename the channel at the directory `directory` with name `name` to `rename`.
**--** You cannot rename to a channel already with the same name in the same directory.
""")

            elif subsection.lower() == "move_channel":
                await ctx.send(f"""
**MOVE_CHANNEL**; Aliases: "mv_ch"
`{BOT_PREFIX}move_channel <directory> <name> <new_directory>`
------------------------------
Moves a channel or category at the directory `directory` with name `name` to the directory `new_directory`.
**--** You cannot move a channel or category if the destination already has a channel or category with that name.
""")

            elif subsection.lower() == "import_channel":
                await ctx.send(f"""
**IMPORT_CHANNEL**; Aliases: "imp_ch"
`{BOT_PREFIX}import_channel <channel> <new_directory> <name>`
------------------------------
Imports an existing channel into the directory `new_directory` with the name `name`.
**--** Your channel will not be moved or changed.
**--** You cannot import a channel if the destination already has a channel or category with the name `name`.
""")
            elif subsection.lower() == "hide_channel":
                await ctx.send(f"""
**HIDE_CHANNEL**; Aliases: "hd_ch"
`{BOT_PREFIX}hide_channel <directory> <name>`
------------------------------
Hide an existing channel from the directory `directory` with the name `name`.
**--** Your channel will not be moved, changed, or deleted.
**--** To make it appear again, use the `import_channel` command to import it back in a directory.
""")
            elif subsection.lower() == "save_directory":
                await ctx.send(f"""
**SAVE_DIRECTORY**; Aliases: "save"
`{BOT_PREFIX}save_directory`
------------------------------
Save your current directory setup to a file to be loaded later at any time.
**--** This file contains pickled data using Python.
**--** To load said file, use the `{BOT_PREFIX}setup` command and attach the file to proceed.
**----** The process takes longer depending on how many channels are in the entire directory.
""")
            elif subsection.lower() == "update":
                await ctx.send(f"""
**UPDATE**
`{BOT_PREFIX}update`
------------------------------
Updates the directory channel.
**--** The more channels in the directory, the longer it takes to finish.
**----** During this time, no changes can be made to the directory.

**--** This command is automatically called when any channel in your server is deleted.
**----** If channels are being deleted faster than the bot can update, you may have to update it manually when you are done.

**--** The more channels that are deleted when calling this command, the longer it takes to finish.
**----** The system works by checking if a channel exists. If not, it updates internal memory and restarts.
""")

            elif subsection.lower() == "help":
                await ctx.send(f"""
**HELP**
`{BOT_PREFIX}help [section] [subsection]`
------------------------------
Sends a help message.
**--** The `section` and `subsection` arguments:
**----** Typing `{BOT_PREFIX}help` will give you `section` names.
**----** If `section` is "commands", `subsection` help on a certain command.
""")

            elif subsection.lower() == "invite":
                await ctx.send(f"""
**INVITE**
`{BOT_PREFIX}invite`
------------------------------
Sends an invite link to let me join a server.
""")

def setup(bot: Bot):
    bot.add_cog(Misc_Commands(bot))
