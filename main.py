import discord
from discord.ext import commands
from discord import app_commands
import json
import os

# ================= CONFIG =================

TOKEN = os.getenv("TOKEN")
CANAL_PERMITIDO = 1489609986219704390  # ID DO CANAL
GUILD_ID = 1489609598557229156  # ID DO SERVIDOR

ARQUIVO = "roupas.json"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ================= ARQUIVO =================

if not os.path.exists(ARQUIVO):
    with open(ARQUIVO, "w") as f:
        json.dump({}, f)


def carregar():
    with open(ARQUIVO, "r") as f:
        return json.load(f)


def salvar(data):
    with open(ARQUIVO, "w") as f:
        json.dump(data, f, indent=4)


# ================= MODAIS =================

class RegistrarModal(discord.ui.Modal, title="📋 Registrar Roupa"):
    nome = discord.ui.TextInput(label="Nome da roupa")
    codigo = discord.ui.TextInput(
        label="Código da roupa",
        style=discord.TextStyle.paragraph
    )

    async def on_submit(self, interaction: discord.Interaction):
        roupas = carregar()

        roupas[self.nome.value.lower()] = self.codigo.value
        salvar(roupas)

        embed = discord.Embed(
            title="✅ Roupa registrada",
            description=f"**{self.nome.value}** salva com sucesso!",
            color=discord.Color.green()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


# ================= COMANDOS =================

@tree.command(name="registrar", description="Registrar uma roupa")
async def registrar(interaction: discord.Interaction):

    if interaction.channel_id != CANAL_PERMITIDO:
        await interaction.response.send_message(
            "❌ Use este comando no canal correto.",
            ephemeral=True
        )
        return

    await interaction.response.send_modal(RegistrarModal())


@tree.command(name="buscar", description="Buscar roupa pelo nome")
async def buscar(interaction: discord.Interaction, nome: str):

    if interaction.channel_id != CANAL_PERMITIDO:
        await interaction.response.send_message(
            "❌ Use este comando no canal correto.",
            ephemeral=True
        )
        return

    roupas = carregar()
    nome = nome.lower()

    if nome in roupas:
        codigo = roupas[nome]

        msg = await interaction.response.send_message(
            f"👕 **{nome}**\n```{codigo}```"
        )

        # apagar após 60 segundos
        mensagem = await interaction.original_response()
        await mensagem.delete(delay=60)

    else:
        await interaction.response.send_message(
            "❌ Roupa não encontrada.",
            ephemeral=True
        )


# ================= READY =================

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)

    tree.copy_global_to(guild=guild)
    await tree.sync(guild=guild)

    print(f"Bot online como {bot.user}")


# ================= START =================

bot.run(TOKEN
