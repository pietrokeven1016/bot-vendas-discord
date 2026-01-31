import os
import discord
from discord.ext import commands

# -------------------
# Pegando variáveis do Replit/Raiwail
# -------------------
try:
    TOKEN = os.environ["DISCORD_TOKEN"]
except KeyError:
    raise Exception("❌ Variável de ambiente DISCORD_TOKEN não encontrada!")

try:
    STAFF_ROLE_ID = int(os.environ["STAFF_ROLE_ID"])
except KeyError:
    raise Exception("❌ Variável de ambiente STAFF_ROLE_ID não encontrada!")

# -------------------
# Intents
# -------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # necessário para pegar cargos

bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------
# Evento on_ready
# -------------------
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

# -------------------
# Comando para criar ticket
# -------------------
@bot.command()
async def ticket(ctx):
    embed = discord.Embed(
        title="Ticket",
        description="Clique no botão para abrir um ticket!",
        color=discord.Color.blue()
    )

    button = discord.ui.Button(label="Fechar Ticket", style=discord.ButtonStyle.red)

    async def button_callback(interaction: discord.Interaction):
        # Verifica se quem clicou tem o cargo staff
        if STAFF_ROLE_ID not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message("Você não é staff!", ephemeral=True)
            return

        # Fecha o ticket (apaga o canal onde o ticket foi aberto)
        await interaction.channel.delete()

    button.callback = button_callback
    view = discord.ui.View()
    view.add_item(button)

    await ctx.send(embed=embed, view=view)

# -------------------
# Comando de teste
# -------------------
@bot.command()
async def teste(ctx):
    await ctx.send("✅ Comando teste funcionando!")

# -------------------
# Start do bot
# -------------------
bot.run(TOKEN)
