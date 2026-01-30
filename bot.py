import os
import discord
from discord.ext import commands
from discord.ui import Button, View

# intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =====================
# EVENTO ON READY
# =====================
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

# =====================
# COMANDO TESTE
# =====================
@bot.command()
async def teste(ctx):
    await ctx.send("✅ Bot está funcionando!")

# =====================
# VIEW DO PAINEL
# =====================
class PainelVenda(View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(
            Button(
                label="💰 Comprar Conta",
                style=discord.ButtonStyle.green,
                custom_id="comprar_conta"
            )
        )

# =====================
# COMANDO PAINEL (NOME NOVO)
# =====================
@bot.command()
async def painelvendas(ctx):
    embed = discord.Embed(
        title="🛒 Painel de Compras",
        description="Clique no botão abaixo para comprar.",
        color=discord.Color.green()
    )

    await ctx.send(embed=embed, view=PainelVenda())

# =====================
# INTERAÇÃO DO BOTÃO
# =====================
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        if interaction.data.get("custom_id") == "comprar_conta":
            await interaction.response.send_message(
                "✅ Botão funcionando! (PIX entra depois)",
                ephemeral=True
            )

# =====================
# START DO BOT
# =====================
TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:
    raise ValueError("❌ DISCORD_TOKEN não encontrado nas variáveis de ambiente")

bot.run(TOKEN)
