from discord.ext import commands
from discord import app_commands
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
    @discord.app_commands.command(name="help", description="Mostra todos os comandos disponíveis do Apelogs.")
    async def slash_help(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        
        embed = discord.Embed(
            title="📚 Comandos do Apelogs",
            description=f"Aqui está a lista de tudo que eu posso fazer. \nMeu prefixo para comandos de música é `{self.client.command_prefix}`.",
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=self.client.user.display_avatar.url)

        # 🛠️ Comandos Principais e de Utilidade
        embed.add_field(
            name="🛠️ Utilidades",
            value=(
                "`/ping` - Verifica a latência do bot.\n"
                "`/help` - Mostra esta mensagem de ajuda.\n"
                "`/clima <cidade>` – Mostra o clima de uma cidade.\n"
                "`/filme <título>` – Busca informações de um filme/série.\n"
                "`/receita [prato]` – Busca uma receita (aleatória ou específica)."
            ),
            inline=False
        )
        
        # 💰 Comandos de Economia e Perfil
        embed.add_field(
            name="💰 Economia e Perfil",
            value=(
                "`/saldo [usuário]` - Mostra seu saldo em maõs, no banco e na carteira!\n"
                "`/perfil [usuário]` - Exibe o perfil completo do usuário.\n"
                "`/setbio <texto>` - Define sua biografia personalizada.\n"
                "`/daily` - Coleta sua recompensa diária.\n"
                "`/trabalhar` - Faz um trabalho para ganhar dinheiro.\n"
                "`/rank` - Exibe o ranking dos mais ricos.\n"
                "`/pagar <usuário> <quantia>` - Transfere dinheiro para outros."
            ),
            inline=False
        )
        
        # 🏦 Comandos de Banco e Investimentos
        embed.add_field(
            name="🏦 Banco e Investimentos",
            value=(
                "`/depositar <quantia>` - Guarda dinheiro no banco.\n"
                "`/sacar <quantia>` - Retira dinheiro do banco.\n"
                "`/investir <quantia>` - Compra cotas do Fundo Alox.\n"
                "`/resgatar <cotas>` - Vende suas cotas do Fundo.\n"
                "`/carteira` - Mostra seus investimentos atuais."
            ),
            inline=False
        )

        # 🎰 Jogos
        embed.add_field(
            name="🎰 Jogos de Azar",
            value=(
                "`/jackpot` - Mostra o prêmio atual da máquina.\n"
                "`/slot [aposta]` - Joga na máquina de caça-níquel."
            ),
            inline=False
        )

        # 🧠 Inteligência Artificial
        embed.add_field(
            name="🧠 Inteligência Artificial",
            value=(
                "`/ia <pergunta>` – Converse diretamente comigo.\n"
                "*Menção* - Me mencione em qualquer mensagem (`@Apelogs`) para uma resposta."
            ),
            inline=False
        )
        
        # 🎲 Comandos de Diversão
        embed.add_field(
            name="🎲 Diversão",
            value=(
                "`/biscoitinho` - Receba uma frase do biscoito da sorte.\n"
                "`/apergunta <dúvida>` - Responde sua pergunta de sim/não."
            ),
            inline=False
        )
        
        # 🎵 Comandos de Música
        embed.add_field(
            name=f"🎵 Música (use o prefixo `{self.client.command_prefix}`)",
            value=(
                "`play <música>` - Toca ou adiciona uma música à fila.\n"
                "`pause` / `resume` - Pausa ou retoma a música.\n"
                "`skip` - Pula para a próxima música.\n"
                "`stop` - Para a música e limpa a fila.\n"
                "`queue` - Mostra a fila de músicas.\n"
                "`clearq` - Limpa a fila de músicas."
            ),
            inline=False
        )

        # 🐾 Comandos de Animais
        embed.add_field(
            name="🐾 Animais",
            value="`/dog`, `/cat`, `/fox`, `/panda`, `/redpanda`, `/guaxinim`, `/coala`, `/canguru`, `/baleia`, `/bird`.",
            inline=False
        )
 
        await interaction.followup.send(embed=embed)

async def setup(client):
    await client.add_cog(Core(client))
