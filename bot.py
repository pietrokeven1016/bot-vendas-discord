import discord
from discord.ext import commands
import logging

# ================= LOGS =================
logging.basicConfig(level=logging.INFO)

# ================= CONFIG =================
TOKEN = "SEU_TOKEN_AQUI"

CARGO_STAFF_ID = 123456789012345678  # ID do cargo staff
CATEGORIA_TICKET_ID = 123456789012345678  # ID da categoria dos tickets

# ================= BOT =================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================= CARRINHO =================
carrinhos = {}

produtos = {
    "1 Mitica Random": 2.89,
    "2 Miticas Random": 4.29,
    "3 Miticas Random": 6.99,
    "4 Miticas Random": 10.99,
    "5 Miticas Random": 13.99,
}

# ================= VIEWS =================
class PainelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Selecione um produto",
        options=[
            discord.SelectOption(label=nome, description=f"R$ {preco}")
            for nome, preco in produtos.items()
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        try:
            user_id = interaction.user.id
            carrinhos.setdefault(user_id, [])
            carrinhos[user_id].append(select.values[0])

            await interaction.response.send_message(
                f"✅ **{select.values[0]}** adicionado ao carrinho!",
                view=CarrinhoView(),
                ephemeral=True
            )
        except Exception as e:
            print("ERRO SELECT:", e)

class CarrinhoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🛒 Ver carrinho", style=discord.ButtonStyle.secondary)
    async def ver(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            itens = carrinhos.get(interaction.user.id, [])
            if not itens:
                await interaction.response.send_message("Carrinho vazio.", ephemeral=True)
                return

            total = sum(produtos[i] for i in itens)
            texto = "\n".join(itens)

            await interaction.response.send_message(
                f"🛒 **Carrinho:**\n{texto}\n\n💰 Total: **R$ {total:.2f}**",
                ephemeral=True
            )
        except Exception as e:
            print("ERRO CARRINHO:", e)

    @discord.ui.button(label="💳 Finalizar compra", style=discord.ButtonStyle.success)
    async def pagar(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            guild = interaction.guild
            categoria = guild.get_channel(CATEGORIA_TICKET_ID)

            canal = await guild.create_text_channel(
                name=f"ticket-{interaction.user.name}",
                category=categoria
            )

            await canal.set_permissions(interaction.user, read_messages=True, send_messages=True)
            await canal.set_permissions(guild.default_role, read_messages=False)

            embed = discord.Embed(
                title="🧾 Ticket de Compra",
                description="Um staff irá te atender.",
                color=discord.Color.green()
            )

            await canal.send(
                content=f"{interaction.user.mention}",
                embed=embed,
                view=FecharTicketView()
            )

            await interaction.response.send_message(
                f"🎫 Ticket criado: {canal.mention}",
                ephemeral=True
            )
        except Exception as e:
            print("ERRO PAGAMENTO:", e)

class FecharTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Fechar ticket", style=discord.ButtonStyle.danger)
    async def fechar(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            cargo = interaction.guild.get_role(CARGO_STAFF_ID)

            if cargo not in interaction.user.roles:
                await interaction.response.send_message(
                    "❌ Apenas staff pode fechar o ticket.",
                    ephemeral=True
                )
                return

            await interaction.channel.delete()
        except Exception as e:
            print("ERRO FECHAR TICKET:", e)

# ================= COMANDOS =================
@bot.command()
async def painel(ctx):
    embed = discord.Embed(
        title="KNZ STORE | MITICAS RANDOM",
        description="Selecione um produto abaixo",
        color=discord.Color.purple()
    )

    await ctx.send(embed=embed, view=PainelView())

@bot.command()
async def teste(ctx):
    await ctx.send("✅ Bot funcionando!")

# ================= READY =================
@bot.event
async def on_ready():
    bot.add_view(PainelView())
    bot.add_view(CarrinhoView())
    bot.add_view(FecharTicketView())
    print(f"Bot conectado como {bot.user}")

# ================= RUN =================
bot.run(TOKEN)
