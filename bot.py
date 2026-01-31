import discord
from discord.ext import commands
from discord import ui
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

CARGO_STAFF = "Staff"
CATEGORIA_TICKET = "Tickets"

# ================= BOTÃO PARA ABRIR TICKET =================
class TicketView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ui.Button(label="🛒 Abrir Ticket", style=discord.ButtonStyle.green, custom_id="abrir_ticket"))

# ================= TICKET COMPLETO (FECHAR + SELECT MENU) =================
class TicketCompletoView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        # Botão de fechar
        self.add_item(ui.Button(label="🔒 Fechar Ticket", style=discord.ButtonStyle.red, custom_id="fechar_ticket"))

        # Select Menu
        options = [
            discord.SelectOption(label="1 MÍTICA RANDOM", value="1_mitica"),
            discord.SelectOption(label="2 MÍTICAS RANDOM", value="2_miticas"),
            discord.SelectOption(label="3 MÍTICAS RANDOM", value="3_miticas"),
        ]
        self.add_item(ui.Select(placeholder="Selecione a opção de conta desejada", options=options, custom_id="selecionar_conta"))

# ================= EVENTO DE INTERAÇÃO =================
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.component:
        return

    # ----------------- ABRIR TICKET -----------------
    if interaction.data["custom_id"] == "abrir_ticket":
        guild = interaction.guild
        user = interaction.user

        categoria = discord.utils.get(guild.categories, name=CATEGORIA_TICKET)
        if categoria is None:
            categoria = await guild.create_category(CATEGORIA_TICKET)

        for canal in categoria.channels:
            if canal.name == f"ticket-{user.id}":
                await interaction.response.send_message("❌ Você já tem um ticket aberto.", ephemeral=True)
                return

        staff_role = discord.utils.get(guild.roles, name=CARGO_STAFF)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True),
        }

        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        canal = await guild.create_text_channel(
            name=f"ticket-{user.id}",
            category=categoria,
            overwrites=overwrites
        )

        await canal.send(
            f"🎫 **Ticket aberto!**\n\n{user.mention}, descreva seu pedido ou selecione sua conta abaixo:",
            view=TicketCompletoView()
        )

        await interaction.response.send_message(f"✅ Ticket criado: {canal.mention}", ephemeral=True)

    # ----------------- FECHAR TICKET -----------------
    elif interaction.data["custom_id"] == "fechar_ticket":
        staff_role = discord.utils.get(interaction.guild.roles, name=CARGO_STAFF)
        if staff_role not in interaction.user.roles:
            await interaction.response.send_message("❌ Apenas a **staff** pode fechar o ticket.", ephemeral=True)
            return
        await interaction.response.send_message("🔒 Ticket será fechado...", ephemeral=True)
        await interaction.channel.delete()

    # ----------------- SELECT MENU -----------------
    elif interaction.data["custom_id"] == "selecionar_conta":
        escolha = interaction.data["values"][0]

        # Dados de cada opção
        dados_contas = {
            "1_mitica": {"nome": "1 MÍTICA RANDOM", "valor": "R$2.40", "estoque": 1, "icone": "https://tiermaker.com/images/media/hero_images/2024/17709405/blox-fruits-tier-list--dragon-rework-holiday-update-17709405/177094051735169387.jpg"},
            "2_miticas": {"nome": "2 MÍTICAS RANDOM", "valor": "R$3.60", "estoque": 0, "icone": "https://tiermaker.com/images/media/hero_images/2024/17709405/blox-fruits-tier-list--dragon-rework-holiday-update-17709405/177094051735169387.jpg"},
            "3_miticas": {"nome": "3 MÍTICAS RANDOM", "valor": "R$5.00", "estoque": 0, "icone": "https://tiermaker.com/images/media/hero_images/2024/17709405/blox-fruits-tier-list--dragon-rework-holiday-update-17709405/177094051735169387.jpg"},
        }

        conta = dados_contas[escolha]

        embed = discord.Embed(title=conta["nome"], color=discord.Color.green())
        embed.add_field(name="💰 Valor", value=conta["valor"], inline=True)
        embed.add_field(name="📦 Estoque", value=str(conta["estoque"]), inline=True)
        embed.set_thumbnail(url=conta["icone"])

        await interaction.response.send_message(embed=embed, ephemeral=True)

# ================= COMANDOS =================
@bot.command()
async def painel(ctx):
    embed = discord.Embed(
        title="🛒 Painel de Atendimento",
        description="Clique no botão abaixo para abrir um ticket.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=TicketView())

@bot.command()
async def teste(ctx):
    await ctx.send("✅ Bot funcionando!")

bot.run(os.getenv("DISCORD_TOKEN"))


