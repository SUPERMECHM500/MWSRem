
# Lib
from os import popen, getcwd
from os.path import join, exists
from asyncio import sleep
from datetime import datetime
from pickle import dump

# Site
from discord.activity import Activity
from discord.enums import ActivityType, Status
from discord.ext.commands.cog import Cog
from discord.ext.tasks import loop

# Local
from utils.classes import Bot


class BackgroundTasks(Cog):
    """Background loops"""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.dblpy = self.bot.connect_dbl()
        self.bot.univ.Loops = []
        self.bot.univ.Loops.append(self.save_data.start())
        self.bot.univ.Loops.append(self.status_change.start())

    @loop(seconds=60)
    async def status_change(self):
        utchour = str(datetime.utcnow().hour)
        utcminute = str(datetime.utcnow().minute)
        if len(utchour) == 1:
            utchour = "0" + utchour
        if len(utcminute) == 1:
            utcminute = "0" + utcminute
        time = f"{utchour}:{utcminute}"

        if self.bot.univ.Inactive >= 5:
            status = Status.idle
        else:
            status = Status.online

        if self.bot.debug_mode:
            activity = Activity(type=ActivityType.playing, name="in DEBUG MODE")
        else:
            activity = Activity(
                type=ActivityType.watching,
                name=f"{self.bot.command_prefix}help | UTC: {time}"
            )

        await self.bot.change_presence(status=status, activity=activity)

    @loop(seconds=60)
    async def save_data(self):
        hour = str(datetime.now().hour)
        minute = str(datetime.now().minute)
        date = str(str(datetime.now().date().month) + "/" + str(datetime.now().date().day) + "/" + str(
            datetime.now().date().year))
        if len(hour) == 1:
            hour = "0" + hour
        if len(minute) == 1:
            minute = "0" + minute
        time = f"{hour}:{minute}, {date}"

        print("Saving...", end="\r")
        with open(join(getcwd(), "Serialized", "data.pkl"), "wb") as f:
            data = {
                "Directories": self.bot.univ.Directories
            }

            try:
                dump(data, f)
            except Exception as e:
                print(f"[{time} || Unable to save] Pickle dumping Error:", e)

        with open(join(getcwd(), "Serialized", "bot_config.pkl"), "wb") as f:
            config_data = {
                "debug_mode": self.bot.debug_mode,
                "auto_pull": self.bot.auto_pull,
                "prefix": self.bot.command_prefix
            }

            try:
                dump(config_data, f)
            except Exception as e:
                print("[Unknown Error] Pickle dumping error:", e)

        self.bot.univ.Inactive = self.bot.univ.Inactive + 1
        print(f"[CDR: {time}] Saved data.", end="\n" if not self.bot.auto_pull else "\r")

        if self.bot.auto_pull:
            print(f"[CDR: {time}] Saved data. Auto-pull: Checking git repository for changes...{' '*30}", end="\r")
            resp = popen("git pull").read()
            resp = f"```diff\n{resp}\n```"
            if str(resp) != f"```diff\nAlready up to date.\n\n```":
                for i in self.bot.owner_ids:
                    owner = self.bot.get_user(i)
                    await owner.send(f"**__Auto-pulled from github repository and restarted cogs.__**\n{resp}")
                    print(f"[CDR: {time}] Saved data. Auto-pull: Changes sent to owner via Discord.")

                for x_loop in self.bot.univ.Loops:
                    x_loop.cancel()

                modules = {module.__module__: cog for cog, module in self.bot.cogs.items()}
                for module in modules:
                    self.bot.reload_extension(module)
            else:
                print(f'[CDR: {time}] Saved data. Auto-pull: No new changes.{" "*30}')

    @status_change.before_loop
    async def sc_wait(self):
        await self.bot.wait_until_ready()
        await sleep(30)

    @save_data.before_loop
    async def sd_wait(self):
        await self.bot.wait_until_ready()
        await sleep(15)


def setup(bot: Bot):
    bot.add_cog(BackgroundTasks(bot))
