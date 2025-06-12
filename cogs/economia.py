from discord.ext import commands
from discord import app_commands
from utils.economia_manager import Manager
import discord, random, asyncio
from datetime import datetime, timedelta, timezone

class Economia(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.manager = Manager()
        
    @app_commands.command(name="saldo", description="Mostra seu saldo ou o de outro usuário.")
    @app_commands.describe(usuario="O usuário no qual você quer ver o saldo!")
    async def saldo(self, interaction: discord.Interaction, usuario: discord.Member = None):
        target_user = usuario or interaction.user
        
        balance = self.manager.get_balance(target_user.id)
        
        embed = discord.Embed(
            title=f"💰 Saldo de {target_user.display_name}",
            description=f"Você possui **${balance:,}**.",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=target_user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="daily", description="Colete sua recompensa diária!")
    async def daily(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        cooldown_duration = timedelta(hours=24)
        
        last_used = self.manager.get_cooldown(user_id, "daily")
        
        if last_used:
            time_since_last_used = datetime.now(timezone.utc) - last_used
            if time_since_last_used < cooldown_duration:
                tempo_restante = cooldown_duration - time_since_last_used
                
                total_seconds_left = int(tempo_restante.total_seconds())
                horas, rem = divmod(total_seconds_left, 3600)
                minutos, segundos = divmod(rem, 60)
                tempo_formatado = f"{horas:02d}:{minutos:02d}:{segundos:02d}"

                embed_erro = discord.Embed(
                    title="⏳ Calma, apressadinho!",
                    description=f"Você precisa esperar mais `{tempo_formatado}` para usar este comando novamente.",
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_erro, ephemeral=True)
                return

        recompensa = random.randint(200, 750)
        self.manager.add_balance(user_id, recompensa)
        self.manager.update_cooldown(user_id, "daily")
        
        embed = discord.Embed(
            title="🎉 Recompensa Diária",
            description=f"Você coletou sua recompensa diária e ganhou **${recompensa:,}**!",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="trabalhar", description="Trabalhe para ganhar um dinheiro extra.")
    async def trabalhar(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        cooldown_duration = timedelta(hours=1)
        
        last_used = self.manager.get_cooldown(user_id, "work")
        
        if last_used:
            time_since_last_used = datetime.now(timezone.utc) - last_used
            if time_since_last_used < cooldown_duration:
                tempo_restante = cooldown_duration - time_since_last_used
                total_seconds_left = int(tempo_restante.total_seconds())
                horas, rem = divmod(total_seconds_left, 3600)
                minutos, segundos = divmod(rem, 60)
                tempo_formatado = f"{minutos:02d}:{segundos:02d}"

                embed_erro = discord.Embed(
                    title="💼 Você já bateu o ponto!",
                    description=f"Seu turno ainda não acabou. Volte em `{tempo_formatado}` para trabalhar de novo.",
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_erro, ephemeral=True)
                return

        ganhos = random.randint(50, 200)
        trabalhos = ["entregador de pizza", "lavador de pratos", "passeador de cães", "testador de colchões", "garoto de programa", "stripper"]
        
        self.manager.add_balance(user_id, ganhos)
        self.manager.update_cooldown(user_id, "work")
        
        embed = discord.Embed(
            title="💼 Dia de Trabalho",
            description=f"Você trabalhou como **{random.choice(trabalhos)}** e ganhou **${ganhos:,}**!",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pagar", description="Transfere dinheiro para outro usuário.")
    @app_commands.describe(destinatario="Para quem você quer pagar.", quantia="A quantia a ser paga.")
    async def pagar(self, interaction: discord.Interaction, destinatario: discord.Member, quantia: int):
        remetente_id = interaction.user.id
        destinatario_id = destinatario.id
        if remetente_id == destinatario_id:
            await interaction.response.send_message("Você não pode pagar a si mesmo!", ephemeral=True)
            return
        if quantia <= 0:
            await interaction.response.send_message("A quantia deve ser positiva!", ephemeral=True)
            return
        saldo_remetente = self.manager.get_balance(remetente_id)
        if saldo_remetente < quantia:
            await interaction.response.send_message(f"Você não tem dinheiro suficiente! Seu saldo é de ${saldo_remetente:,}.", ephemeral=True)
            return
        self.manager.add_balance(remetente_id, -quantia)
        self.manager.add_balance(destinatario_id, quantia)
        embed = discord.Embed(
            title="💸 Transferência Realizada",
            description=f"{interaction.user.mention} transferiu **${quantia:,}** para {destinatario.mention}.",
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed)
    

    @app_commands.command(name="rank", description="Mostra os usuários mais ricos do servidor.")
    async def rank(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = self.manager.load_data()
        server_members = {str(member.id) for member in interaction.guild.members}
        server_data = {uid: udata.get("balance", 0) for uid, udata in data["users"].items() if uid in server_members}
        sorted_users = sorted(server_data.items(), key=lambda item: item[1], reverse=True)
        embed = discord.Embed(title="🏆 Ranking dos Pobrinhos", color=discord.Color.gold())
        
        description = ""
        for i, (user_id, balance) in enumerate(sorted_users[:10]):
            user = self.client.get_user(int(user_id))
            if user:
                description += f"**{i+1}.** {user.mention} - **${balance:,}**\n"
        
        if not description:
            description = "Ninguém no ranking ainda. Use `/daily` para começar!"
            
        embed.description = description
        await interaction.followup.send(embed=embed)

        
    #JACKPOTTTTTTTTTTTTTT
    @app_commands.command(name="jackpot", description="Mostra o valor atual do prêmio acumulado no /slot.")
    async def jackpot(self, interaction: discord.Interaction):
        valor_jackpot = self.manager.get_jackpot()
        embed = discord.Embed(
            title="💎 Jackpot Atual",
            description=f"O prêmio acumulado para quem tirar a sorte grande é de **${valor_jackpot:,}**!",
            color=discord.Color.dark_gold()
        )
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="slot", description="Aposte na máquina caça-níquel para tentar a sorte grande!")
    @app_commands.describe(aposta="A quantia que você quer apostar (mínimo 50).")
    async def slot(self, interaction: discord.Interaction, aposta: int = 50):
        user_id = interaction.user.id

        if aposta < 50:
            await interaction.response.send_message("A aposta mínima é de **$50**.", ephemeral=True)
            return

        saldo_atual = self.manager.get_balance(user_id)
        if saldo_atual < aposta:
            await interaction.response.send_message(f"Você não tem saldo suficiente para apostar **${aposta:,}**.", ephemeral=True)
            return

        self.manager.add_balance(user_id, -aposta)

        simbolos = ["🍒", "🍋", "🍉", "⭐", "🍀", "💎"]
        
        embed = discord.Embed(title="🎰 **Girando...** 🎰", description="...", color=discord.Color.light_grey())
        await interaction.response.send_message(embed=embed)
        
        for _ in range(5):
            reels = [random.choice(simbolos) for _ in range(3)]
            embed.description = f"**| {reels[0]} | {reels[1]} | {reels[2]} |**"
            await interaction.edit_original_response(embed=embed)
            await asyncio.sleep(0.5)

        resultado = [random.choice(simbolos) for _ in range(3)]
        embed.description = f"**| {resultado[0]} | {resultado[1]} | {resultado[2]} |**"
        
        if resultado[0] == resultado[1] == resultado[2]:
            premio = self.manager.get_jackpot()
            self.manager.add_balance(user_id, premio)
            self.manager.set_jackpot(1000)
            
            embed.title = "🎉 **JACKPOT!** 🎉"
            embed.color = discord.Color.gold()
            embed.add_field(name="Parabéns!", value=f"Você tirou a sorte grande e ganhou **${premio:,}**!")

        elif resultado[0] == resultado[1] or resultado[1] == resultado[2] or resultado[0] == resultado[2]:
            premio = aposta * 2
            self.manager.add_balance(user_id, premio)

            embed.title = "✨ **Quase lá!** ✨"
            embed.color = discord.Color.green()
            embed.add_field(name="Boa!", value=f"Você conseguiu um par e ganhou **${premio:,}**!")

        else:
            contribuicao_jackpot = int(aposta * 0.80)
            self.manager.update_jackpot(contribuicao_jackpot)

            embed.title = "😕 **Não foi desta vez...** 😕"
            embed.color = discord.Color.red()
            valor_jackpot = self.manager.get_jackpot()
            embed.add_field(name="Que pena!", value=f"Mais sorte da próxima vez. O prêmio do jackpot aumentou! O valor total é de **${valor_jackpot:,}**!")

        await interaction.edit_original_response(embed=embed)
    
    
async def setup(client):
    await client.add_cog(Economia(client))