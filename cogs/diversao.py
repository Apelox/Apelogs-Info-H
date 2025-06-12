from discord.ext import commands
import discord, requests, random

class Diversao(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @discord.app_commands.command(name="biscoitinho", description="Receba uma frase inspiradora (ou não) do nosso biscoito da sorte!")
    async def biscoito_da_sorte(self, interaction: discord.Interaction):
        frases = [
            "Você vai morrer em breve :D",
            "Você perdeu O JOGO!",
            "Não olhe para trás.",
            "Mande mensagem para sua ex AGORA!",
            "Se agora for um horário PAR você deveria se preocupar.",
            "ablublublé",
            "A vida trará coisas boas se tiver paciência.",
            "Demonstre amor e alegria em todas as oportunidades e verá que a paz nasce dentro de si.",
            "Não compense na ira o que lhe falta na razão.",
            "Defeitos e virtudes são apenas dois lados da mesma moeda.",
            "A maior de todas as torres começa no solo.",
            "Não há que ser forte. Há que ser flexível.",
            "Todos os dias organiza os seus cabelos, por que não faz o mesmo com o coração?",
            "Há três coisas que jamais voltam; a flecha lançada, a palavra dita e a oportunidade perdida.",
            "A juventude não é uma época da vida, é um estado de espírito.",
            "Podemos escolher o que semear, mas somos obrigados a colher o que plantamos.",
            "Dê toda a atenção á formação dos seus filhos, sobretudo com bons exemplos da sua própria vida.",
            "Siga os bons e aprenda com eles.",
            "Não importa o tamanho da montanha, ela não pode tapar o sol.",
            "O bom-senso vale mais do que muito conhecimento.",
            "Quem quer colher rosas tem de estar preparado para suportar os espinhos.",
            "São os nossos amigos que nos ensinam as mais valiosas lições.",
            "Aquele que se importa com o sentimento dos outros, não é um tolo.",
            "A adversidade é um espelho que reflete o verdadeiro eu.",
            "Lamentar aquilo que não temos é desperdiçar aquilo que já possuímos.",
            "Uma bela flor é incompleta sem as suas folhas.",
            "Sem o fogo do entusiasmo, não há o calor da vitória.",
            "O riso é a menor distância entre duas pessoas.",
            "Os defeitos são mais fortes quando o amor é fraco.",
            "Amizade e Amor são coisas que se unem num piscar de olhos.",
            "Surpreender e ser surpreendido é o segredo do amor.",
            "Faça pequenas coisas hoje e coisas maiores lhe serão confiadas amanhã.",
            "A paciência na adversidade é sinal de um coração sensível.",
            "A sorte favorece a mente bem preparada.",
            "A sua visão se tornará mais clara apenas quando conseguir olhar para dentro do seu coração.",
            "Quem olha para fora sonha; quem olha para dentro acorda.",
            "As pessoas esquecerão o que você disse e o que você fez… mas nunca esquecerão como se sentiram.",
            "Espere pelo mais sábio dos conselhos: o tempo.",
            "Todas as coisas são difíceis antes de se tornarem fáceis.",
            "Se você se sente só é porque construiu muros ao invés de pontes.",
            "Vencer é 90 por cento suor e 10 por cento de engenho.",
            "O amor está sempre mais próximo do que você imagina.",
            "Você é do tamanho do seu sonho.",
            "Pare de procurar eternamente; a felicidade está mesmo aqui ao seu lado.",
            "O conhecimento é a única virtude e a ignorância é o único vício.",
            "O nosso primeiro e último amor é… o amor-próprio.",
            "Deixe de lado as preocupações e seja feliz.",
            "A vontade das pessoas é a melhor das leis.",
            "Nós somos o que pensamos.",
            "A maior barreira para o sucesso é o medo do fracasso.",
            "O pessimista vê a dificuldade em cada oportunidade; O otimista vê a oportunidade em cada dificuldade.",
            "Muitas das grandes realizações do mundo foram feitas por homens cansados e desanimados que continuaram o seu trabalho.",
            "O insucesso é apenas uma oportunidade para recomeçar de novo com mais experiência.",
            "Coragem é a resistência ao medo, domínio do medo, e não a ausência do medo.",
            "O verdadeiro homem mede a sua força, quando se defronta com o obstáculo.",
            "Quem quer vencer um obstáculo deve armar-se da força do leão e da prudência da serpente.",
            "A adversidade desperta em nós capacidades que, em circunstâncias favoráveis, teriam ficado adormecidas.",
            "Motivação não é sinónimo de transformação, mas um passo em sua direção.",
            "O que empobrece o ser humano, não é a falta de dinheiro, mais sim, a falta de fé,motivação e criatividade.",
            "A inspiração vem dos outros. A motivação vem de dentro de nós.",
            "Não acredite mais em pessoas especiais, mas em momentos especiais com pessoas normais.",
            "A nossa vida tem 4 sentidos… Amar, Sofrer, Lutar e Vencer. Ame muito, sofra pouco, lute bastante e vença sempre!",
            "Nada é por acaso… Acredite em seus sonhos e nos seus potenciais….Na vida tudo se supera..",
            "Acredite em milagres, mas não dependa deles.",
            "Você sempre será a sua melhor companhia!"
        ]
        
        escolha = random.choice(frases)
        embed = discord.Embed(
            title="🥠 Biscoito da Sorte",
            description=f"**Sua sorte de hoje é:**\n\n> {escolha}",
            color=discord.Color.random()
        )
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="apergunta", description="Faça uma pergunta de sim ou não e o oráculo responderá!")
    async def apergunta(self, interaction: discord.Interaction, duvida: str):

        await interaction.response.defer()
        with open("data/respostas.txt", "r", encoding="utf-8") as f:
                respostas = f.read().splitlines()
        if not respostas:
            await interaction.followup.send("Meu oráculo está silencioso... O arquivo de respostas está vazio.")
            return

        resposta_escolhida = random.choice(respostas)
        mensagem_final = (
            f"🔮{resposta_escolhida}"
            )
        await interaction.followup.send(mensagem_final)
        
            
async def setup(client):
    await client.add_cog(Diversao(client))