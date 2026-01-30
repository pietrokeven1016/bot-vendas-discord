import discord
from discord.ext import commands
from discord import app_commands

# ========= CONFIGURAÇÕES (MUDE SOMENTE AQUI) =========
TOKEN = "COLE_SEU_TOKEN_DO_BOT_AQUI"

STAFF_ROLE_ID = 123456789012345678   # ID do cargo STAFF
TICKET_CATEGORY_ID = 123456789012345678  # ID da categoria dos tickets
# ====================================================

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ================= EVENTOS =================
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands sincronizados: {len(synced)}")
    except Exception as e:
        print(e)


# ================= BOTÃO ABRIR TICKET =================
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎟️ Abrir Ticket", style=discord.ButtonStyle.green, custom_id="abrir_ticket")
    async def abrir_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        member = interaction.user

        staff_role = guild.get_role(STAFF_ROLE_ID)
        category = guild.get_channel(TICKET_CATEGORY_ID)

        if staff_role is None or category is None:
            await interaction.response.send_message(
                "❌ Categoria ou cargo da staff não encontrado.",
                ephemeral=True
            )
            return

        # Verifica se já existe ticket
        for channel in category.text_channels:
            if channel.name == f"ticket-{member.id}":
                await interaction.response.send_message(
                    f"❌ Você já tem um ticket aberto: {channel.mention}",
                    ephemeral=True
                )
                return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{member.id}",
            category=category,
            overwrites=overwrites
        )

        await channel.send(
            f"🎟️ Ticket aberto por {member.mention}\n"
            f"Aguarde um staff.",
            view=CloseTicketView()
        )

        await interaction.response.send_message(
            f"✅ Ticket criado: {channel.mention}",
            ephemeral=True
        )


# ================= BOTÃO FECHAR TICKET =================
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Fechar Ticket", style=discord.ButtonStyle.red, custom_id="fechar_ticket")
    async def fechar_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        member = interaction.user
        staff_role = guild.get_role(STAFF_ROLE_ID)

        if staff_role not in member.roles:
            await interaction.response.send_message(
                "❌ Apenas a staff pode fechar este ticket.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "🔒 Ticket será fechado em 5 segundos..."
        )

        await interaction.channel.delete(delay=5)


# ================= COMANDO PAINEL =================
@bot.command()
async def painel(ctx):
    embed = discord.Embed(
        title="🎟️ Sistema de Tickets",
        description="Clique no botão abaixo para abrir um ticket.",
        color=0x2ecc71
    )

    await ctx.send(embed=embed, view=TicketView())


# ================= START =================
bot.run(TOKEN)
