import discord

from src.api.services_api import ServicesView
from src.api.request import accountRequest
from src.api.api import embed_color
from discord.ext import commands


class ServicesCommand(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.slash_command(
        name="services",
        description="See your services on Cavening"
    )
    @discord.default_permissions(
        administrator=True
    )
    async def _services(self, ctx: discord.ApplicationContext):
        await ctx.defer(
            ephemeral=True
        )

        account_details = await accountRequest()
        view = None

        if not account_details["success"]:
            services = discord.Embed(
                description="Es gab einen Fehler mit der Verbindung.",
                color=embed_color
            )
        else:
            account_detail = account_details["data"]
            product_kvm = str(len(account_detail["products"]["kvm_server"]["nl"]) + len(account_detail["products"]["kvm_server"]["de"]))
            product_domain = str(len(account_detail["products"]["domains"]))
            product_custom = str(len(account_detail["products"]["custom_products"]) + len(account_detail["products"]["custom_services"]))

            services = discord.Embed(
                color=embed_color
            )
            services.add_field(
                name="``💻`` **Deine Dienste**:",
                value="> **KVM-Server**: " + product_kvm + "\n> **Domains**: " + product_domain + "\n> **Weitere Dienste**: " + product_custom
            )

            params = {
                "kvm_server": product_kvm,
                "domains": product_domain,
                "custom_products": product_custom
            }
            view = ServicesView(self.bot, params)

        await ctx.respond(
            embed=services,
            view=view
        )


def setup(bot):
    bot.add_cog(ServicesCommand(bot))
