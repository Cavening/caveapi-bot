import discord

from src.api.request import url_web_users, accountRequest
from src.api.api import embed_color, commandPing
from discord.ext import commands


class AccountCommand(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.slash_command(
        name="account",
        description="Siehe dein Konto bei Cavening"
    )
    @discord.default_permissions(
        administrator=True
    )
    async def _account(self, ctx: discord.ApplicationContext):
        await ctx.defer(
            ephemeral=True
        )

        account_details = await accountRequest()
        account_donation = await accountRequest(True)
        if not account_details["success"]:
            account = discord.Embed(
                description="Es gab einen Fehler mit der Verbindung.",
                color=embed_color
            )
        else:
            account_detail = account_details["data"]
            icon_url = None
            if account_donation["success"]:
                icon_url = account_donation["data"]["profile_picture"]

            account = discord.Embed(
                color=embed_color
            )
            account.set_author(
                name=account_detail["username"],
                icon_url=icon_url,
                url=url_web_users
            )
            account.add_field(
                name="``🙋‍♂️`` **Vorname**:",
                value="N/A" if str(account_detail["full_name"]).split(" ")[0] == "" else
                str(account_detail["full_name"]).split(" ")[0],
                inline=False
            )
            account.add_field(
                name="``💸`` **Guthaben**:",
                value=str(account_detail["balance"]["value"]) + "€",
                inline=False
            )
            command = await commandPing(self.bot, "services")
            account.add_field(
                name="``💻`` **Deine Dienste**:",
                value="Siehe " + command,
                inline=False
            )

        await ctx.respond(
            embed=account
        )


def setup(bot):
    bot.add_cog(AccountCommand(bot))
