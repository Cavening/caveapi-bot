import discord
import sys
import os

from dotenv import load_dotenv

sys.dont_write_bytecode = True
load_dotenv()
bot = discord.Bot()


@bot.event
async def on_ready():
    for guild in bot.guilds:
        print(str(bot.user) + " Bot wurde auf dem '" + str(guild.id) + "' Server gestartet.")

for path in ["src/commands"]:
    for filename in os.listdir("./" + path):
        if filename.endswith(".py"):
            path = path.replace("/", ".")
            file_name = str(filename[:-3])

            bot.load_extension(path + "." + file_name)

bot.run(os.getenv("BOT_TOKEN"))
