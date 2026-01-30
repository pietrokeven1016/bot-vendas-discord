import discord
from discord.ext import commands

# ========= CONFIGURAÇÕES =========

TOKEN = "COLE_AQUI_O_TOKEN_DO_BOT"

PREFIXO = "!"

CARGO_STAFF_ID = 123456789012345678  # ID do cargo da staff
CATEGORIA_TICKET_ID = 123456789012345678  # ID da categoria onde os tickets vão ser criados

# =================================

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIXO, intents=intents)

# ========= EVENTOS =========

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

# ========= BOTÃO =========

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Abrir Ticket", style=discord.ButtonStyle.green, custom_id="abrir_ticket")
    async def abrir_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        member = interaction.user

        staff_role = guild.get_role(CARGO_STAFF_ID)
        categoria = guild.get_channel(CATEGORIA_TICKET_ID)

        if staff_role is None or categoria is None:
            await interaction.response.send_message(
                "❌ Cargo da staff ou categoria não encontrada.",
                ephemeral=True
            )
            return

        # Cria o canal
        canal = await guild.create_text_channel(
            name=f"ticket-{member.name}",
            category=categoria,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                staff_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
        )

        await canal.send(
            f"🎟️ Ticket criado por {member.mention}\n"
            f"🔧 Staff: {staff_role.mention}"
        )

        await interaction.response.send_message(
            f"✅ Ticket criado: {canal.mention}",
            ephemeral=True
        )

# ========= COMANDOS =========

@bot.command()
async def painel(ctx):
    embed = discord.Embed(
        title="Central de Atendimento",
        description="Clique no botão abaixo para abrir um ticket.",
        color=discord.Color.green()
    )

    await ctx.send(embed=embed, view=TicketView())

# ========= INICIAR =========

bot.run(TOKEN)
