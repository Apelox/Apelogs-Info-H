import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os

from config.settings import DISCORD_TOKEN, COMMAND_PREFIX

intents = discord.Intents.all()
client = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

@client.remove_command('help')    
@client.command()
@commands.is_owner()
async def reload(ctx, cog: str):
    try:
        await client.reload_extension(f"cogs.{cog}")
        await ctx.send(f"✅ Cog {cog} recarregada com sucesso.")
    except Exception as e:
        await ctx.send(f"❌ Erro ao recarregar {cog}: {e}")




@client.event
async def on_ready():
    print(f"Bot conectado como {client.user}")
    try:
        synced = await client.tree.sync()
        print(f"Slash commands sincronizados: {len(synced)}")
    except Exception as e:
        print(f"Erro ao sincronizar slash commands: {e}")
    print("A uma ideia de Patrick Bateman, é uma espécie de abstração, mas eu não sou isso na realidade, isso é uma entidade... É ilusório, embora eu possa esconder meu olhar frio e apertando minha mão você sinta minha carne e até pense que temos o mesmo estilo de vida eu... simplesmente não existo.")

    
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f"cogs.{filename[:-3]}")
            print(f"{filename[:-3]} iniciada.")

            
async def main():
    await load_cogs()
    await client.start(DISCORD_TOKEN)
    



asyncio.run(main())
