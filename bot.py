import discord
from discord.ext import commands

TOKEN = "SEU_TOKEN_AQUI"

GUILD_ID = 123456789012345678      # ID do servidor
CATEGORY_ID = 123456789012345678   # ID da categoria dos tickets
STAFF_ROLE_ID = 123456789012345678 # ID do cargo staff

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")


# 🔘 BOTÃO DO TICKET
class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="📩 Abrir Ticket",
        style=discord.ButtonStyle.green,
        custom_id="abrir_ticket"
    )
    async def abrir_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        member = interaction.member

        # 🔒 VERIFICA CARGO STAFF
        if STAFF_ROLE_ID not in [role.id for role in member.roles]:
            await interaction.response.send_message(
                "❌ Você não tem o cargo necessário para abrir ticket.",
                ephemeral=True
            )
            return

        category = guild.get_channel(CATEGORY_ID)
        if category is None:
            await interaction.response.send_message(
                "❌ Categoria de tickets não encontrada.",
                ephemeral=True
            )
            return

        # 🆕 CRIA CANAL
        channel = await guild.create_text_channel(
            name=f"ticket-{member.name}",
            category=category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                member: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                guild.get_role(STAFF_ROLE_ID): discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True
                )
            }
        )

        await interaction.response.send_message(
            f"✅ Ticket criado: {channel.mention}",
            ephemeral=True
        )

        await channel.send(
            f"🎫 **Ticket aberto por {member.mention}**\n"
            "Explique seu problema e aguarde um staff."
        )


# 📌 COMANDO DO PAINEL
@bot.command()
@commands.has_permissions(administrator=True)
async def painel(ctx):
    embed = discord.Embed(
        title="🎟️ Central de Atendimento",
        description="Clique no botão abaixo para abrir um ticket.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=TicketButton())


bot.run(TOKEN)
