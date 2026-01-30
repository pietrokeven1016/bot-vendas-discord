import os
import discord
from discord.ext import commands
from discord.ui import View, Button

# ================= CONFIG =================
STAFF_ROLE_ID = 123456789012345678   # ID do cargo staff
CATEGORY_TICKET_ID = 123456789012345678  # ID da categoria dos tickets
# =========================================

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("TOKEN NÃO CARREGADO")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================= EVENTS =================
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

# ================= VIEWS =================
class PainelTicket(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(
            label="🎟️ Abrir Ticket",
            style=discord.ButtonStyle.green,
            custom_id="abrir_ticket"
        ))

class FecharTicket(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(
            label="🔒 Fechar Ticket",
            style=discord.ButtonStyle.red,
            custom_id="fechar_ticket"
        ))

# ================= COMMAND =================
@bot.command()
async def painel(ctx):
    embed = discord.Embed(
        title="🎫 Central de Atendimento",
        description="Clique no botão abaixo para abrir um ticket",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=PainelTicket())

# ================= INTERACTIONS =================
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.component:
        return

    custom_id = interaction.data["custom_id"]
    guild = interaction.guild
    user = interaction.user

    # ===== ABRIR TICKET =====
    if custom_id == "abrir_ticket":
        category = guild.get_channel(CATEGORY_TICKET_ID)

        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            category=category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                guild.get_role(STAFF_ROLE_ID): discord.PermissionOverwrite(view_channel=True)
            }
        )

        await channel.send(
            f"🎫 Ticket de {user.mention}\nExplique seu problema abaixo.",
            view=FecharTicket()
        )

        await interaction.response.send_message(
            f"✅ Ticket criado: {channel.mention}",
            ephemeral=True
        )

    # ===== FECHAR TICKET =====
    if custom_id == "fechar_ticket":
        staff_role = guild.get_role(STAFF_ROLE_ID)

        if staff_role not in user.roles:
            await interaction.response.send_message(
                "❌ Apenas a staff pode fechar tickets.",
                ephemeral=True
            )
            return

        await interaction.channel.delete()

# ================= START =================
bot.run(TOKEN)
