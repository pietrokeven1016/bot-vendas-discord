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

# ================= DADOS DAS CONTAS =================
DADOS_CONTAS = {
    "1_mitica": {"nome": "1 MÍTICA RANDOM", "valor": "2.40", "estoque": 5, "login": "usuario1", "senha": "senha123"},
    "2_miticas": {"nome": "2 MÍTICAS RANDOM", "valor": "3.60", "estoque": 3, "login": "usuario2", "senha": "senhaabc"},
    "3_miticas": {"nome": "3 MÍTICAS RANDOM", "valor": "5.00", "estoque": 2, "login": "usuario3", "senha": "senhaxyz"},
    "4_miticas": {"nome": "4 MÍTICAS RANDOM", "valor": "7.00", "estoque": 1, "login": "usuario4", "senha": "senha987"}
}

# ================= CARRINHOS =================
CARRINHOS = {}  # chave: user.id, valor: lista de itens

# ================= VIEWS =================
class TicketView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ui.Button(label="🛒 Abrir Ticket", style=discord.ButtonStyle.green, custom_id="abrir_ticket"))

class TicketCompletoView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ui.Button(label="🔒 Fechar Ticket", style=discord.ButtonStyle.red, custom_id="fechar_ticket"))
        options = [
            discord.SelectOption(label="1 MÍTICA RANDOM", value="1_mitica"),
            discord.SelectOption(label="2 MÍTICAS RANDOM", value="2_miticas"),
            discord.SelectOption(label="3 MÍTICAS RANDOM", value="3_miticas"),
            discord.SelectOption(label="4 MÍTICAS RANDOM", value="4_miticas"),
        ]
        self.add_item(ui.Select(placeholder="Selecione a opção de conta desejada", options=options, custom_id="selecionar_conta"))

class CarrinhoView(ui.View):
    def __init__(self, cliente_id):
        super().__init__(timeout=None)
        self.cliente_id = cliente_id
        self.add_item(ui.Button(label="🗑 Cancelar", style=discord.ButtonStyle.red, custom_id=f"carrinho_cancelar_{cliente_id}"))
        self.add_item(ui.Button(label="💳 Ir para Pagamento", style=discord.ButtonStyle.green, custom_id=f"carrinho_pagamento_{cliente_id}"))

class PagamentoView(ui.View):
    def __init__(self, cliente_id):
        super().__init__(timeout=None)
        self.cliente_id = cliente_id
        self.add_item(ui.Button(label="🪙 Gerar QR Code", style=discord.ButtonStyle.green, custom_id=f"gerar_qr_{cliente_id}"))
        self.add_item(ui.Button(label="✅ Confirmar Pagamento (Staff)", style=discord.ButtonStyle.blurple, custom_id=f"confirmar_pagamento_{cliente_id}"))

# ================= EVENTO DE INTERAÇÃO =================
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.component:
        return

    # ----------------- ABRIR TICKET -----------------
    if interaction.data["custom_id"] == "abrir_ticket":
        guild = interaction.guild
        user = interaction.user
        categoria = discord.utils.get(guild.categories, name=CATEGORIA_TICKET)
        if categoria is None:
            categoria = await guild.create_category(CATEGORIA_TICKET)

        for canal in categoria.channels:
            if canal.name == f"ticket-{user.id}":
                await interaction.response.send_message("❌ Você já tem um ticket aberto.", ephemeral=True)
                return

        staff_role = discord.utils.get(guild.roles, name=CARGO_STAFF)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True),
        }
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        canal = await guild.create_text_channel(name=f"ticket-{user.id}", category=categoria, overwrites=overwrites)
        await canal.send(f"🎫 **Ticket aberto!**\n\n{user.mention}, selecione sua conta abaixo:", view=TicketCompletoView())
        await interaction.response.send_message(f"✅ Ticket criado: {canal.mention}", ephemeral=True)

    # ----------------- FECHAR TICKET -----------------
    elif interaction.data["custom_id"] == "fechar_ticket":
        staff_role = discord.utils.get(interaction.guild.roles, name=CARGO_STAFF)
        if staff_role not in interaction.user.roles:
            await interaction.response.send_message("❌ Apenas a staff pode fechar o ticket.", ephemeral=True)
            return
        await interaction.response.send_message("🔒 Ticket será fechado...", ephemeral=True)
        await interaction.channel.delete()

    # ----------------- SELECT MENU -----------------
    elif interaction.data["custom_id"] == "selecionar_conta":
        cliente_id = interaction.user.id
        escolha = interaction.data["values"][0]
        conta = DADOS_CONTAS.get(escolha)
        if conta is None:
            await interaction.response.send_message("❌ Opção inválida.", ephemeral=True)
            return
        if conta["estoque"] == 0:
            await interaction.response.send_message("❌ Esta opção está sem estoque no momento.", ephemeral=True)
            return

        if cliente_id not in CARRINHOS:
            CARRINHOS[cliente_id] = []
        CARRINHOS[cliente_id].append(conta)

        embed = discord.Embed(
            title=f"{conta['nome']} adicionado ao carrinho!",
            description=f"💰 Valor: R${conta['valor']}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, view=CarrinhoView(cliente_id), ephemeral=True)

        # ---------------- NOTIFICAR STAFF ----------------
        staff_channel = discord.utils.get(interaction.guild.text_channels, name="staff-pedidos")
        if staff_channel:
            embed_staff = discord.Embed(
                title="🛒 Novo pedido!",
                description=f"Cliente: {interaction.user.mention}\nItem: {conta['nome']}\nValor: R${conta['valor']}",
                color=discord.Color.blurple()
            )
            await staff_channel.send(embed=embed_staff, view=PagamentoView(cliente_id))

    # ----------------- CANCELAR ITEM -----------------
    elif interaction.data["custom_id"].startswith("carrinho_cancelar_"):
        cliente_id = int(interaction.data["custom_id"].split("_")[-1])
        carrinho = CARRINHOS.get(cliente_id, [])
        if not carrinho:
            await interaction.response.send_message("❌ Carrinho já está vazio.", ephemeral=True)
            return
        item_removido = carrinho.pop()
        await interaction.response.send_message(f"🗑 {item_removido['nome']} removido do carrinho.", ephemeral=True)

    # ----------------- IR PARA PAGAMENTO -----------------
    elif interaction.data["custom_id"].startswith("carrinho_pagamento_"):
        cliente_id = int(interaction.data["custom_id"].split("_")[-1])
        carrinho = CARRINHOS.get(cliente_id, [])
        if not carrinho:
            await interaction.response.send_message("❌ Carrinho vazio.", ephemeral=True)
            return
        total = sum(float(item['valor']) for item in carrinho)
        embed = discord.Embed(
            title="💳 Pagamento",
            description=f"Total: **R${total:.2f}**\nClique em Gerar QR Code para Pix ou peça a confirmação à staff.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, view=PagamentoView(cliente_id), ephemeral=True)

    # ----------------- GERAR QR PIX -----------------
    elif interaction.data["custom_id"].startswith("gerar_qr_"):
        cliente_id = int(interaction.data["custom_id"].split("_")[-1])
        carrinho = CARRINHOS.get(cliente_id, [])
        if not carrinho:
            await interaction.response.send_message("❌ Carrinho vazio.", ephemeral=True)
            return

        ultimo_item = carrinho[-1]
        qr_file = ""
        if ultimo_item['nome'] == "1 MÍTICA RANDOM":
            qr_file = "pix_1.png"
        elif ultimo_item['nome'] == "2 MÍTICAS RANDOM":
            qr_file = "pix_2.png"
        elif ultimo_item['nome'] == "3 MÍTICAS RANDOM":
            qr_file = "pix_3.png"
        elif ultimo_item['nome'] == "4 MÍTICAS RANDOM":
            qr_file = "pix_4.png"

        await interaction.response.send_message(
            f"📷 Escaneie o QR Pix para pagar **{ultimo_item['nome']}**:",
            file=discord.File(qr_file),
            ephemeral=True
        )

    # ----------------- CONFIRMAR PAGAMENTO (STAFF) -----------------
    elif interaction.data["custom_id"].startswith("confirmar_pagamento_"):
        staff_role = discord.utils.get(interaction.guild.roles, name=CARGO_STAFF)
        if staff_role not in interaction.user.roles:
            await interaction.response.send_message("❌ Apenas a staff pode confirmar o pagamento.", ephemeral=True)
            return

        cliente_id = int(interaction.data["custom_id"].split("_")[-1])
        carrinho = CARRINHOS.get(cliente_id, [])
        if not carrinho:
            await interaction.response.send_message("❌ Carrinho vazio do cliente.", ephemeral=True)
            return

        mensagem = "✅ Pagamento confirmado! Aqui estão os logins:\n"
        for item in carrinho:
            mensagem += f"**{item['nome']}** → Login: `{item['login']}`, Senha: `{item['senha']}`\n"
        CARRINHOS[cliente_id] = []

        await interaction.response.send_message(mensagem, ephemeral=True)

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
