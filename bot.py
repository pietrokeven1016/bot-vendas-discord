import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ===============================
# CARRINHO (memória simples)
# ===============================
carrinhos = {}

produtos = {
    "1_mitica": {"nome": "1 Mítica Random", "preco": 2.89},
    "2_mitica": {"nome": "2 Míticas Random", "preco": 4.29},
    "3_mitica": {"nome": "3 Míticas Random", "preco": 6.99},
    "4_mitica": {"nome": "4 Míticas Random", "preco": 10.99},
    "5_mitica": {"nome": "5 Míticas Random", "preco": 13.99},
}

# ===============================
# SELECT DE PRODUTOS
# ===============================
class ProdutoSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label=produtos[p]["nome"],
                description=f"R$ {produtos[p]['preco']}",
                value=p
            )
            for p in produtos
        ]

        super().__init__(
            placeholder="Selecione um produto",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        produto = produtos[self.values[0]]

        if user_id not in carrinhos:
            carrinhos[user_id] = []

        carrinhos[user_id].append(produto)

        await interaction.response.send_message(
            f"✅ **{produto['nome']}** adicionado ao carrinho!",
            ephemeral=True
        )

# ===============================
# VIEW DO PAINEL
# ===============================
class PainelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ProdutoSelect())

    @discord.ui.button(label="🛒 Ver Carrinho", style=discord.ButtonStyle.primary)
    async def ver_carrinho(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        carrinho = carrinhos.get(user_id, [])

        if not carrinho:
            await interaction.response.send_message(
                "❌ Seu carrinho está vazio.",
                ephemeral=True
            )
            return

        total = sum(p["preco"] for p in carrinho)

        descricao = ""
        for p in carrinho:
            descricao += f"• {p['nome']} — R$ {p['preco']}\n"

        embed = discord.Embed(
            title="🛒 Seu Carrinho",
            description=descricao,
            color=0x9b59b6
        )
        embed.add_field(name="💰 Total", value=f"R$ {total:.2f}", inline=False)

        await interaction.response.send_message(
            embed=embed,
            view=CarrinhoView(),
            ephemeral=True
        )

# ===============================
# VIEW DO CARRINHO
# ===============================
class CarrinhoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="➕ Continuar comprando", style=discord.ButtonStyle.secondary)
    async def continuar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "🛍️ Use o menu novamente para adicionar mais produtos.",
            ephemeral=True
        )

    @discord.ui.button(label="💳 Ir para pagamento", style=discord.ButtonStyle.success)
    async def pagar(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        carrinho = carrinhos.get(user_id, [])

        total = sum(p["preco"] for p in carrinho)

        await interaction.response.send_message(
            f"💳 **Pagamento iniciado**\n"
            f"Total: **R$ {total:.2f}**\n\n"
            "📌 Envie o comprovante para a staff.",
            ephemeral=True
        )

# ===============================
# COMANDO PAINEL
# ===============================
@bot.command()
async def painel(ctx):
    embed = discord.Embed(
        title="KNZ STORE | MÍTICAS RANDOM",
        description=(
            "🌟 **TODAS POSSUEM:**\n"
            "👑 GodHuman desbloqueado\n"
            "🔥 Nível Máximo\n\n"
            "⬇️ Selecione um produto abaixo"
        ),
        color=0x9b59b6
    )

    await ctx.send(embed=embed, view=PainelView())

# ===============================
# BOT ONLINE
# ===============================
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

bot.run("SEU_TOKEN_AQUI")
