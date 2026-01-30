import discord
from discord.ext import commands
from discord import ui
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

CARGO_STAFF = "Staff"  # nome exato do cargo da staff
CATEGORIA_TICKET = "Tickets"  # nome da categoria

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

# ================= BOTÃO =================

class TicketButton(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="🛒 Abrir Ticket", style=discord.ButtonStyle.green)
    async def abrir_ticket(self, interaction: discord.Interaction, button: ui.Button):
        guild = interaction.guild
        user = interaction.user

        categoria = discord.utils.get(guild.categories, name=CATEGORIA_TICKET)
        if categoria is None:
            categoria = await guild.create_category(CATEGORIA_TICKET)

        # verifica se já tem ticket
        for canal in categoria.channels:
            if canal.name == f"ticket-{user.id}":
                await interaction.response.send_message(
                    "❌ Você já tem um ticket aberto.", ephemeral=True
                )
                return

        staff_role = discord.utils.get(guild.roles, name=CARGO_STAFF)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True),
        }

        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True
            )

        canal = await guild.create_text_channel(
            name=f"ticket-{user.id}",
            category=categoria,
            overwrites=overwrites
        )

        await canal.send(
            f"🎫 **Ticket aberto!**\n\n"
            f"Olá {user.mention}, descreva seu pedido.\n"
            f"Um membro da staff irá te atender em breve."
        )

        await interaction.response.send_message(
            f"✅ Ticket criado: {canal.mention}", ephemeral=True
        )

# ================= COMANDOS =================

@bot.command()
async def painel(ctx):
    embed = discord.Embed(
        title="🛒 Painel de Atendimento",
        description="Clique no botão abaixo para abrir um ticket.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=TicketButton())

@bot.command()
async def teste(ctx):
    await ctx.send("✅ Bot funcionando!")

bot.run(os.getenv("DISCORD_TOKEN"))
