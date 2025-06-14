from discord.ext import commands
from discord import app_commands
from utils.economia_manager import Manager
import discord, random, asyncio
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

class Economia(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.manager = Manager()
        
    @app_commands.command(name="saldo", description="Mostra seu saldo ou o de outro usuário.")
    @app_commands.describe(usuario="O usuário no qual você quer ver o saldo!")
    async def saldo(self, interaction: discord.Interaction, usuario: discord.Member = None):
        target_user = usuario or interaction.user
        preco_cota_atual = await self._atualizar_mercado()
        user_data = self.manager.get_user_data(target_user.id)
        cotas = user_data["investments"]["cotas"]
        valor_total = cotas * preco_cota_atual
        
        saldo_mao = user_data.get("balance", 0)
        saldo_banco = user_data.get("bank", 0)
        
        embed = discord.Embed(
            title=f"💰 Saldo de {target_user.display_name}",
            description=f"Possui **${saldo_mao:,}** em mãos\n**${saldo_banco:,}** no banco\nE $**{valor_total:,.0f}** na carteira!",
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
        with open("data/trabalhos.txt", "r", encoding="utf-8") as f:
            trabalhos = f.read().splitlines()
        if not trabalhos:
            await interaction.followup.send("Meu oráculo está silencioso... O arquivo de trabalhos está vazio.")
            return

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
    
    
    #PERFIL
    @app_commands.command(name="perfil", description="Mostra seu perfil econômico e suas badges.")
    @app_commands.describe(usuario="O usuário do qual você quer ver o perfil.")
    async def perfil(self, interaction: discord.Interaction, usuario: discord.Member = None):
        preco_cota_atual = await self._atualizar_mercado()
        target_user = usuario or interaction.user
        user_data = self.manager.get_user_data(target_user.id)
        saldo_mao = user_data.get("balance", 0)
        saldo_banco = user_data.get("bank", 0)
        valor_investido = user_data["investments"]["total_investido_acumulado"]
        cotas = user_data["investments"]["cotas"]
        valor_total = cotas * preco_cota_atual
        lucro_prejuizo = valor_total - valor_investido
        
        if lucro_prejuizo >= 0:
            lucro_str = f"```diff\n+ ${lucro_prejuizo:,.2f}\n```"
        else:
            lucro_str = f"```diff\n- ${abs(lucro_prejuizo):,.2f}\n```"
        
        
        biografia = user_data.get("biography", "Nenhuma biografia definida.")
        badges = user_data.get("badges", [])
        badges_str = " ".join(badges) if badges else "Nenhuma badge ainda."
        

        data_criacao = discord.utils.format_dt(target_user.created_at, style='f')
        data_entrada = discord.utils.format_dt(target_user.joined_at, style='R')   


        embed = discord.Embed()
        embed.title=f"👤 Perfil de {target_user.display_name}"
        embed.description=f"*{biografia}*"
        embed.color=target_user.color
        
        
        embed.set_thumbnail(url=target_user.display_avatar.url)

        embed.add_field(name="💵 Em Mãos", value=f"```${saldo_mao:,}```", inline=True)
        embed.add_field(name="🏦 No Banco", value=f"```${saldo_banco:,}```")
        embed.add_field(name="💼 Na Carteira", value=f"```${valor_total:,.0f}```")
        invest_level = self._get_nivel_investidor(user_data["investments"]["total_investido_acumulado"])
        embed.add_field(name="📈 Nível de Investidor", value=invest_level, inline=False)
        embed.add_field(name="📈 Investimentos", value=lucro_str, inline=True)
                
        embed.add_field(name="🏆 Badges", value=badges_str, inline=False)

        embed.set_footer(text=f"ID do Usuário: {target_user.id}")
        embed.add_field(name="🗓️ Conta Criada", value=data_criacao, inline=True)
        embed.add_field(name="👋 Entrou no Servidor", value=data_entrada, inline=True)

        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setbio", description="Define sua biografia para o comando /perfil.")
    @app_commands.describe(texto="O texto da sua nova biografia (máximo 150 caracteres).")
    async def setbio(self, interaction: discord.Interaction, texto: str):
        if len(texto) > 150:
            await interaction.response.send_message("❌ Sua biografia não pode ter mais de 150 caracteres.", ephemeral=True)
            return

        user_id = interaction.user.id
        user_data = self.manager.get_user_data(user_id)
        
        user_data["biography"] = texto
        self.manager.set_user_data(user_id, user_data)
        
        await interaction.response.send_message("✅ Sua biografia foi atualizada com sucesso!", ephemeral=True)
    
    #BANCO
    @app_commands.command(name="depositar", description="Deposita dinheiro no banco para mantê-lo seguro.")
    @app_commands.describe(quantia="A quantia a ser depositada.")
    async def depositar(self, interaction: discord.Interaction, quantia: int):
        user_id = interaction.user.id
        
        if quantia <= 0:
            await interaction.response.send_message("A quantia deve ser positiva!", ephemeral=True)
            return

        user_data = self.manager.get_user_data(user_id)
        saldo_mao = user_data.get("balance", 0)

        if saldo_mao < quantia:
            await interaction.response.send_message(f"Você não tem dinheiro suficiente! Seu saldo em mãos é de ${saldo_mao:,}.", ephemeral=True)
            return

        user_data["balance"] -= quantia
        user_data["bank"] += quantia
        self.manager.set_user_data(user_id, user_data)
        
        await interaction.response.send_message(f"✅ Você depositou **${quantia:,}** no banco.")

    @app_commands.command(name="sacar", description="Saca dinheiro do banco.")
    @app_commands.describe(quantia="A quantia a ser sacada.")
    async def sacar(self, interaction: discord.Interaction, quantia: int):
        user_id = interaction.user.id

        if quantia <= 0:
            await interaction.response.send_message("A quantia deve ser positiva!", ephemeral=True)
            return

        user_data = self.manager.get_user_data(user_id)
        saldo_banco = user_data.get("bank", 0)

        if saldo_banco < quantia:
            await interaction.response.send_message(f"Você não tem saldo suficiente no banco! Seu saldo no banco é de ${saldo_banco:,}.", ephemeral=True)
            return
        
        user_data["balance"] += quantia
        user_data["bank"] -= quantia
        self.manager.set_user_data(user_id, user_data)

        await interaction.response.send_message(f"✅ Você sacou **${quantia:,}** do banco.")
    
    
    @app_commands.command(name="carteira", description="Mostra sua carteira de investimentos no Fundo Alox.")
    async def carteira(self, interaction: discord.Interaction):
        await interaction.response.defer()
        preco_cota_atual = await self._atualizar_mercado()
        
        user_data = self.manager.get_user_data(interaction.user.id)
        cotas = user_data["investments"]["cotas"]
        valor_total = cotas * preco_cota_atual

        embed = discord.Embed(
            title=f"💼 Carteira de {interaction.user.display_name}",
            color=discord.Color.dark_green()
        )
        embed.add_field(name="Cotas do Fundo", value=f"{cotas:.4f}", inline=True)
        embed.add_field(name="Preço Atual por Cota", value=f"${preco_cota_atual:,.0f}", inline=True)
        embed.add_field(name="Valor Total da Carteira", value=f"${valor_total:,.0f}", inline=False)
        embed.set_footer(text="Use /investir para comprar mais cotas ou /resgatar para vender.")

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="investir", description="Investe seu dinheiro do banco no Fundo Alox.")
    @app_commands.describe(quantia="A quantia em dinheiro que você deseja investir.")
    async def investir(self, interaction: discord.Interaction, quantia: int):
        await interaction.response.defer()
        if quantia <= 0:
            await interaction.followup.send("A quantia para investir deve ser positiva!", ephemeral=True)
            return

        user_id = interaction.user.id
        user_data = self.manager.get_user_data(user_id)
        saldo_banco = user_data["bank"]

        if saldo_banco < quantia:
            await interaction.followup.send(f"Você não tem saldo suficiente no banco! Seu saldo é de ${saldo_banco:,}.", ephemeral=True)
            return

        preco_cota_atual = await self._atualizar_mercado()
        cotas_compradas = quantia / preco_cota_atual
        user_data["bank"] -= quantia
        user_data["investments"]["cotas"] += cotas_compradas
        user_data["investments"]["total_investido_acumulado"] += quantia
        
        self.manager.set_user_data(user_id, user_data)

        embed = discord.Embed(
            title="📈 Investimento Realizado!",
            description=f"Você investiu **${quantia:,}** e comprou **{cotas_compradas:.4f}** cotas do Fundo Alox.",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="resgatar", description="Vende suas cotas do Fundo Alox e recebe o dinheiro no banco.")
    @app_commands.describe(cotas="O número de cotas que você deseja vender.")
    async def resgatar(self, interaction: discord.Interaction, cotas: float):
        await interaction.response.defer()
        if cotas <= 0:
            await interaction.followup.send("O número de cotas para resgatar deve ser positivo!", ephemeral=True)
            return

        user_id = interaction.user.id
        user_data = self.manager.get_user_data(user_id)
        cotas_usuario = user_data["investments"]["cotas"]

        if cotas_usuario < cotas:
            await interaction.followup.send(f"Você não tem cotas suficientes! Você possui {cotas_usuario:.4f} cotas.", ephemeral=True)
            return
            
        preco_cota_atual = await self._atualizar_mercado()
        valor_resgatado = cotas * preco_cota_atual
        user_data["bank"] += valor_resgatado
        user_data["investments"]["cotas"] -= cotas
        self.manager.set_user_data(user_id, user_data)
        
        embed = discord.Embed(
            title="💰 Resgate Realizado!",
            description=f"Você vendeu **{cotas:.4f}** cotas e resgatou **${valor_resgatado:,.2f}** para seu banco.",
            color=discord.Color.blue()
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="banco", description="Mostra estatísticas globais do Fundo Alox e do banco.")
    async def banco(self, interaction: discord.Interaction):
        await interaction.response.defer()
        preco_cota_atual = await self._atualizar_mercado()
        
        data = self.manager.load_data()
        users_data = data.get("users", {})
        invest_data = data.get("global", {}).get("investimento", {})

        valor_total_banco = sum(user.get("bank", 0) for user in users_data.values())
        total_cotas_compradas = sum(user.get("investments", {}).get("cotas", 0) for user in users_data.values())
        
        preco_cota_atual = invest_data.get("preco_por_cota", 0)
        valor_total_investido = total_cotas_compradas * preco_cota_atual
        
        historico_precos = invest_data.get("preco_cota_historico", [])
        
        embed = discord.Embed(
            title="🏦 Estatísticas Gerais do Banco Alox",
            description="Visão geral da economia do servidor.",
            color=discord.Color.dark_blue()
        )
        
        embed.add_field(
            name="💰 Ativos no Banco",
            value=f"**${valor_total_banco:,.2f}**",
            inline=True
        )
        embed.add_field(
            name="📈 Ativos Investidos",
            value=f"**${valor_total_investido:,.2f}**",
            inline=True
        )
        embed.add_field(
            name="📄 Total de Cotas",
            value=f"**{total_cotas_compradas:,.4f}** cotas no mercado",
            inline=False
        )
        
        if historico_precos:
            ultimos_registros = historico_precos[-5:]
            ultimos_registros.reverse()
            
            texto_historico = ""
            fuso_horario_br = ZoneInfo("America/Sao_Paulo")
            
            for registro in ultimos_registros:
                data_utc = datetime.fromisoformat(registro["data"])
                data_br = data_utc.astimezone(fuso_horario_br)
                texto_historico += f"`{data_br.strftime('%d/%m %Hh')}` - **${registro['preco']:,.2f}**\n"
                
            embed.add_field(
                name="📊 Histórico Recente do Preço da Cota",
                value=texto_historico,
                inline=False
            )
        else:
            embed.add_field(
                name="📊 Histórico Recente do Preço da Cota",
                value="Nenhum histórico disponível ainda.",
                inline=False
            )
        
        embed.set_footer(text=f"Preço atual da cota: ${preco_cota_atual:,.2f}")
        
        await interaction.followup.send(embed=embed)


    async def _atualizar_mercado(self):
        data = self.manager.load_data()
        invest_data = data["global"]["investimento"]
        
        preco_atual = invest_data["preco_por_cota"]
        ultima_att_str = invest_data["ultima_atualizacao"]
        ultima_att = datetime.fromisoformat(ultima_att_str)
        
        agora = datetime.now(timezone.utc)
        horas_passadas = int((agora - ultima_att).total_seconds() / 3600)

        if horas_passadas > 0:
            historico = invest_data.get("preco_cota_historico", [])
            for _ in range(horas_passadas):
                preco_atual *= random.uniform(0.97, 1.05)
                historico.append({"data": (ultima_att + timedelta(hours=_+1)).isoformat(), "preco": preco_atual})

            invest_data["preco_cota_historico"] = historico[-30:]
            
            data["global"]["investimento"]["preco_por_cota"] = preco_atual
            data["global"]["investimento"]["ultima_atualizacao"] = (ultima_att + timedelta(hours=horas_passadas)).isoformat()
            self.manager.save_data(data)
        
        return data["global"]["investimento"]["preco_por_cota"]

    def _get_nivel_investidor(self, total_investido):
        if 1 <= total_investido <= 999:
            return "Investidor Iniciante 🥉"
        elif 1000 <= total_investido <= 4999:
            return "Especulador Astuto 🥈"
        elif 5000 <= total_investido <= 24999:
            return "Rei das Finanças🥇"
        elif 25000 <= total_investido <= 99999:
            return "Barão do Mercado 💎"
        elif total_investido >= 100000:
            return "Lenda Financeira 👑"
        else:
            return "Nenhum"        
        
    
async def setup(client):
    await client.add_cog(Economia(client))