import discord
from discord.ext import commands
from discord import ui
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

CARGO_STAFF = "Staff"
CATEGORIA_TICKET = "Tickets"

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

# ================= BOTÕES E SELECT MENU =================

class TicketView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="🛒 Abrir Ticket", style=discord.ButtonStyle.green)
    async def abrir_ticket(self, interaction: discord.Interaction, button: ui.Button):
        guild = interaction.guild
        user = interaction.user

        categoria = discord.utils.get(guild.categories, name=CATEGORIA_TICKET)
        if categoria is None:
            categoria = await guild.create_category(CATEGORIA_TICKET)

        for canal in categoria.channels:
            if canal.name == f"ticket-{user.id}":
                await interaction.response.send_message(
                    "❌ Você já tem um ticket aberto.", ephemeral=True
                )
                return

        staff_role = discord.utils.get(guild.roles, name=CARGO_STAFF)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True),
        }

        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True
            )

        canal = await guild.create_text_channel(
            name=f"ticket-{user.id}",
            category=categoria,
            overwrites=overwrites
        )

        # Select Menu para escolher conta
        class SelecionarContaView(ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.add_item(ui.StringSelect(
                    placeholder="Selecione a opção de conta desejada",
                    options=[
                        discord.SelectOption(label="1 mítica aleatória", value="1_mitica"),
                        discord.SelectOption(label="2 míticas aleatórias", value="2_miticas"),
                        discord.SelectOption(label="3 míticas aleatórias", value="3_miticas")
                    ],
                    custom_id="selecionar_conta"
                ))

            @ui.select(custom_id="selecionar_conta")
            async def select_callback(self, select_interaction: discord.Interaction, select):
                escolha = select.values[0]
                await select_interaction.response.send_message(
                    f"✅ Você selecionou: **{escolha.replace('_', ' ')}**",
                    ephemeral=True
                )
                # Aqui você pode chamar sua função para entregar a conta
                # entregar_conta(select_interaction.user.id, escolha)

        await canal.send(
            f"🎫 **Ticket aberto!**\n\n"
            f"{user.mention}, descreva seu pedido ou selecione sua conta abaixo:",
            view=FecharTicketView() + SelecionarContaView()
        )

        await interaction.response.send_message(
            f"✅ Ticket criado: {canal.mention}", ephemeral=True
        )

class FecharTicketView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="🔒 Fechar Ticket", style=discord.ButtonStyle.red)
    async def fechar_ticket(self, interaction: discord.Interaction, button: ui.Button):
        staff_role = discord.utils.get(interaction.guild.roles, name=CARGO_STAFF)

        if staff_role not in interaction.user.roles:
            await interaction.response.send_message(
                "❌ Apenas a **staff** pode fechar o ticket.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "🔒 Ticket será fechado em 3 segundos...",
            ephemeral=True
        )

        await interaction.channel.delete()

# ================= COMANDOS =================

@bot.command()
async def painel(ctx):
    embed = discord.Embed(
        title="🛒 Painel de Atendimento",
        description="Clique no botão abaixo para abrir um ticket.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=TicketView())

@bot.command()
async def teste(ctx):
    await ctx.send("✅ Bot funcionando!")

bot.run(os.getenv("DISCORD_TOKEN"))
