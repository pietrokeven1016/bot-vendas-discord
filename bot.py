import discord
from discord.ext import commands
from discord.ui import Button, View
import os

# ===== CONFIGURAÇÕES =====

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ===== EVENTO DE INICIALIZAÇÃO =====

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

# ===== PAINEL DE VENDAS =====

class PainelVenda(View):
    def __init__(self):
        super().__init__(timeout=None)

        botao = Button(
            label="💰 Comprar Conta",
            style=discord.ButtonStyle.green
        )

        botao.callback = self.comprar
        self.add_item(botao)

    async def comprar(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "✅ **Pedido iniciado com sucesso!**\n\n"
            "💳 Pagamento via **PIX** será o próximo passo.\n"
            "_Mercado Pago será integrado em breve._",
            ephemeral=True
        )

# ===== COMANDO DO PAINEL =====

@bot.command()
async def painel(ctx):
    embed = discord.Embed(
        title="🛒 Loja Oficial - Blox Fruits",
        description=(
            "**📦 Produto:** Conta de Blox Fruits\n"
            "**💵 Preço:** R$ XX,XX\n"
            "**⚡ Entrega:** Automática após pagamento\n\n"
            "Clique no botão abaixo para comprar 👇"
        ),
        color=discord.Color.green()
    )

    embed.set_footer(text="Mkz Store • Compra segura")

    await ctx.send(embed=embed, view=PainelVenda())

# ===== INICIAR BOT =====

bot.run(os.getenv("DISCORD_TOKEN"))
