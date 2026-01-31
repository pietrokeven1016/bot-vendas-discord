import discord
from discord.ext import commands
from discord import ui
import os
from dotenv import load_dotenv
import qrcode
from io import BytesIO

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

CARGO_STAFF = "Staff"
CATEGORIA_TICKET = "Tickets"

# ================= DADOS DAS CONTAS =================
DADOS_CONTAS = {
    "1_mitica": {"nome": "1 MÍTICA RANDOM", "valor": "2.40", "estoque": 1, "login": "user1", "senha": "1234"},
    "2_miticas": {"nome": "2 MÍTICAS RANDOM", "valor": "3.60", "login": "user2", "senha": "abcd"},
    "3_miticas": {"nome": "3 MÍTICAS RANDOM", "valor": "5.00", "login": "user3", "senha": "xyz"},
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
        ]
        self.add_item(ui.Select(placeholder="Selecione a opção de conta desejada", options=options, custom_id="selecionar_conta"))

class CarrinhoView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ui.Button(label="🗑 Cancelar", style=discord.ButtonStyle.red, custom_id="carrinho_cancelar"))
        self.add_item(ui.Button(label="💳 Ir para Pagamento", style=discord.ButtonStyle.green, custom_id="carrinho_pagamento"))

class PagamentoView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ui.Button(label="🪙 Gerar QR Code", style=discord.ButtonStyle.green, custom_id="gerar_qr"))
        self.add_item(ui.Button(label="✅ Confirmar Pagamento (Staff)", style=discord.ButtonStyle.blurple, custom_id="confirmar_pagamento"))

# ================= FUNÇÃO PARA GERAR QR PIX =================
def gerar_pix_qr(chave_pix: str, valor: float):
    pix_string = f"00020126580014BR.GOV.BCB.PIX0136{chave_pix}520400005303986540{valor:.2f}5802BR5913Compra6009Cidade62070503***6304"
    img = qrcode.make(pix_string)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

# ================= EVENTO DE INTERAÇÃO =================
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.component:
        return

    user_id = interaction.user.id

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
        escolha = interaction.data["values"][0]
        conta = DADOS_CONTAS.get(escolha)
        if conta is None:
            await interaction.response.send_message("❌ Opção inválida.", ephemeral=True)
            return
        if conta["estoque"] == 0:
            await interaction.response.send_message("❌ Esta opção está sem estoque no momento.", ephemeral=True)
            return

        if user_id not in CARRINHOS:
            CARRINHOS[user_id] = []
        CARRINHOS[user_id].append(conta)

        embed = discord.Embed(title=f"{conta['nome']} adicionado ao carrinho!", description=f"💰 Valor: R${conta['valor']}", color=discord.Color.green())
        await interaction.response.send_message(embed=embed, view=CarrinhoView(), ephemeral=True)

    # ----------------- VER CARRINHO -----------------
    elif interaction.data["custom_id"] == "ver_carrinho":
        carrinho = CARRINHOS.get(user_id, [])
        if not carrinho:
            await interaction.response.send_message("🛒 Seu carrinho está vazio.", ephemeral=True)
            return
        embed = discord.Embed(title="🛒 Seu Carrinho", color=discord.Color.blue())
        total = 0
        for i, item in enumerate(carrinho, 1):
            embed.add_field(name=f"{i}. {item['nome']}", value=f"💰 R${item['valor']}", inline=False)
            total += float(item['valor'])
        embed.add_field(name="💵 Total", value=f"R${total:.2f}", inline=False)
        await interaction.response.send_message(embed=embed, view=CarrinhoView(), ephemeral=True)

    # ----------------- CANCELAR ITEM -----------------
    elif interaction.data["custom_id"] == "carrinho_cancelar":
        carrinho = CARRINHOS.get(user_id, [])
        if not carrinho:
            await interaction.response.send_message("❌ Seu carrinho já está vazio.", ephemeral=True)
            return
        item_removido = carrinho.pop()
        await interaction.response.send_message(f"🗑 {item_removido['nome']} foi removido do seu carrinho.", ephemeral=True)

    # ----------------- IR PARA PAGAMENTO -----------------
    elif interaction.data["custom_id"] == "carrinho_pagamento":
        carrinho = CARRINHOS.get(user_id, [])
        if not carrinho:
            await interaction.response.send_message("❌ Seu carrinho está vazio.", ephemeral=True)
            return
        total = sum(float(item['valor']) for item in carrinho)
        embed = discord.Embed(title="💳 Pagamento", description=f"Total: **R${total:.2f}**\nClique em Gerar QR Code para Pix ou peça a confirmação à staff.", color=discord.Color.green())
        await interaction.response.send_message(embed=embed, view=PagamentoView(), ephemeral=True)

    # ----------------- GERAR QR -----------------
    elif interaction.data["custom_id"] == "gerar_qr":
        carrinho = CARRINHOS.get(user_id, [])
        if not carrinho:
            await interaction.response.send_message("❌ Carrinho vazio.", ephemeral=True)
            return
        total = sum(float(item['valor']) for item in carrinho)
        chave_pix = "seu-email-ou-telefone"  # coloque sua chave Pix aqui
        qr_img = gerar_pix_qr(chave_pix, total)
        await interaction.response.send_message("📷 Aqui está seu QR Pix:", file=discord.File(fp=qr_img, filename="pix.png"), ephemeral=True)

    # ----------------- CONFIRMAR PAGAMENTO (STAFF) -----------------
    elif interaction.data["custom_id"] == "confirmar_pagamento":
        staff_role = discord.utils.get(interaction.guild.roles, name=CARGO_STAFF)
        if staff_role not in interaction.user.roles:
            await interaction.response.send_message("❌ Apenas a staff pode confirmar o pagamento.", ephemeral=True)
            return
        carrinho = CARRINHOS.get(user_id, [])
        if not carrinho:
            await interaction.response.send_message("❌ Carrinho vazio.", ephemeral=True)
            return

        # Envia login + senha de todas as contas compradas
        mensagem = "✅ Pagamento confirmado! Aqui estão seus logins:\n"
        for item in carrinho:
            mensagem += f"**{item['nome']}** → Login: `{item['login']}`, Senha: `{item['senha']}`\n"

        # Limpa o carrinho após envio
        CARRINHOS[user_id] = []

        await interaction.response.send_message(mensagem, ephemeral=True)

# ================= COMANDOS =================
@bot.command()
async def painel(ctx):
    embed = discord.Embed(title="🛒 Painel de Atendimento", description="Clique no botão abaixo para abrir um ticket.", color=discord.Color.green())
    await ctx.send(embed=embed, view=TicketView())

@bot.command()
async def teste(ctx):
    await ctx.send("✅ Bot funcionando!")

bot.run(os.getenv("DISCORD_TOKEN"))
