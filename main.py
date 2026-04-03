import discord
from discord.ext import commands
import json
import os

# ================= CONFIG =================

TOKEN = "SEU_TOKEN_AQUI"
CANAL_PERMITIDO = 123456789012345678

ARQUIVO = "roupas.json"
HISTORICO = "historico.json"

# ================= INTENTS =================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

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

class NomeModal(discord.ui.Modal, title="Registrar Roupa"):
    nome = discord.ui.TextInput(label="Nome da roupa")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_modal(CodigoModal(self.nome.value))


class CodigoModal(discord.ui.Modal, title="Código da Roupa"):
    codigo = discord.ui.TextInput(label="Código", style=discord.TextStyle.paragraph)

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

        msg = await interaction.response.send_message(
            f"✅ **{self.nome}** registrada!",
        )

        sent = await interaction.original_response()
        await sent.delete(delay=60)


# ================= PAINEL =================

class PainelView(discord.ui.View):
    @discord.ui.button(label="Registrar Roupa", style=discord.ButtonStyle.green)
    async def registrar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        await interaction.response.send_modal(NomeModal())


# ================= LOJA =================

class LojaView(discord.ui.View):
    def __init__(self, roupas):
        super().__init__(timeout=None)
        self.roupas = list(roupas.items())
        self.index = 0

    def gerar_embed(self):
        nome, codigo = self.roupas[self.index]

        embed = discord.Embed(
            title=f"🛍️ Loja de Roupas GTA",
            description=f"**{nome}**\n```{codigo}```",
            color=discord.Color.blue()
        )

        embed.set_footer(text=f"{self.index+1}/{len(self.roupas)}")
        return embed

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
    async def anterior(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index = (self.index - 1) % len(self.roupas)
        await interaction.response.edit_message(embed=self.gerar_embed(), view=self)

    @discord.ui.button(label="📋 Copiar", style=discord.ButtonStyle.primary)
    async def copiar(self, interaction: discord.Interaction, button: discord.ui.Button):
        nome, codigo = self.roupas[self.index]

        msg = await interaction.channel.send(f"```{codigo}```")
        await msg.delete(delay=60)

        await interaction.response.defer()

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
    async def proximo(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index = (self.index + 1) % len(self.roupas)
        await interaction.response.edit_message(embed=self.gerar_embed(), view=self)


# ================= COMANDOS =================

@bot.command()
async def painel(ctx):
    if ctx.channel.id != CANAL_PERMITIDO:
        return

    embed = discord.Embed(
        title="📋 Painel de Registro",
        description="Clique para registrar uma roupa",
        color=discord.Color.green()
    )

    await ctx.send(embed=embed, view=PainelView())


@bot.command()
async def loja(ctx):
    if ctx.channel.id != CANAL_PERMITIDO:
        return

    roupas = carregar(ARQUIVO)

    if not roupas:
        await ctx.send("❌ Nenhuma roupa cadastrada.")
        return

    view = LojaView(roupas)
    await ctx.send(embed=view.gerar_embed(), view=view)


# ================= BUSCA =================

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id != CANAL_PERMITIDO:
        return

    if message.content.startswith("#"):
        nome = message.content[1:].lower()
        roupas = carregar(ARQUIVO)

        if nome in roupas:
            codigo = roupas[nome]

            msg = await message.channel.send(f"```{codigo}```")
            await msg.delete(delay=60)
        else:
            msg = await message.channel.send("❌ Não encontrada.")
            await msg.delete(delay=10)

    await bot.process_commands(message)


# ================= START =================

import os
TOKEN = os.getenv("TOKEN")