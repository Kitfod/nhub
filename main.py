import discord
from discord.ext import commands
from discord import app_commands
import json
import os

# ================= CONFIG =================

TOKEN = os.getenv("TOKEN")
CANAL_PERMITIDO = 1489609986219704390

ARQUIVO = "roupas.json"
HISTORICO = "historico.json"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ================= ARQUIVOS =================

for arquivo in [ARQUIVO, HISTORICO]:
    if not os.path.exists(arquivo):
        with open(arquivo, "w") as f:
            json.dump({}, f)


def carregar(arq):
    with open(arq, "r") as f:
        return json.load(f)


def salvar(arq, data):
    with open(arq, "w") as f:
        json.dump(data, f, indent=4)


# ================= MODAIS =================

class NomeModal(discord.ui.Modal, title="📋 Registrar Roupa"):
    nome = discord.ui.TextInput(label="Nome da roupa")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_modal(CodigoModal(self.nome.value))


class CodigoModal(discord.ui.Modal, title="👕 Código da Roupa"):
    codigo = discord.ui.TextInput(label="Cole o código", style=discord.TextStyle.paragraph)

    def __init__(self, nome):
        super().__init__()
        self.nome = nome

    async def on_submit(self, interaction: discord.Interaction):
        roupas = carregar(ARQUIVO)
        historico = carregar(HISTORICO)

        roupas[self.nome.lower()] = self.codigo.value
        historico[self.nome.lower()] = self.codigo.value

        salvar(ARQUIVO, roupas)
        salvar(HISTORICO, historico)

        embed = discord.Embed(
            title="✅ Roupa Registrada",
            description=f"**{self.nome}** foi salva com sucesso!",
            color=discord.Color.green()
        )

        await interaction.response.send_message(embed=embed)

        msg = await interaction.original_response()
        await msg.delete(delay=60)


# ================= PAINEL =================

class PainelView(discord.ui.View):
    @discord.ui.button(label="Registrar Roupa", style=discord.ButtonStyle.success, emoji="📋")
    async def registrar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        await interaction.response.send_modal(NomeModal())


# ================= LOJA =================

class LojaView(discord.ui.View):
    def __init__(self, roupas):
        super().__init__(timeout=None)
        self.roupas = list(roupas.items())
        self.index = 0

    def embed(self):
        nome, codigo = self.roupas[self.index]

        embed = discord.Embed(
            title="🛍️ Loja de Roupas GTA",
            description=f"👕 **{nome}**\n```{codigo}```",
            color=discord.Color.blurple()
        )

        embed.set_footer(text=f"{self.index+1}/{len(self.roupas)}")
        return embed

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
    async def anterior(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index = (self.index - 1) % len(self.roupas)
        await interaction.response.edit_message(embed=self.embed(), view=self)

    @discord.ui.button(label="📋 Copiar", style=discord.ButtonStyle.primary)
    async def copiar(self, interaction: discord.Interaction, button: discord.ui.Button):
        nome, codigo = self.roupas[self.index]
        msg = await interaction.channel.send(f"```{codigo}```")
        await msg.delete(delay=60)
        await interaction.response.defer()

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
    async def proximo(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index = (self.index + 1) % len(self.roupas)
        await interaction.response.edit_message(embed=self.embed(), view=self)


# ================= SLASH COMMANDS =================

@tree.command(name="painel", description="Abrir painel de registro")
async def painel_slash(interaction: discord.Interaction):
    if interaction.channel.id != CANAL_PERMITIDO:
        return

    embed = discord.Embed(
        title="📋 Painel de Registro",
        description="Clique abaixo para registrar uma roupa",
        color=discord.Color.green()
    )

    await interaction.response.send_message(embed=embed, view=PainelView())


@tree.command(name="loja", description="Abrir loja de roupas")
async def loja_slash(interaction: discord.Interaction):
    if interaction.channel.id != CANAL_PERMITIDO:
        return

    roupas = carregar(ARQUIVO)

    if not roupas:
        await interaction.response.send_message("❌ Nenhuma roupa cadastrada.", ephemeral=True)
        return

    view = LojaView(roupas)
    await interaction.response.send_message(embed=view.embed(), view=view)


@tree.command(name="buscar", description="Buscar roupa pelo nome")
async def buscar_slash(interaction: discord.Interaction, nome: str):
    if interaction.channel.id != CANAL_PERMITIDO:
        return

    roupas = carregar(ARQUIVO)

    nome = nome.lower()

    if nome in roupas:
        codigo = roupas[nome]

        embed = discord.Embed(
            title="🔎 Roupa encontrada",
            description=f"👕 **{nome}**\n```{codigo}```",
            color=discord.Color.blue()
        )

        await interaction.response.send_message(embed=embed)

        msg = await interaction.original_response()
        await msg.delete(delay=60)
    else:
        await interaction.response.send_message("❌ Não encontrada.", ephemeral=True)


# ================= READY =================

GUILD_ID = 1489609598557229156  # ID DO SERVIDOR

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)

    # copia comandos globais pra guild
    tree.copy_global_to(guild=guild)

    # sincroniza na guild
    await tree.sync(guild=guild)

    print(f"Bot online como {bot.user}")


# ================= START =================

bot.run(TOKEN)
