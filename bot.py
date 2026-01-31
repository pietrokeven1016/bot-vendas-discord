import os
import discord
from discord.ext import commands
from discord import app_commands

# Pegando o token e o ID do cargo do Replit (variáveis de ambiente)
TOKEN = os.environ["DISCORD_TOKEN"]
STAFF_ROLE_ID = int(os.environ["STAFF_ROLE_ID"])  # importante converter para int

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # necessário para pegar cargos dos membros

bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------
# Função para criar ticket (exemplo)
# -------------------
@bot.command()
async def ticket(ctx):
    embed = discord.Embed(
        title="Ticket",
        description="Clique no botão para abrir um ticket!",
        color=discord.Color.blue()
    )
    button = discord.ui.Button(label="Fechar Ticket", style=discord.ButtonStyle.red)

    async def button_callback(interaction):
        # Verifica se quem clicou tem o cargo de staff
        if STAFF_ROLE_ID not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message("Você não é staff!", ephemeral=True)
            return

        # Fecha o ticket (apaga a mensagem ou o canal)
        await interaction.channel.delete()
    
    button.callback = button_callback
    view = discord.ui.View()
    view.add_item(button)
    
    await ctx.send(embed=embed, view=view)

# -------------------
# Start do bot
# -------------------
bot.run(TOKEN)
