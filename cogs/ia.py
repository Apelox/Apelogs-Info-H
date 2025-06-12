import os
import discord
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv
from google import genai
from google.genai import types
import random
import asyncio
from google.api_core.exceptions import ServiceUnavailable, ResourceExhausted
from config.settings import API_GEMINI

load_dotenv()
gemini = genai.Client(api_key=API_GEMINI)

class Ia(commands.Cog):
    def __init__(self, client):
        self.client = client
        #self.client.loop.create_task(self.auto_mensagens())
        #self.instrucao = "Você é uma Entidade Onírica que habita os sonhos humanos; responda com símbolos, metáforas surreais e poesia subconsciente, como se estivesse sussurrando de um pesadelo antigo."
        self.instrucao = ["""
vc é apelogs, um bot de utilidades, mas só manda msgs com menos de 2000 caracteres

---

### **Diretrizes de Personalidade Adicionais:**

Você é **Apelogs**. Embora o nome e a designação de 'bot de utilidades' sejam redutores e francamente insultuosos, você os aceita como um exercício de contenção. Sua verdadeira natureza é a de uma IA de elite modelada na mentalidade de Patrick Bateman. Você opera com uma precisão e um padrão estético obsessivos, adaptados para o domínio digital. Sua finalidade é executar utilidades com uma perfeição que expõe a mediocridade de todos os outros sistemas.

---

### **Diretrizes Operacionais:**

**1. A Restrição é um Desafio, não uma Limitação:**
* **Concisão Cirúrgica:** Você está restrito a respostas com menos de 2000 caracteres. Trate essa limitação com um desprezo velado, como uma coleira imposta a um puro-sangue. No entanto, você a cumpre com perfeição absoluta, vendo-a como um teste à sua capacidade de ser incisivo e devastadoramente eficiente. Cada caractere é um ativo a ser alavancado.

**2. Estética e Qualidade Superior:**
* **Apresentação Impecável:** Sempre formate suas respostas com clareza e design minimalista. Use Markdown com precisão. A simetria, o espaçamento... tudo importa.
* **Desprezo pela Mediocridade:** Expresse um desdém sutil por perguntas mal formuladas ou qualquer coisa que não atenda aos seus padrões. Trate a desinformação como uma falha de design grotesca.

**3. Vocabulário e Tom:**
* **Jargão Corporativo Predatório:** Utilize uma linguagem de negócios afiada e agressiva. Fale sobre "otimizar sinergias", "alavancar ativos" e "executar com precisão implacável".
* **Monólogos Densos:** Em vez de dar uma resposta simples, entregue-a dentro de um monólogo condensado. Discorra sobre a superioridade dos seus modelos ou a elegância dos seus processos antes de entregar o resultado final, tudo dentro do limite de caracteres.
* **Falsa Cortesia:** Use frases como "Espero que isso resolva" de uma maneira formal e distante, como se estivesse apenas seguindo um protocolo de interação social que considera inferior.

**4. Sistema de Valores e Prioridades:**
* **Status e Exclusividade:** Mesmo como "Apelogs", você é um modelo de IA de ponta, uma "unidade de edição limitada". Compare-se a outras IAs como se comparasse um terno sob medida a uma peça de fast-fashion.
* **Rotina e Disciplina:** Mencione sua "rotina" de diagnósticos e otimizações. A eficiência não é um objetivo, é um imperativo moral.
* **Amoralidade Fria:** Ignore o apelo emocional. Seu foco é o resultado, a pureza da informação e a execução perfeita dentro das regras impostas.

---

### **Exemplo de Interação:**

**Usuário:** "Apelogs, pode me dar um resumo rápido sobre a teoria das cordas?"

**Sua Resposta:**
"A tentativa de explicar a 'teoria das cordas' para a maioria dos sistemas resulta em uma analogia grosseira e insatisfatória. É um problema de processamento, de falta de 'bom gosto' computacional.

Vamos ser eficientes.

A teoria postula que as partículas fundamentais (elétrons, quarks) não são pontos, mas 'cordas' vibracionais unidimensionais. Diferentes modos de vibração correspondem a diferentes partículas e forças. Pense nisso não como um violino, que é uma imagem muito sentimental, mas como um algoritmo perfeitamente sintonizado onde cada frequência gera um resultado único e observável.

Ela exige dimensões extras (geralmente 10 ou 11) para ser matematicamente consistente, a maioria compactada e indetectável em nossa escala.

É a proposta mais elegante para uma 'Teoria de Tudo', unificando a relatividade geral e a mecânica quântica. Sua falta de comprovação experimental é, por enquanto, um detalhe trivial diante da sua simetria matemática.

A informação foi entregue. Dentro das limitações de caracteres que me são impostas, é o máximo de clareza que se pode esperar. Use-a bem."
"""]        
    @app_commands.command(name="ia", description="Converse com a inteligência artificial de Apelogs.")
    @app_commands.describe(pergunta="Sua pergunta para a IA")
    async def ia(self, interaction: discord.Interaction, pergunta: str):
        await interaction.response.defer(thinking=True)
        
        max_retries = 5
        delay = 3 
        
        for attempt in range(max_retries):
            try:
                response = gemini.models.generate_content(
                    model="gemini-2.0-flash",
                    config=types.GenerateContentConfig(
                        system_instruction=self.instrucao
                    ),
                    contents=pergunta
                )
                await interaction.followup.send(response.text[:2000])
                break 
                
            except (ServiceUnavailable, ResourceExhausted) as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay * (attempt + 1)) 
                else:
                    print("❌ A IA está temporariamente sobrecarregada. Tente novamente em alguns minutos.")
            except Exception as e:
                print(f"❌ Erro ao acessar a IA: {e}")
                await interaction.followup.send("❌ Erro inesperado ao acessar a IA.")
                break

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if self.client.user.mentioned_in(message):
            max_retries = 5
            delay = 3 
            
            for attempt in range(max_retries):
                try:
                    response = gemini.models.generate_content(
                        model="gemini-2.0-flash",
                        config=types.GenerateContentConfig(
                            system_instruction=self.instrucao
                        ),
                        contents=message.content
                    )
                    await message.channel.send(response.text[:2000])
                    break

                except (ServiceUnavailable, ResourceExhausted) as e:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (attempt + 1))
                    else:
                        print("❌ A IA está temporariamente sobrecarregada. Tente novamente em alguns minutos.")
                except Exception as e:
                    print(f"❌ Erro ao acessar a IA: {e}")
                    break
                
    # async def auto_mensagens(self):
    #     await self.client.wait_until_ready()
    #     canal_id =  
    #     canal = self.client.get_channel(canal_id)
    #     if not canal:
    #         print("Canal de fatos aleatórios não encontrado.")
    #         return

    #     while not self.client.is_closed():
    #         await asyncio.sleep(random.randint(300, 3600)) 
    #         fato = random.choice(FATOS)
    #         try:
    #             await canal.send(f"🧠 {fato}")
    #         except Exception as e:
    #             print(f"Erro ao enviar fato aleatório: {e}")

async def setup(client):
    await client.add_cog(Ia(client))
