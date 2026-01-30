import discord
from discord.ext import commands
import os

# =========================
# CONFIGURAÇÕES (IDs)
# =========================

TOKEN = os.getenv("DISCORD_TOKEN")  # coloque no painel de variáveis do host

CATEGORY_TICKET_ID = 123456789012345678  # ID da categoria de tickets
STAFF_ROLE_ID = 123456789012345678       # ID do cargo da staff

# =========================
# BOT
# =========================

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# EVENTOS
# =========================

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

# =========================
# COMANDOS
# =========================

@bot.command()
async def teste(ctx):
    await ctx.send("✅ Bot está funcionando!")

@bot.command()
async def painel(ctx):
    embed = discord.Embed(
        title="🛒 Central de Atendimento",
        description="Clique no botão abaixo para abrir um ticket",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=PainelView())

# =========================
# VIEW DO PAINEL
# =========================

class PainelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="📩 Abrir Ticket",
        style=discord.ButtonStyle.green,
        custom_id="abrir_ticket"
    )
    async def abrir_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        categoria = guild.get_channel(CATEGORY_TICKET_ID)
        staff_role = guild.get_role(STAFF_ROLE_ID)

        if categoria is None or staff_role is None:
            await interaction.followup.send(
                "❌ Categoria ou cargo da staff não encontrado.",
                ephemeral=True
            )
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=categoria,
            overwrites=overwrites
        )

        await interaction.followup.send(
            f"✅ Ticket criado: {channel.mention}",
            ephemeral=True
        )

        await channel.send(
            f"🎟️ Ticket aberto por {interaction.user.mention}",
            view=FecharTicketView()
        )

# =========================
# VIEW DE FECHAR TICKET
# =========================

class FecharTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🔒 Fechar Ticket",
        style=discord.ButtonStyle.red,
        custom_id="fechar_ticket"
    )
    async def fechar_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)

        if staff_role not in interaction.user.roles:
            await interaction.response.send_message(
                "❌ Apenas a staff pode fechar este ticket.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "⛔ Ticket será fechado em 5 segundos...",
            ephemeral=True
        )

        await interaction.channel.delete(delay=5)

# =========================
# START
# =========================

bot.run(TOKEN)
