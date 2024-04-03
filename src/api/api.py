import discord
import os

embed_color = int("0x" + os.getenv("EMBED_COLOR"), 16)


async def commandPing(bot: discord.Bot, command: str):
    try:
        bot_command = bot.get_command(command)

        command = "</" + command + ":" + str(bot_command.id) + ">"
    except:
        command = "</" + command + ":1>"

    return command
