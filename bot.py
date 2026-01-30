import discord
from discord.ext import commands
import os

# ===== INTENTS (OBRIGATÓRIO) =====
intents = discord.Intents.default()
intents.message_content = True  # ESSENCIAL

bot = commands.Bot(command_prefix="!", intents=intents)


# ===== EVENTO DE INICIALIZAÇÃO =====
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")


# ===== EVENTO PARA COMANDOS FUNCIONAREM =====
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Log para debug
    print(f"Mensagem recebida: {message.content}")

    await bot.process_commands(message)


# ===== COMANDO TESTE =====
@bot.command()
async def teste(ctx):
    await ctx.send("✅ Bot está respondendo!")


# ===== COMANDO PAINEL =====
@bot.command()
async def painel(ctx):
    embed = discord.Embed(
        title="🛒 Painel de Vendas",
        description="Painel funcionando corretamente!",
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)


# ===== INICIAR BOT =====
token = os.getenv("DISCORD_TOKEN")

if not token:
    raise ValueError("❌ DISCORD_TOKEN não encontrado nas variáveis de ambiente")

bot.run(token)
