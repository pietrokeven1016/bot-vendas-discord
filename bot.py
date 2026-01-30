import discord
from discord.ext import commands
from discord.ui import Button, View
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

# ===== PAINEL DE VENDAS =====

class PainelVenda(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(
            label="💰 Comprar Conta",
            style=discord.ButtonStyle.green,
            custom_id="comprar_conta"
        ))

@bot.command()
async def painel(ctx):
    embed = discord.Embed(
        title="🛒 Loja Oficial - Blox Fruits",
        description=(
            "**📦 Produto:** Conta de Blox Fruits\n"
            "**💵 Preço:** R$ XX,XX\n"
            "**⚡ Entrega:** Automática após pagamento\n\n"
            "Clique no botão abaixo para iniciar a compra 👇"
        ),
        color=discord.Color.green()
    )

    embed.set_footer(text="Mkz Store • Compra segura")

    await ctx.send(embed=embed, view=PainelVenda())

# ===== INTERAÇÃO DO BOTÃO =====

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        if interaction.data["custom_id"] == "comprar_conta":
            await interaction.response.send_message(
                "✅ Pedido iniciado!\n\n"
                "💳 O pagamento via **PIX** será o próximo passo.\n"
                "_(Mercado Pago em breve)_",
                ephemeral=True
            )

bot.run(os.getenv("DISCORD_TOKEN"))
