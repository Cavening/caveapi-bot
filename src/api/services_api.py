import discord
import json

from src.api.request import url_web_kvm, url_web_domain, url_web_custom, accountRequest, kvmRequest, domainRequest
from discord.ui import View, Button, Select
from src.api.api import embed_color

emoji_kvm_nl = "🇳🇱"
emoji_kvm_de = "🇩🇪"
emoji_domains = "🌍"
emoji_custom_products = "🛒"
emoji_custom_service = "💻"
services_label = {
    "kvm_server": "KVM Server",
    "domains": "Domains",
    "custom_products": "Weitere Dienste"
}


class ServicesView(View):
    def __init__(self, bot: discord.Bot, services: json):
        super().__init__(timeout=None)
        self.bot = bot

        for service in services:
            self.add_item(ServiceButton(bot, service, services[service]))


class ServiceButton(Button):
    def __init__(self, bot: discord.Bot, service: str, count: str):
        if count == "0":
            disabled = True
        else:
            disabled = False

        super().__init__(
            label=services_label[service],
            disabled=disabled,
            style=discord.ButtonStyle.blurple,
            custom_id="services_" + service
        )
        self.bot = bot
        self.service = service

    async def callback(self, interaction: discord.Interaction):
        account_details = await accountRequest()
        if not account_details["success"]:
            await interaction.response.edit_message(
                content="``❌`` Fehler! Es gab einen Fehler mit der Verbindung.\n** **"
            )
            return

        services = []
        view = None

        if self.service == "kvm_server":
            kvm_server = account_details["data"]["products"]["kvm_server"]
            for location in kvm_server:
                for data in kvm_server[location]:
                    services.append({
                        "id": data["id"],
                        "name": data["name"],
                        "location": location
                    })

            if len(services) == 0:
                account = discord.Embed(
                    description="Du besitzt derzeit keinen KVM Server.",
                    color=embed_color
                )
            else:
                services_text = []
                for service in services:
                    if service["location"] == "nl":
                        emoji = emoji_kvm_nl
                    else:
                        emoji = emoji_kvm_de

                    services_text.append(
                        emoji + " [#" + str(service["id"]) + "](" + url_web_kvm + str(
                            service["id"]) + ") | " + str(service["name"]))

                account = discord.Embed(
                    description="``💻`` **Deine KVM Server**:\n" + "\n".join(services_text),
                    color=embed_color
                )
        elif self.service == "domains":
            domains_data = account_details["data"]["products"]["domains"]
            for domains in domains_data:
                services.append({
                    "id": domains["id"],
                    "name": domains["name"],
                    "status": domains["status"]
                })

            if len(services) == 0:
                account = discord.Embed(
                    description="Du besitzt derzeit keinen Domains.",
                    color=embed_color
                )
            else:
                services_text = []
                for service in services:
                    services_text.append(
                        emoji_domains + " [#" + str(service["id"]) + "](" + url_web_domain + str(service["id"]) + ") | " + str(service["name"]))

                account = discord.Embed(
                    description="``" + emoji_domains + "`` **Deine Domains**:\n" + "\n".join(services_text),
                    color=embed_color
                )
        elif self.service == "custom_products":
            custom_services_data = account_details["data"]["products"]["custom_services"]
            custom_products_data = account_details["data"]["products"]["custom_products"]
            for custom_services in custom_services_data:
                services.append({
                    "id": custom_services["id"],
                    "name": custom_services["name"],
                    "status": custom_services["status"],
                    "server_content": custom_services["server_content"],
                    "link": custom_services["link"],
                    "type": "services"
                })
            for custom_products in custom_products_data:
                if "project" in custom_products and "name" in custom_products["project"]:
                    services.append({
                        "id": custom_products["id"],
                        "name": custom_products["project"]["name"],
                        "content": custom_products["content"],
                        "type": "products"
                    })
                else:
                    services.append({
                        "id": custom_products["id"],
                        "content": custom_products["content"],
                        "type": "products"
                    })

            if len(services) == 0:
                account = discord.Embed(
                    description="Du besitzt derzeit keine weitere Dienste.",
                    color=embed_color
                )
            else:
                services_text_service = []
                services_text_product = []
                for service in services:
                    if service["type"] == "services":
                        name = str(service["name"])
                    elif service["type"] == "products":
                        if "name" in service:
                            name = str(service["name"])
                        else:
                            name = str(service["content"])

                    services_text_product.append(
                        "[#" + str(service["id"]) + "](" + url_web_custom + str(
                            service["id"]) + ") | " + name)
                if len(services_text_service) == 0:
                    services_text_service.append("/")
                if len(services_text_product) == 0:
                    services_text_product.append("/")

                account = discord.Embed(
                    description="``🖥️`` **__Weitere__**:\n** **",
                    color=embed_color
                )
                account.add_field(
                    name="``" + emoji_custom_service + "`` **Dienste**:",
                    value="\n".join(services_text_service),
                    inline=False
                )
                account.add_field(
                    name="``" + emoji_custom_products + "`` **Produkte**:",
                    value="\n".join(services_text_product),
                    inline=False
                )

        if len(services) != 0:
            view = ServicesSelectView(self.bot, self.service, services)
        await interaction.response.edit_message(
            embed=account,
            view=view
        )


class ServicesSelectView(View):
    def __init__(self, bot: discord.Bot, service: str, params: json):
        super().__init__(timeout=None)
        self.bot = bot

        self.add_item(ServicesSelect(bot, service, params))


class ServicesSelect(Select):
    def __init__(self, bot: discord.Bot, service: str, params: json):
        self.bot = bot
        self.params = params
        self.service = service
        options = []

        if service == "kvm_server":
            for service_data in params:
                if service_data["location"] == "nl":
                    emoji = emoji_kvm_nl
                    description = "Skylink"
                    value = "kvm_skylink_"
                else:
                    emoji = emoji_kvm_de
                    description = "NTT Frankfurt"
                    value = "kvm_ntt_"

                options.append(
                    discord.SelectOption(
                        label=str(service_data["name"]),
                        description="#" + str(service_data["id"]) + " | Standort: " + description,
                        emoji=emoji,
                        value=value + str(service_data["id"])
                    )
                )
        elif service == "domains":
            for service_data in params:
                options.append(
                    discord.SelectOption(
                        label=str(service_data["name"]),
                        description="#" + str(service_data["id"]) + " | TLD: ." + str(service_data["name"]).split(".")[1],
                        emoji=emoji_domains,
                        value="domains_" + str(service_data["name"])
                    )
                )
        elif service == "custom_products":
            for service_data in params:
                if service_data["type"] == "services":
                    options.append(
                        discord.SelectOption(
                            label=str(service_data["name"]),
                            description="Typ: Dienst",
                            emoji=emoji_custom_service,
                            value="custom_services_" + str(service_data["id"])
                        )
                    )
                elif service_data["type"] == "products":
                    if "name" in service_data:
                        label = str(service_data["name"])
                    else:
                        label = str(service_data["content"])

                    options.append(
                        discord.SelectOption(
                            label=label,
                            description="Typ: Produkt",
                            emoji=emoji_custom_products,
                            value="custom_products_" + str(service_data["id"])
                        )
                    )

        super().__init__(
            custom_id="services_select",
            placeholder="🔎 Wähle einen Dienst",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        service_id = str(interaction.data["values"][0]).split("_")
        view = None
        product = {}

        if self.service == "kvm_server":
            kvm_request = await kvmRequest(service_id[2])
            if not kvm_request["success"]:
                await interaction.response.edit_message(
                    content="``❌`` Fehler! Der KVM Server konnte nicht gefunden werden.\n** **"
                )
                return

            kvm_data = kvm_request["data"]
            if service_id[1] == "skylink":
                emoji = emoji_kvm_nl
            else:
                emoji = emoji_kvm_de
            if kvm_data["status"]["status"] == "running":
                status = "🟢"
            elif kvm_data["status"]["status"] == "offline":
                status = "🔴"
            else:
                status = "🟡"

            services = discord.Embed(
                title=emoji + " KVM Server",
                description="``" + status + "`` **Name**: " + str(
                    kvm_data["name"]) + "\n``🪢`` **Hardware**: \n> **" + str(
                    kvm_data["hardware"]["cpu"]["value"]) + " Kern(e)**\n> » " + str(
                    kvm_data["hardware"]["cpu"]["type"]) + "\n> **" + str(
                    kvm_data["hardware"]["memory"]["value"]) + " " + str(
                    kvm_data["hardware"]["memory"]["unit"]) + " Ram**\n> **" + str(
                    kvm_data["hardware"]["disk"]["value"]) + " " + str(
                    kvm_data["hardware"]["disk"]["unit"]) + " Speicher**\n``🔌`` **IPv4**: " + str(
                    len(kvm_data["ip_address"]["ipv4"])) + "\n``🔌`` **IPv6**: " + str(
                    len(kvm_data["ip_address"]["ipv6"])),
                color=embed_color
            )
            view = ServiceLinkView(url_web_kvm + service_id[2])
        elif self.service == "domains":
            domain_request = await domainRequest(str(service_id[1]))
            if not domain_request["success"]:
                await interaction.response.edit_message(
                    content="``❌`` Fehler! Diese Domain konnte nicht gefunden werden.\n** **"
                )
                return

            for check in self.params:
                if str(check["name"]) == str(service_id[1]):
                    product = check

            domain_data = domain_request["data"]
            if product["status"] == "ACTIVE":
                status = "🟢"
            else:
                status = "🔴"

            services = discord.Embed(
                title="``" + emoji_domains + "`` Domain",
                description="``" + status + "`` **Domain**: " + str(domain_data["domain"]) + "\n``💡`` **TLD**: " + str(domain_data["tld"]) + "\n``🗒️`` **DNS Einträge**: " + str(len(domain_data["dns_entries"])),
                color=embed_color
            )
            view = ServiceLinkView(url_web_domain + str(domain_data["domain"]))
        elif self.service == "custom_products":
            for check in self.params:
                if str(check["id"]) == str(service_id[2]) and str(check["type"]) == service_id[1]:
                    product = check
            view = ServiceLinkView(url_web_custom + str(service_id[2]))

            if service_id[1] == "products":
                text = ""
                if "name" in product:
                    text = "``" + emoji_custom_products + "`` **Name**: " + str(product["name"]) + "\n"
                text += "``ℹ️`` **Info**: " + str(product["content"])

                services = discord.Embed(
                    title="``" + emoji_custom_products + "`` Produkt",
                    description=text,
                    color=embed_color
                )
            elif service_id[1] == "services":
                if product["status"] == "active":
                    status = "🟢"
                else:
                    status = "🔴"

                services = discord.Embed(
                    title="``" + emoji_custom_service + "`` Dienst",
                    description="``" + status + "`` **Name**: " + str(product["name"]),
                    color=embed_color
                )

        await interaction.response.edit_message(
            embed=services,
            view=view
        )


class ServiceLinkView(View):
    def __init__(self, service_url: str):
        super().__init__(timeout=None)

        self.add_item(ServiceLink(service_url))


class ServiceLink(Button):
    def __init__(self, service_url: str):
        super().__init__(
            label="Webinterface",
            url=service_url
        )

    async def callback(self, interaction: discord.Interaction):
        pass
