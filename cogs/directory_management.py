# Lib
from contextlib import suppress
from copy import deepcopy
from os import remove
from asyncio import TimeoutError, sleep
from pickle import Unpickler, dump

# Site
from discord import TextChannel
from discord.ext.commands import cooldown, BucketType
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import bot_has_permissions, command, has_permissions
from discord.errors import NotFound, HTTPException
from discord.file import File

# Local
from utils.classes import Bot
from utils.directory_mgmt import recurse_index, loadingupdate as loading

required_permissions_total = {
    "manage_channels": True,
    "manage_roles": True,
    "manage_messages": True,
    "read_messages": True,
    "send_messages": True,
    "attach_files": True,
    "add_reactions": True
}

required_permissions = {
    "read_messages": True,
    "manage_messages": True,
    "send_messages": True
}


class Commands(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.bot.remove_command("help")

    @cooldown(1, 300, BucketType.guild)
    @bot_has_permissions(manage_channels=True, add_reactions=True, manage_roles=True, **required_permissions)
    @has_permissions(manage_channels=True, manage_guild=True)
    @command(name="setup", aliases=["su"])
    async def setup_directory(self, ctx: Context):
        if not ctx.guild:
            await ctx.send("This command cannot be used in a DM channel.")
            return

        if ctx.guild.id in self.bot.univ.LoadingUpdate:
            await ctx.send("Wait a second, you impatient being!\n`The directory is being updated at the moment.`",
                           delete_after=5)
            return
        else:
            with loading(self.bot, ctx.guild.id):

                if ctx.guild.id in self.bot.univ.Directories:
                    msg = await ctx.send("You already have a directory tree set up. Continue anyway?\n"
                                         "Note: Your old channels will not be deleted, "
                                         "but the old directory channel will not be kept updated or managed anymore.\n"
                                         "*The restart button **will** teardown the old directory for you.*\n"
                                         "`[  ] (within 30 seconds)`"
                                         )

                    await msg.add_reaction("✅")
                    await msg.add_reaction("❎")
                    await msg.add_reaction("🔄")

                else:
                    msg = await ctx.send("This setup will create a new category that you can edit.\n"
                                         "The category is used by the bot to identify "
                                         "it as a storage system for the channels.\n\n"
                                         "The entire process is handled by me so, mind your manners, please.\n"
                                         "`[  ] (within 30 seconds)`"
                                         )
                    await msg.add_reaction("✅")
                    await msg.add_reaction("❎")

                def check(c_reaction, c_user):
                    emj = ["✅", "❎"]
                    if ctx.guild.id in self.bot.univ.Directories:
                        emj.append("🔄")

                    return str(c_reaction.emoji) in emj and c_user == ctx.author and c_reaction.message.id == msg.id

                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=30, check=check)
                except TimeoutError:
                    await msg.edit(content="You timed out, so I wont continue.")
                    await msg.clear_reactions()

                    return
                else:
                    await reaction.remove(user)
                    if ctx.guild.id in self.bot.univ.Directories:
                        if str(reaction.emoji) == "❎":
                            await msg.edit(content="You already have a directory tree set up. Continue anyway?\n"
                                                   "Note: Your old channels will not be deleted, "
                                                   "but the old directory channel will not be kept "
                                                   "updated or managed anymore.\n"
                                                   "*The restart button **will** teardown the old directory for you.*\n"
                                                   "`[❎] (=================)`"
                                           )
                            await msg.clear_reactions()
                            await sleep(2)
                            await msg.edit(content="Okay, I canceled the operation.")
                            ctx.command.reset_cooldown(ctx)

                            return

                        elif str(reaction.emoji) == "✅":
                            await msg.edit(content="You already have a directory tree set up. Continue anyway?\n"
                                                   "Note: Your old channels will not be deleted, "
                                                   "but the old directory channel will not be kept "
                                                   "updated or managed anymore.\n"
                                                   "*The restart button **will** teardown the old directory for you.*\n"
                                                   "`[✅] (=================)`"
                                           )
                            with suppress(Exception):
                                await self.bot.get_channel(self.bot.univ.Directories[ctx.guild.id]["categoryID"]).edit(
                                    name="[❌] Directory Archive")

                        elif str(reaction.emoji) == "🔄":
                            await msg.edit(content="You already have a directory tree set up. Continue anyway?\n"
                                                   "Note: Your old channels will not be deleted, "
                                                   "but the old directory channel will not be kept "
                                                   "updated or managed anymore.\n"
                                                   "*The restart button **will** teardown the old directory for you.*\n"
                                                   "`[🔄] (=================)`"
                                           )

                            await msg.clear_reactions()
                            await sleep(2)
                            await msg.edit(content="Tearing down...")

                            try:
                                category = self.bot.get_channel(self.bot.univ.Directories[ctx.guild.id]["categoryID"])
                            except NotFound:
                                await msg.edit(content="I couldn't find the category for the channels.")
                                await sleep(2)
                                self.bot.univ.Directories.pop(ctx.guild.id)
                            else:
                                for i in category.channels:
                                    await i.delete()

                                await category.delete()

                                self.bot.univ.Directories.pop(ctx.guild.id)

                                await msg.edit(content="Teardown complete.")

                    else:
                        if str(reaction.emoji) == "❎":
                            await msg.edit(content="This setup will create a new category that you can edit.\n"
                                                   "The category is used by the bot to identify "
                                                   "it as a storage system for the channels.\n\n"
                                                   "The entire process is handled by me so, mind your manners, please."
                                                   "\n`[❎] (=================)`"
                                           )

                            await msg.clear_reactions()
                            await sleep(2)
                            await msg.edit(content="Okay, I canceled the operation.")
                            ctx.command.reset_cooldown(ctx)

                            return

                        elif str(reaction.emoji) == "✅":
                            await msg.edit(content="This setup will create a new category that you can edit.\n"
                                                   "The category is used by the bot to identify "
                                                   "it as a storage system for the channels.\n\n"
                                                   "The entire process is handled by me so, mind your manners, please."
                                                   "\n`[✅] (=================)`"
                                           )
                    await msg.clear_reactions()
                    await sleep(2)
                    if ctx.guild.id in self.bot.univ.Directories:
                        self.bot.univ.Directories.pop(ctx.guild.id)

                    if ctx.guild.id not in self.bot.univ.Directories:
                        if ctx.message.attachments:
                            file = None
                            for i in ctx.message.attachments:
                                if i.filename == f"cdr_directory.pkl":
                                    file = i
                                    break

                            await msg.edit(content="You've attached a valid file to your message.\n"
                                                   "Do you want to attempt to load it?\n"
                                                   "`[  ] (within 10 seconds)`"
                                           )
                            await msg.add_reaction("✅")
                            await msg.add_reaction("❎")

                            def check(c_reaction, c_user):
                                return str(c_reaction.emoji) in ["✅",  "❎"] \
                                       and c_user.id == ctx.author.id and c_reaction.message.id == msg.id

                            try:
                                reaction, user = await self.bot.wait_for("reaction_add", timeout=10, check=check)
                            except TimeoutError:
                                await msg.clear_reactions()
                                await msg.edit(content="You timed out, so I canceled the operation.")

                                return
                            else:
                                await msg.clear_reactions()
                                if str(reaction.emoji) == "❎":
                                    await msg.edit(content="You've attached a valid file to your message.\n"
                                                           "Do you want to attempt to load it?\n"
                                                           "`[❎] (=================)`"
                                                   )
                                    await sleep(2)
                                    await msg.clear_reactions()

                                    await msg.edit(content="Setting up now...")
                                    cat = await ctx.guild.create_category("Directory Archive")
                                    directory = await cat.create_text_channel("directory",
                                                                              topic="Managers: Leave this channel "
                                                                                    "on top for easy access. "
                                                                                    "Also do not delete it.")

                                    await directory.set_permissions(ctx.guild.default_role, send_messages=False)
                                    member_self = await ctx.guild.fetch_member(self.bot.user.id)
                                    await directory.set_permissions(member_self, send_messages=True)

                                    await msg.edit(
                                        content=f"Finished setup. Get to the directory here: {directory.mention}")

                                    dmessage = await directory.send("Finishing setup...")

                                    self.bot.univ.Directories.update(
                                        {ctx.guild.id: {"categoryID": cat.id,
                                                        "channelID": directory.id,
                                                        "messageID": dmessage.id,
                                                        "tree": {
                                                            "root": {}
                                                            }
                                                        }
                                         }
                                    )

                                    await self.bot.update_directory(ctx, note="Finished setup.")
                                    await msg.edit(content=f"Finished setup. "
                                                           f"Get to the directory here: {directory.mention}")

                                    return

                                elif str(reaction.emoji) == "✅":
                                    await msg.edit(content="You've attached a valid file to your message.\n"
                                                           "Do you want to attempt to load it?\n"
                                                           "`[✅] (=================)`"
                                                   )

                                    await sleep(2)
                                    await msg.edit(content="Setting up with attached file...")

                                    await file.save(f"{self.bot.cwd}/Workspace/incoming_{ctx.guild.id}.pkl")
                                    with open(f"{self.bot.cwd}/Workspace/incoming_{ctx.guild.id}.pkl", "rb") as f:
                                        try:
                                            tree = Unpickler(f).load()
                                            # TODO: WARNING: USERS CAN UPLOAD MALICIOUS .PKLs MAKING THIS INSECURE.

                                        except Exception as e:
                                            await msg.edit(
                                                content=f"The setup failed because the file is either changed, "
                                                        f"corrupted, or outdated.\n"
                                                        f"`Error description: {e}`")

                                            return

                                    remove(f"{self.bot.cwd}/Workspace/incoming_{ctx.guild.id}.pkl")

                                    cat = await ctx.guild.create_category("Directory Archive")
                                    directory = await cat.create_text_channel("directory",
                                                                              topic="Managers: Leave this channel "
                                                                                    "on top for easy access. "
                                                                                    "Also do not delete it.")

                                    await directory.set_permissions(ctx.guild.default_role, send_messages=False)
                                    member_self = await ctx.guild.fetch_member(self.bot.user.id)
                                    await directory.set_permissions(member_self, send_messages=True)
                                    await directory.set_permissions(ctx.author, send_messages=True)

                                    dmessage = await directory.send("Adding channels...")

                                    self.bot.univ.Directories.update(
                                        {ctx.guild.id: {"categoryID": cat.id,
                                                        "channelID": directory.id,
                                                        "messageID": dmessage.id,
                                                        "tree": {}
                                                        }
                                         }
                                    )

                                    try:

                                        tree = await self.bot.convert_to_directory(ctx, tree)
                                        self.bot.univ.Directories[ctx.guild.id]["tree"] = tree
                                    except TypeError as e:
                                        self.bot.univ.Directories.pop(ctx.guild.id)
                                        for i in cat.channels:
                                            await i.delete()

                                        await cat.delete()
                                        await msg.edit(
                                            content=f"The setup failed because the file does not contain valid data.\n"
                                                    f"`Error description: {e}`")

                                        return
                                    else:
                                        await self.bot.update_directory(ctx=ctx, note="Finished automated setup.")
                                        await msg.edit(content=f"Finished setup. "
                                                               f"Get to the directory here: {directory.mention}")

                                    return
                        else:
                            await msg.clear_reactions()

                            await msg.edit(content="Setting up now...")
                            cat = await ctx.guild.create_category("Directory Archive")
                            directory = await cat.create_text_channel("directory",
                                                                      topic="Managers: "
                                                                            "Leave this channel on top for "
                                                                            "easy access. Also do not delete it.")

                            await directory.set_permissions(ctx.guild.default_role, send_messages=False)
                            member_self = await ctx.guild.fetch_member(self.bot.user.id)
                            await directory.set_permissions(member_self, send_messages=True)

                            dmessage = await directory.send("Finishing setup...")

                            self.bot.univ.Directories.update(
                                {ctx.guild.id: {"categoryID": cat.id,
                                                "channelID": directory.id,
                                                "messageID": dmessage.id,
                                                "tree": {
                                                    "root": {}
                                                         }
                                                }
                                 }
                            )

                            await self.bot.update_directory(ctx, note="Finished setup.")
                            await msg.edit(content=f"Finished setup. Get to the directory here: {directory.mention}")

                            return

    @cooldown(1, 30, BucketType.guild)
    @bot_has_permissions(manage_channels=True, **required_permissions)
    @has_permissions(manage_channels=True, manage_guild=True)
    @command(name="teardown", aliases=["td"])
    async def teardown_directory(self, ctx: Context, categoryid: int = 0):
        if not ctx.guild:
            await ctx.send("This command cannot be used in a DM channel.")
            return

        if ctx.guild.id in self.bot.univ.LoadingUpdate:
            await ctx.send("Wait a second, you impatient being!\n`The directory is being updated at the moment.`",
                           delete_after=5)
            return
        else:
            with loading(self.bot, ctx.guild.id):

                if categoryid == 0:
                    if ctx.guild.id in self.bot.univ.Directories:
                        if ctx.channel.id == self.bot.univ.Directories[ctx.guild.id]["channelID"]:
                            await ctx.send("You can't do that here!", delete_after=5)
                            ctx.command.reset_cooldown(ctx)

                            return

                        msg = await ctx.send(
                            "Are you sure? **This will delete every channel"
                            "created by the bot unless it is imported**.\n"
                            "If you want to, you can save your directory first using the `save_directory` command.\n"
                            "`[  ] (within 30 seconds)`"
                            )

                        await msg.add_reaction("✅")
                        await msg.add_reaction("❎")

                        def check(c_reaction, c_user):
                            return str(c_reaction.emoji) in ["✅", "❎"] \
                                   and c_user.id == ctx.author.id and c_reaction.message.id == msg.id

                        try:
                            reaction, user = await self.bot.wait_for("reaction_add", timeout=30, check=check)
                        except TimeoutError:
                            await msg.clear_reactions()
                            await msg.edit(content="You timed out, so I wont continue.")

                            return
                        else:
                            await msg.clear_reactions()
                            if str(reaction.emoji) == "❎":
                                await msg.edit(
                                    content="Are you sure? **This will delete every channel"
                                            "created by the bot unless it is imported**.\n"
                                            "If you want to, you can save your directory first "
                                            "using the `save_directory` command.\n"
                                            "`[❎] (=================)`"
                                    )
                                ctx.command.reset_cooldown(ctx)

                                await sleep(2)
                                await msg.edit(content="Okay, I canceled the operation.")

                                return

                            elif str(reaction.emoji) == "✅":
                                await msg.edit(
                                    content="Are you sure? **This will delete every channel"
                                            "created by the bot unless it is imported**.\n"
                                            "If you want to, you can save your directory first "
                                            "using the `save_directory` command.\n"
                                            "`[✅] (=================)`"
                                    )

                                await sleep(2)
                                await msg.edit(content="Tearing down...")

                                await self.bot.update_directory(ctx, note="Memory updated; Teardown in progress;")
                                tree = deepcopy(self.bot.univ.Directories[reaction.message.guild.id]["tree"])
                                while True:
                                    ids = self.bot.get_all_ids(tree, c_ids=list())
                                    if isinstance(ids, dict):
                                        tree = ids
                                        continue
                                    elif isinstance(ids, list):
                                        break

                                for x in ids:
                                    if not x[1]:
                                        ch = self.bot.get_channel(x[0])
                                        if ch:
                                            await ch.delete()
                                            await sleep(0.1)

                                category = self.bot.get_channel(
                                    self.bot.univ.Directories[ctx.guild.id]["categoryID"])
                                await category.delete()

                                dchannel = self.bot.get_channel(
                                    self.bot.univ.Directories[ctx.guild.id]["channelID"])
                                await dchannel.delete()

                                self.bot.univ.Directories.pop(ctx.guild.id)

                                await msg.edit(content="Teardown complete.")
                    else:
                        await ctx.send("You don't have a directory to tear down.")
                else:
                    if ctx.guild.id in self.bot.univ.Directories and ctx.channel.id == \
                            self.bot.univ.Directories[ctx.guild.id]["channelID"]:
                        await ctx.send("You can't do that here!", delete_after=5)

                        return

                    if ctx.guild.id in self.bot.univ.Directories and categoryid == \
                            self.bot.univ.Directories[ctx.guild.id]["categoryID"]:
                        await ctx.send(
                            "You cannot specify the external category used for the directory. "
                            "In that case, don't specify any ID.",
                            delete_after=5)

                        return

                    try:
                        category = self.bot.get_channel(categoryid)
                    except NotFound:
                        await ctx.send("No category with that ID exists.")
                    else:
                        if categoryid not in [guild.id for guild in ctx.guild.channels]:
                            await ctx.send(
                                "That category does exist, but it isn't in your server. Why would I let you do that?")

                            return

                    msg = await ctx.send("Are you sure?\n"
                                         "Confirm: You are deleting an external category. "
                                         "This will delete **EVERY** channel under it.\n"
                                         "`[  ] (within 10 seconds)`"
                                         )

                    await msg.add_reaction("✅")
                    await msg.add_reaction("❎")

                    def check(c_reaction, c_user):
                        return str(c_reaction.emoji) in ["✅", "❎"] \
                               and c_user == ctx.author and c_reaction.message.id == msg.id

                    try:
                        reaction, user = await self.bot.wait_for("reaction_add", timeout=10, check=check)
                    except TimeoutError:
                        await msg.clear_reactions()
                        await msg.edit(content="You timed out, so I wont continue.")

                        return
                    else:
                        await msg.clear_reactions()
                        if str(reaction.emoji) == "❎":
                            await msg.edit(
                                content="Are you sure?\n"
                                        "Confirm: You are deleting an external category. "
                                        "This will delete **EVERY** channel under it.\n"
                                        "`[❎] (=================)`"
                                )
                            ctx.command.reset_cooldown(ctx)

                            await sleep(2)
                            await msg.edit(content="Okay, I canceled the operation.")

                            return

                        elif str(reaction.emoji) == "✅":
                            await msg.edit(content="Are you sure?\n"
                                                   "Confirm: You are deleting an external category. "
                                                   "This will delete **EVERY** channel under it.\n"
                                                   "`[✅] (=================)`"
                                           )

                            await sleep(2)
                            await msg.edit(content="Tearing down external category...")

                            for i in category.channels:
                                await i.delete()

                            await category.delete()

                            await msg.edit(
                                content="Teardown complete. "
                                        "Note that imported channels from that directory "
                                        "will no longer appear in the directory if you have it set up.")
                            if ctx.guild.id in self.bot.univ.Directories:
                                await self.bot.update_directory(ctx=ctx,
                                                                note="External category deletion; "
                                                                     "Imported channels from that category now removed."
                                                                )

                            return

    @cooldown(1, 5, BucketType.guild)
    @command(aliases=["new_ch"])
    @bot_has_permissions(manage_channels=True, **required_permissions)
    @has_permissions(manage_channels=True)
    async def create_channel(self, ctx: Context, directory: str, name: str):
        if not ctx.guild:
            await ctx.send("This command cannot be used in a DM channel.")
            return

        if ctx.guild.id in self.bot.univ.LoadingUpdate:
            await ctx.send("Wait a second, you impatient being!\n`The directory is being updated at the moment.`",
                           delete_after=5)
            return

        else:
            with loading(self.bot, ctx.guild.id):

                if ctx.guild.id in self.bot.univ.Directories:
                    if ctx.channel.id == self.bot.univ.Directories[ctx.guild.id]["channelID"]:
                        if len(name) > 50:
                            await ctx.send("\"name\" cannot be greater than 50 characters long.", delete_after=5)

                            return

                        path = directory.split("//")
                        if len(path) > 10:
                            await ctx.send("You cannot create a channel in a directory deeper than 10 levels.\n"
                                           "`A level is one position in your path: root(1)/level(2)/level(3)/etc(4)`",
                                           delete_after=10)

                            return

                        try:
                            get_item = recurse_index(self.bot.univ.Directories[ctx.guild.id]['tree'], path)

                        except KeyError as e:
                            await ctx.send(f"That directory doesn't exist.\n`Invalid category: {e}`", delete_after=5)
                            return

                        else:
                            try:
                                if isinstance(get_item, tuple):
                                    raise KeyError(str(path[-1]))
                                else:
                                    if name in get_item:
                                        await ctx.send("A channel or category in that directory already exists.",
                                                       delete_after=5)
                                        return

                                    category = self.bot.get_channel(
                                        self.bot.univ.Directories[ctx.guild.id]["categoryID"])
                                    dchannel = self.bot.get_channel(
                                        self.bot.univ.Directories[ctx.guild.id]["channelID"])
                                    channel = await category.create_text_channel(f"finishing-creation",
                                                                                 topic=f"Go back: {dchannel.mention}; "
                                                                                       f"Name: \"{name}\"")

                                    await channel.edit(name=str(f"{name}-{channel.id}"))

                                    get_item[name] = (channel.id, False)

                            except KeyError as e:
                                await ctx.send(
                                    f"Your last position, {e}, is a channel, not a category.\n`Invalid category: {e}`",
                                    delete_after=5)
                                return

                            else:
                                await self.bot.update_directory(ctx=ctx,
                                                                note=f"New channel; Name: \"{name}\"; "
                                                                     f"Path: \"{directory}\".")
                                print(f"+ Added new channel to server \"{ctx.guild.name}\".")
                    else:
                        await ctx.send(
                            f"This command must be used in the directory channel created by the bot.\n"
                            f"Deleted it? Use the command `{self.bot.command_prefix}update`.")
                        return
                else:
                    await ctx.send(
                        f"You don't have a directory yet. "
                        f"Use the `{self.bot.command_prefix}setup` command to create one.")
                    return

    @cooldown(1, 5, BucketType.guild)
    @command(aliases=["new_cat"])
    @bot_has_permissions(**required_permissions)
    @has_permissions(manage_channels=True)
    async def create_category(self, ctx, directory, name):
        if not ctx.guild:
            await ctx.send("This command cannot be used in a DM channel.")
            return

        if ctx.guild.id in self.bot.univ.LoadingUpdate:
            await ctx.send("Wait a second, you impatient being!\n`The directory is being updated at the moment.`",
                           delete_after=5)
            return
        else:
            with loading(self.bot, ctx.guild.id):

                if ctx.guild.id in self.bot.univ.Directories:
                    if ctx.channel.id == self.bot.univ.Directories[ctx.guild.id]["channelID"]:
                        if len(name) > 50:
                            await ctx.send("\"name\" cannot be greater than 50.", delete_after=5)
                            return

                        d = directory.split("//")
                        if len(d) > 10:
                            await ctx.send("You cannot create a category in a directory deeper than 10 levels.\n"
                                           "`A level is one position in your path: root(1)/level(2)/level(3)/etc(4)`",
                                           delete_after=10)

                            return

                        try:
                            get_item = recurse_index(self.bot.univ.Directories[ctx.guild.id]['tree'], d)

                        except KeyError as e:
                            await ctx.send(f"That directory doesn't exist.\n`Invalid category name: {e}`",
                                           delete_after=5)

                        else:
                            if isinstance(get_item, tuple):
                                raise KeyError(str(d[-1]))
                            else:
                                if name in get_item:
                                    await ctx.send("A channel or category in that directory already exists.",
                                                   delete_after=5)
                                    return

                                get_item[name] = dict()

                            await self.bot.update_directory(ctx=ctx,
                                                            note=f"New category; Name: \"{name}\"; "
                                                                 f"Path: \"{directory}\".")
                            print(f"+ Added new category to server \"{ctx.guild.name}\".")
                    else:
                        await ctx.send(
                            f"This command must be used in the directory channel created by the bot.\n"
                            f"Deleted it? Use the command `{self.bot.command_prefix}update`.")
                else:
                    await ctx.send(
                        f"You don't have a directory yet. "
                        f"Use the `{self.bot.command_prefix}setup` command to create one.")

    @cooldown(1, 10, BucketType.guild)
    @command(aliases=["del_cat"])
    @bot_has_permissions(manage_channels=True, **required_permissions)
    @has_permissions(manage_channels=True)
    async def delete_category(self, ctx, directory, name):
        if not ctx.guild:
            await ctx.send("This command cannot be used in a DM channel.")
            return

        if ctx.guild.id in self.bot.univ.LoadingUpdate:
            await ctx.send("Wait a second, you impatient being!\n`The directory is being updated at the moment.`",
                           delete_after=5)
            return
        else:
            with loading(self.bot, ctx.guild.id):

                if ctx.guild.id not in self.bot.univ.Directories:
                    await ctx.send(
                        f"You don't have a directory yet. "
                        f"Use the `{self.bot.command_prefix}setup` command to create one."
                    )
                    return

                if ctx.channel.id != self.bot.univ.Directories[ctx.guild.id]["channelID"]:
                    await ctx.send(
                        f"This command must be used in the directory channel created by the bot.\n"
                        f"Deleted it? Use the command `{self.bot.command_prefix}update`."
                    )
                    return

                path = directory.split("//")
                if len(path) > 10:
                    await ctx.send("You cannot delete a category in a directory deeper than 10 levels.\n"
                                   "`A level is one position in your path: root(1)/level(2)/level(3)/etc(4)`",
                                   delete_after=10)
                    return

                get_item = recurse_index(self.bot.univ.Directories[ctx.guild.id]['tree'], path)

                def recurse_delete_category(d: dict):
                    if not isinstance(d, dict):
                        raise TypeError

                    for key, val in d.items():
                        if isinstance(val, tuple):
                            _channel = self.bot.get_channel(val[0])
                            if _channel and not val[1]:
                                yield _channel
                        elif isinstance(val, dict):
                            yield from recurse_delete_category(val)

                try:
                    for channel in recurse_delete_category(get_item[name]):
                        if channel:
                            await channel.delete()

                    get_item.pop(name)

                except TypeError:
                    await ctx.send(
                        "That's a channel silly! If you need to, go to the channel and delete it yourself. "
                        "I currently cannot do that myself.",
                        delete_after=10
                    )
                    return

                except KeyError as e:
                    await ctx.send(f"That directory doesn't exist.\n`Invalid category name: {e}`", delete_after=5)
                    return

                else:
                    await self.bot.update_directory(
                        ctx=ctx,
                        note=f"Deleted category; Name: \"{name}\"; Path: \"{directory}\"."
                    )
                    print(f"- Deleted category from server \"{ctx.guild.name}\".")
                    return

    @cooldown(1, 5, BucketType.guild)
    @command(aliases=["rn_ch"])
    @bot_has_permissions(manage_channels=True, **required_permissions)
    @has_permissions(manage_channels=True)
    async def rename_channel(self, ctx, directory, name, rename):
        if not ctx.guild:
            await ctx.send("This command cannot be used in a DM channel.")
            return

        if ctx.guild.id in self.bot.univ.LoadingUpdate:
            await ctx.send("Wait a second, you impatient being!\n`The directory is being updated at the moment.`",
                           delete_after=5)
            return

        else:
            with loading(self.bot, ctx.guild.id):

                if ctx.guild.id in self.bot.univ.Directories:
                    if ctx.channel.id == self.bot.univ.Directories[ctx.guild.id]["channelID"]:
                        path = directory.split("//")
                        if len(path) > 10:
                            await ctx.send(
                                "You cannot rename a channel or category in a directory deeper than 10 levels.\n"
                                "`A level is one position in your path: root(1)/level(2)/level(3)/etc(4)`",
                                delete_after=10)

                            return

                        if len(name) > 50:
                            await ctx.send("\"name\" cannot be greater than 50 characters long.", delete_after=5)
                            return

                        if len(rename) > 50:
                            await ctx.send("\"name\" cannot be greater than 50 characters long.", delete_after=5)
                            return

                        get_item = recurse_index(self.bot.univ.Directories[ctx.guild.id]['tree'], path)

                        try:
                            get_item[rename] = get_item.pop(name)
                            if isinstance(get_item[rename], tuple):
                                dchannel = self.bot.get_channel(self.bot.univ.Directories[ctx.guild.id]["channelID"])
                                channel = self.bot.get_channel(get_item[rename][0])
                                await channel.edit(name=f"{rename}-{channel.id}",
                                                   topic=f"Go back: {dchannel.mention}; Name: \"{rename}\"")

                        except KeyError as e:
                            await ctx.send(f"That directory doesn't exist.\n`Invalid category name: {e}`",
                                           delete_after=5)
                            return

                        else:
                            await self.bot.update_directory(ctx=ctx,
                                                            note=f"Renamed channel \"{name}\" "
                                                                 f"to \"{rename}\" in path \"{directory}\".")

                            print(f"= Renamed a channel for server \"{ctx.guild.name}\".")
                            return
                    else:
                        await ctx.send(
                            f"This command must be used in the directory channel created by the bot.\n"
                            f"Deleted it? Use the command `{self.bot.command_prefix}update`.")
                else:
                    await ctx.send(
                        f"You don't have a directory yet. "
                        f"Use the `{self.bot.command_prefix}setup` command to create one.")

    @cooldown(1, 5, BucketType.guild)
    @command(aliases=["mv_ch"])
    @bot_has_permissions(**required_permissions)
    @has_permissions(manage_channels=True)
    async def move_channel(self, ctx, directory, name, new_directory):
        if not ctx.guild:
            await ctx.send("This command cannot be used in a DM channel.")
            return

        if ctx.guild.id in self.bot.univ.LoadingUpdate:
            await ctx.send("Wait a second, you impatient being!\n`The directory is being updated at the moment.`",
                           delete_after=5)
            return
        else:
            with loading(self.bot, ctx.guild.id):

                if ctx.guild.id in self.bot.univ.Directories:
                    if ctx.channel.id == self.bot.univ.Directories[ctx.guild.id]["channelID"]:
                        path = directory.split("//")
                        new_path = new_directory.split("//")
                        if len(path) > 10:
                            await ctx.send("You cannot move a channel in a directory deeper than 10 levels.\n"
                                           "`A level is one position in your path: root(1)/level(2)/level(3)/etc(4)`",
                                           delete_after=10)

                            return

                        if len(new_path) > 10:
                            await ctx.send("You cannot move a channel to a directory deeper than 10 levels.\n"
                                           "`A level is one position in your path: root(1)/level(2)/level(3)/etc(4)`",
                                           delete_after=10)

                            return

                        if len(name) > 50:
                            await ctx.send("\"name\" cannot be greater than 15 characters long.", delete_after=5)
                            return

                        try:
                            get_item = recurse_index(self.bot.univ.Directories[ctx.guild.id]['tree'], path)
                        except KeyError as e:
                            return await ctx.send(f"The starting directory does not exist. Level `{e}` not found.")

                        try:
                            get_new_item = recurse_index(self.bot.univ.Directories[ctx.guild.id]['tree'], new_path)
                        except KeyError as e:
                            return await ctx.send(f"The destination directory does not exist. Level `{e}` not found.")

                        try:
                            if name not in get_new_item:
                                branch = get_item.pop(name)
                            else:
                                await ctx.send(
                                    "The destination directory already has a channel or category with the same name.",
                                    delete_after=5)
                                return

                        except KeyError as e:
                            await ctx.send(f"That directory doesn't exist.\n`Invalid category name: \"{e}\"`",
                                           delete_after=5)
                            return

                        try:
                            get_new_item[name] = branch

                        except KeyError as e:
                            await ctx.send(f"That directory doesn't exist.\n`Invalid category name: {e}`",
                                           delete_after=5)
                            return

                        else:
                            await self.bot.update_directory(ctx=ctx,
                                                            note=f"Moved channel \"{name}\" "
                                                                 f"from path \"{directory}\" to \"{new_directory}\".")
                            print(f"= Moved a channel for server \"{ctx.guild.name}\".")
                            return
                    else:
                        await ctx.send(
                            f"This command must be used in the directory channel created by the bot.\n"
                            f"Deleted it? Use the command `{self.bot.command_prefix}update`.")
                else:
                    await ctx.send(
                        f"You don't have a directory yet. "
                        f"Use the `{self.bot.command_prefix}setup` command to create one.")

    @cooldown(1, 5, BucketType.guild)
    @command(aliases=["imp_ch"])
    @bot_has_permissions(**required_permissions)
    @has_permissions(manage_channels=True)
    async def import_channel(self, ctx, channel: TextChannel, new_directory, name):
        if not ctx.guild:
            await ctx.send("This command cannot be used in a DM channel.")
            return

        if ctx.guild.id in self.bot.univ.LoadingUpdate:
            await ctx.send("Wait a second, you impatient being!\n`The directory is being updated at the moment.`",
                           delete_after=5)
            return
        else:
            with loading(self.bot, ctx.guild.id):

                if ctx.guild.id in self.bot.univ.Directories:
                    if ctx.channel.id == self.bot.univ.Directories[ctx.guild.id]["channelID"]:
                        path = new_directory.split("//")
                        if len(path) > 10:
                            await ctx.send("You cannot import a channel to a directory deeper than 10 levels.\n"
                                           "`A level is one position in your path: root(1)/level(2)/level(3)/etc(4)`",
                                           delete_after=10)

                            return

                        tree = deepcopy(self.bot.univ.Directories[ctx.guild.id]["tree"])
                        while True:
                            ids = self.bot.get_all_ids(tree, c_ids=list())
                            if isinstance(ids, dict):
                                tree = ids
                                continue
                            elif isinstance(ids, list):
                                break

                        if isinstance(ids, list):
                            if channel.id in ids:
                                return await ctx.send("That channel is already in the directory. "
                                                      "It was either created with the new system, or already imported.",
                                                      delete_after=10)
                        else:
                            return

                        get_item = recurse_index(self.bot.univ.Directories[ctx.guild.id]['tree'], path)

                        try:
                            if name not in get_item:
                                get_item[name] = (channel.id, True)
                            else:
                                await ctx.send(
                                    "The destination directory already has a channel or category with the same name.",
                                    delete_after=5)
                                return

                        except KeyError as e:
                            await ctx.send(f"That directory doesn't exist.\n`Invalid category name: {e}`",
                                           delete_after=5)
                            return

                        await self.bot.update_directory(ctx=ctx,
                                                        note=f"Imported channel with name \"{name}\"; "
                                                             f"Path: \"{new_directory}\".")
                        print(f"> Imported channel into directory for server \"{ctx.guild.name}\".")
                        return

                    else:
                        await ctx.send(
                            f"This command must be used in the directory channel created by the bot.\n"
                            f"Deleted it? Use the command `{self.bot.command_prefix}update`.")
                else:
                    await ctx.send(
                        f"You don't have a directory yet. "
                        f"Use the `{self.bot.command_prefix}setup` command to create one.")

    @cooldown(1, 5, BucketType.guild)
    @command(aliases=["hd"])
    @bot_has_permissions(**required_permissions)
    @has_permissions(manage_channels=True)
    async def hide_channel(self, ctx, directory, name):
        if not ctx.guild:
            await ctx.send("This command cannot be used in a DM channel.")
            return

        if ctx.guild.id in self.bot.univ.LoadingUpdate:
            await ctx.send("Wait a second, you impatient being!\n`The directory is being updated at the moment.`",
                           delete_after=5)
            return
        else:
            with loading(self.bot, ctx.guild.id):

                if ctx.guild.id in self.bot.univ.Directories:
                    if ctx.channel.id == self.bot.univ.Directories[ctx.guild.id]["channelID"]:
                        path = directory.split("//")

                        if len(path) > 10:
                            await ctx.send("You cannot hide a channel in a directory deeper than 10 levels.\n"
                                           "`A level is one position in your path: root(1)/level(2)/level(3)/etc(4)`",
                                           delete_after=10)

                            return

                        get_item = recurse_index(self.bot.univ.Directories[ctx.guild.id]['tree'], path)

                        try:
                            if name in get_item:
                                get_item.pop(name)
                            else:
                                await ctx.send("A channel with that name doesn't exist there.", delete_after=5)
                                return

                        except KeyError as e:
                            await ctx.send(f"That directory doesn't exist.\n`Invalid category name: \"{e}\"`",
                                           delete_after=5)
                            return

                        await self.bot.update_directory(ctx=ctx,
                                                        note=f"Removed channel from directory, but was not deleted. "
                                                             f"Name: \"{name}\"; From Path: \"{directory}\".")

                        print(f"< Hidden channel from directory for server \"{ctx.guild.name}\".")
                        return
                    else:
                        await ctx.send(
                            f"This command must be used in the directory channel created by the bot.\n"
                            f"Deleted it? Use the command `{self.bot.command_prefix}update`.")
                else:
                    await ctx.send(
                        f"You don't have a directory yet. "
                        f"Use the `{self.bot.command_prefix}setup` command to create one.")

    @cooldown(1, 120, BucketType.guild)
    @command(aliases=["save"])
    @bot_has_permissions(**required_permissions)
    async def save_directory(self, ctx):
        if not ctx.guild:
            await ctx.send("This command cannot be used in a DM channel.")
            return

        if ctx.guild.id in self.bot.univ.LoadingUpdate:
            await ctx.send("Wait a second, you impatient being!\n`The directory is being updated at the moment.`",
                           delete_after=5)
            return
        else:
            with loading(self.bot, ctx.guild.id):

                if ctx.guild.id in self.bot.univ.Directories:
                    if ctx.channel.id == self.bot.univ.Directories[ctx.guild.id]["channelID"]:
                        await ctx.send("You cannot use that command here.", delete_after=5)
                        return

                    try:
                        open(f"{self.bot.cwd}/Workspace/cdr_directory.pkl", "x").close()
                    except FileExistsError:
                        pass

                    with open(f"{self.bot.cwd}/Workspace/cdr_directory_{ctx.guild.id}.pkl", "wb") as f:
                        data = await self.bot.convert_to_readable(ctx=ctx)
                        dump(data, f)

                    file = File(f"{self.bot.cwd}/Workspace/cdr_directory.pkl")
                    await ctx.author.send(f"This file contains pickled data using Python.\n"
                                          f"Use the command `{self.bot.command_prefix}setup` "
                                          f"and attach the file to load it.",
                                          file=file)

                    await ctx.send("I sent you a Direct Message containing a data file.")

                    remove(f"{self.bot.cwd}/Workspace/cdr_directory_{ctx.guild.id}.pkl")

                    print(f"|| Sent file data from directory to server \"{ctx.guild.name}\".")
                    return
                else:
                    await ctx.send(
                        f"You don't have a directory yet. "
                        f"Use the `{self.bot.command_prefix}setup` command to create one.")

    @cooldown(1, 5, BucketType.guild)
    @command(aliases=["preview", "pvd"])
    @bot_has_permissions(**required_permissions)
    async def preview_directory(self, ctx):
        if ctx.guild and ctx.guild.id in self.bot.univ.Directories and \
                ctx.channel.id == self.bot.univ.Directories[ctx.guild.id]["channelID"]:
            await ctx.send("You cannot use that command here.", delete_after=5)
            return

        message_lines = ["Here is an approximate preview of the file you sent:\n"]
        if ctx.message.attachments:
            file = None
            for i in ctx.message.attachments:
                if i.filename == f"cdr_directory.pkl":
                    file = i
                    break

            if file is None:
                await ctx.send(
                    "You don't have a file named \"cdr_directory.pkl\" attached.\n"
                    "Also make sure that it is a valid Python Pickle file. These are encoded in pure bytes.")
                return
        else:
            await ctx.send("You haven't attached anything to check for.")
            return

        await file.save(f"{self.bot.cwd}/Workspace/incoming_{ctx.guild.id}.pkl")
        with open(f"{self.bot.cwd}/Workspace/incoming_{ctx.guild.id}.pkl", "rb") as f:
            data = Unpickler(f).load()  # TODO: WARNING: USERS CAN UPLOAD MALICIOUS .PKLs MAKING THIS INSECURE

            remove(f"{self.bot.cwd}/Workspace/incoming_{ctx.guild.id}.pkl")

        while True:
            result = self.bot.recurse_read(data["root"], message_lines, preview=True)
            if isinstance(result, dict):
                data["root"] = result
                continue

            else:
                if not list(data["root"].items()):
                    await ctx.send(
                        ":exclamation: The file you sent is empty."
                    )
                    break

                else:
                    message_full = "\n".join(message_lines)
                    try:
                        await ctx.author.send(content=message_full)
                        if ctx.guild:
                            await ctx.send("I sent you a Direct Message with your preview.")

                        break

                    except HTTPException as e:
                        await ctx.author.send(
                            ":exclamation: The directory in the file you sent is too large to be sent as a message. "
                            "A fix will be implemented in the future.\n"
                            "If this is not the case, it is likely a network or Discord error. "
                            f"Please try again.\n"
                            f"`Error description: [{e}]`",
                        )
                        break

    @command()
    @cooldown(1, 10, BucketType.guild)
    @bot_has_permissions(**required_permissions)
    @has_permissions(manage_channels=True)
    async def update(self, ctx):
        if not ctx.guild:
            await ctx.send("This command cannot be used in a DM channel.")
            return

        if ctx.guild.id in self.bot.univ.LoadingUpdate:
            await ctx.send("Wait a second, you impatient being!\n`The directory is being updated at the moment.`",
                           delete_after=5)
            return
        else:
            with loading(self.bot, ctx.guild.id):

                if ctx.guild.id in self.bot.univ.Directories:
                    if self.bot.get_channel(self.bot.univ.Directories[ctx.guild.id]['channelID']) is None:
                        await ctx.send("You need to set up your directory again.")
                        self.bot.univ.Directories.pop(ctx.guild.id)
                        return

                    await self.bot.update_directory(ctx=ctx, note="Update requested manually.")
                    return
                else:
                    await ctx.send(
                        f"You don't have a directory yet. "
                        f"Use the `{self.bot.command_prefix}setup` command to create one.")


def setup(bot: Bot):
    bot.add_cog(Commands(bot))
