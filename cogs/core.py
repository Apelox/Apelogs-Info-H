from discord.ext import commands
import discord
import time
import logging
import asyncio
logger = logging.getLogger('apelog')

class Core(commands.Cog):
    def __init__(self, client):
        self.client = client

    @discord.app_commands.command(name="ping", description="Veja se o bot está online e a latência.")
    async def slash_ping(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        before = time.monotonic()
        await interaction.response.defer()
        after = time.monotonic()
        latency = (after - before) * 1000
        await interaction.followup.send(f"🏓 Pong! Latência: {int(latency)}ms", ephemeral=True)


    #Log
    ######
    
    logging.basicConfig(
        level=logging.INFO,  
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='apelog.log', 
        filemode='a'  
    )

    logger.info('Bot iniciado com sucesso!')
    @commands.Cog.listener()
    async def on_command(self, ctx):
        logger.info(f"Comando {ctx.command} usado por {ctx.author} em {ctx.channel}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        logger.error(f"Erro no comando {ctx.command} usado por {ctx.author}: {error}", exc_info=True)

    ######

    #help

    @discord.app_commands.command(name="help", description="Mostra os comandos de Apelogs.")
    async def slash_help(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        embed = discord.Embed(title="📚 Comandos do Apelogs", color=discord.Color.random())
        embed.add_field(name="/ping", value="Verifica se o bot está online e mostra a latência.", inline=False)
        embed.add_field(name="/help", value="Mostra essa mensagem de ajuda.", inline=False)
        embed.add_field(
            name="Animais",
            value=(
                "**:bird: | !bird**: Envia um gif aleatório de um pássaro.\n"
                "**:cat: | !cat**: Envia um gif aleatório de um gato.\n"
                "**:dog: | !dog**: Envia um gif aleatório de um cachorro.\n"
                "**:panda: | !panda**: Envia um gif aleatório de um panda."
            ),
            inline=False
        )

        await interaction.followup.send(embed=embed) 

async def setup(client):
    await client.add_cog(Core(client))
