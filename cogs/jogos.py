import discord
import random
import re
from discord.ext import commands
from discord import app_commands
from utils.economia_manager import Manager

VALORES = {11: "J", 12: "Q", 13: "K", 14: "A"}
NAIPES = {"E": "♠️", "P": "♣️", "C": "♥️", "D": "♦️"}

def criar_baralho():
    baralho = []
    for naipe in NAIPES.keys():
        for valor in range(2, 15):
            baralho.append({"valor": valor, "naipe": naipe})
    random.shuffle(baralho)
    return baralho

def formatar_carta(carta):
    valor_str = VALORES.get(carta["valor"], str(carta["valor"]))
    naipe_str = NAIPES[carta["naipe"]]
    return f"**{valor_str}** {naipe_str}"


class HigherLowerView(discord.ui.View):
    def __init__(self, game_id, cog_jogos):
        super().__init__(timeout=120)
        self.game_id = game_id
        self.cog_jogos = cog_jogos
        self.children[2].disabled = True

    async def handle_game_end(self, interaction: discord.Interaction):
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)
        self.cog_jogos.active_higher_lower.pop(self.game_id, None)

    async def handle_guess(self, interaction: discord.Interaction, guess: str):
        game = self.cog_jogos.active_higher_lower.get(self.game_id)
        if not game or interaction.user.id != game["player_id"]:
            return await interaction.response.send_message("Este não é o seu jogo!", ephemeral=True)

        carta_anterior = game["current_card"]
        nova_carta = game["deck"].pop()
        game["current_card"] = nova_carta

        resultado_correto = False
        if guess == "maior" and nova_carta["valor"] > carta_anterior["valor"]:
            resultado_correto = True
        elif guess == "menor" and nova_carta["valor"] < carta_anterior["valor"]:
            resultado_correto = True

        if resultado_correto:
            game["streak"] += 1
            if game["streak"] >= 5:
                payout = self.cog_jogos.get_payout(game)
                self.cog_jogos.manager.add_balance(interaction.user.id, payout)
                
                status_final = f"🎉 PARABÉNS! Você atingiu a sequência máxima de 5 acertos e ganhou o prêmio máximo de ${payout:,}!"
                embed = self.cog_jogos.create_higher_lower_embed(game, status_final, game_over=True)
                
                await interaction.response.edit_message(embed=embed)
                await self.handle_game_end(interaction)
                return
            
            self.children[2].disabled = False 
            embed = self.cog_jogos.create_higher_lower_embed(game, f"Você acertou! A nova carta é {formatar_carta(nova_carta)}.")
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            if nova_carta["valor"] == carta_anterior["valor"]:
                motivo = f"⚖️ EMPATE! O jogo continua com a carta: {formatar_carta(nova_carta)}."
                embed = self.cog_jogos.create_higher_lower_embed(game, motivo, game_over=False) 
                await interaction.response.edit_message(embed=embed, view=self)
            else:
                self.cog_jogos.manager.update_jackpot(game['initial_bet'])
                motivo = f"Você perdeu! A carta era {formatar_carta(nova_carta)}."
                
                embed = self.cog_jogos.create_higher_lower_embed(game, motivo, game_over=True)
                await interaction.response.edit_message(embed=embed)
                await self.handle_game_end(interaction)

    @discord.ui.button(label="🔼 Maior", style=discord.ButtonStyle.success)
    async def higher_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_guess(interaction, "maior")

    @discord.ui.button(label="🔽 Menor", style=discord.ButtonStyle.danger)
    async def lower_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_guess(interaction, "menor")

    @discord.ui.button(label="💰 Retirar Lucro", style=discord.ButtonStyle.primary)
    async def cashout_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        game = self.cog_jogos.active_higher_lower.get(self.game_id)
        if not game or interaction.user.id != game["player_id"]:
            return await interaction.response.send_message("Este não é o seu jogo!", ephemeral=True)

        payout = self.cog_jogos.get_payout(game)
        self.cog_jogos.manager.add_balance(interaction.user.id, payout)

        embed = self.cog_jogos.create_higher_lower_embed(game, f"Você retirou seu lucro de ${payout:,}!", game_over=True)
        await interaction.response.edit_message(embed=embed)
        await self.handle_game_end(interaction)

class Jogos(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.manager = Manager()
        self.active_duels = {}
        self.active_higher_lower = {}
        self.payout_multipliers = {1: 1.2, 2: 1.5, 3: 2, 4: 3, 5: 5}

    def get_payout(self, game_state):
        multiplier = self.payout_multipliers.get(game_state["streak"], 0)
        return int(game_state["initial_bet"] * multiplier)

    def create_higher_lower_embed(self, game, status_text, game_over=False):
        payout = self.get_payout(game)
        color = discord.Color.gold()
        if game_over:
            color = discord.Color.dark_red() if payout == 0 else discord.Color.green()

        embed = discord.Embed(title="🃏 Elevador 🃏", description=status_text, color=color)
        embed.add_field(name="Aposta Inicial", value=f"${game['initial_bet']:,}")
        embed.add_field(name="Acertos Seguidos", value=game['streak'])
        embed.add_field(name="Prêmio Atual", value=f"**${payout:,}**")
        embed.set_footer(text=f"Jogo de {game['player_name']}")
        return embed

    @app_commands.command(name="elevador", description="Aposte se a próxima carta será maior ou menor.")
    @app_commands.describe(aposta="O valor que você quer apostar. Mínimo = 50!")
    async def elevador(self, interaction: discord.Interaction, aposta: int):
        APOSTA_MINIMA = 50
        APOSTA_MAXIMA = 200000000000000000
        if aposta < APOSTA_MINIMA:
            return await interaction.response.send_message(f"A aposta mínima é de **${APOSTA_MINIMA}**.", ephemeral=True)

        if aposta > APOSTA_MAXIMA:
            return await interaction.response.send_message(f"A aposta máxima é de **${APOSTA_MAXIMA}**.", ephemeral=True)


        user_balance = self.manager.get_balance(interaction.user.id)
        if user_balance < aposta:
            return await interaction.response.send_message(f"Você não tem saldo suficiente! Seu saldo: ${user_balance:,}", ephemeral=True)
        
        self.manager.add_balance(interaction.user.id, -aposta)

        game_id = interaction.id
        baralho = criar_baralho()
        carta_inicial = baralho.pop()

        self.active_higher_lower[game_id] = {
            "player_id": interaction.user.id,
            "player_name": interaction.user.display_name, 
            "deck": baralho,
            "current_card": carta_inicial,
            "initial_bet": aposta,
            "streak": 0,
        }
        
        status = f"Sua primeira carta é {formatar_carta(carta_inicial)}. A próxima será maior ou menor?"
        embed = self.create_higher_lower_embed(self.active_higher_lower[game_id], status)
        view = HigherLowerView(game_id, self)
        
        await interaction.response.send_message(embed=embed, view=view)


    @app_commands.command(name="roll", description="Rola um ou mais dados no formato XdY+Z (ex: 2d6, d20+5).")
    @app_commands.describe(dados="A rolagem de dados que você quer fazer (ex: '2d6+3').")
    async def roll(self, interaction: discord.Interaction, dados: str):
        padrao = re.compile(r"(\d+)?d(\d+)([+-]\d+)?", re.IGNORECASE)
        match = padrao.fullmatch(dados.strip())

        if not match:
            await interaction.response.send_message(
                "❌ **Formato inválido!** Use a notação `XdY+Z`.\n"
                "Exemplos:\n"
                "`d20` (rola 1 dado de 20 lados)\n"
                "`2d6` (rola 2 dados de 6 lados)\n"
                "`1d8+4` (rola 1 dado de 8 lados e soma 4)\n"
                "`3d10-2` (rola 3 dados de 10 lados e subtrai 2)",
                ephemeral=True
            )
            return

        num_dados_str, num_lados_str, modificador_str = match.groups()
        num_dados = int(num_dados_str) if num_dados_str else 1
        num_lados = int(num_lados_str)
        modificador = int(modificador_str) if modificador_str else 0

        if not (1 <= num_dados <= 100):
            await interaction.response.send_message("❌ Você só pode rolar de 1 a 100 dados de uma vez.", ephemeral=True)
            return
        if not (1 <= num_lados <= 1000):
            await interaction.response.send_message("❌ O dado pode ter de 1 a 1000 lados.", ephemeral=True)
            return

        resultados = [random.randint(1, num_lados) for _ in range(num_dados)]
        soma_dados = sum(resultados)
        total_final = soma_dados + modificador

        resultados_str = ", ".join(map(str, resultados))
        
        embed = discord.Embed(
            title=f"🎲 Rolagem de Dados: `{dados}`",
            color=discord.Color.dark_purple()
        )
        
        descricao = f"**Resultados:** `[{resultados_str}]`\n"
        if modificador > 0:
            descricao += f"**Soma:** {soma_dados} + {modificador} = **{total_final}**"
        elif modificador < 0:
            descricao += f"**Soma:** {soma_dados} - {abs(modificador)} = **{total_final}**"
        else:
            descricao += f"**Total:** **{total_final}**"
            
        embed.description = descricao
        embed.set_footer(text=f"Rolado por {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed)
async def setup(client):
    await client.add_cog(Jogos(client))