import discord
from discord.ext import commands
import os

# ===== CONFIG =====
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ===== EVENTOS =====
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

# ===== COMANDO TESTE =====
@bot.command()
async def teste(ctx):
    await ctx.send("✅ Bot funcionando!")

# ===== VIEW DO PAINEL =====
class PainelVenda(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🛒 Comprar",
        style=discord.ButtonStyle.green,
        custom_id="comprar"
    )
    async def comprar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "🛍️ Pedido recebido! Em breve alguém irá te atender.",
            ephemeral=True
        )

# ===== COMANDO PAINEL =====
@bot.command()
async def painelvendas(ctx):
    embed = discord.Embed(
        title="🛍️ Painel de Vendas",
        description="Clique no botão abaixo para comprar.",
        color=discord.Color.green()
    )
    embed.set_footer(text="Mkz Store")

    await ctx.send(embed=embed, view=PainelVenda())

# ===== START =====
bot.run(os.getenv("DISCORD_TOKEN"))
