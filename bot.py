import discord
import os
from discord.ext import commands
from discord.ui import Button, View

# intents
intents = discord.Intents.default()
intents.message_content = True

# bot
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

# painel de venda
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
            "✅ Botão funcionando!\n\n🔒 Pagamento via PIX será integrado em breve.",
            ephemeral=True
        )

# comando do painel
@bot.command()
async def painel(ctx):
    await ctx.send("🛒 **Painel de Compras**", view=PainelVenda())

# comando teste
@bot.command()
async def teste(ctx):
    await ctx.send("FUNCIONOU ✅")

# iniciar bot (TOKEN VEM DO RAILWAY)
bot.run(os.getenv("DISCORD_TOKEN"))