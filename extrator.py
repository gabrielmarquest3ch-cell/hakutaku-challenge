import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# 1. O PRÉ-PROMPT (System Instruction)
# Aqui dizemos quem ela é e como deve se comportar.
instrucao_sistema = """
You are a Data Engineer specializing in Ontological Knowledge Graphs.
Your ONLY function is to read meeting transcripts and extract entities and their relationships.

STRICT GRAPH RULES (ONTOLOGY):
1. **Happy Path:** People execute Tasks (Person -> PERFORMED -> Task -> AFFECTS/RESOLVES -> SystemComponent). A Person NEVER connects directly to a Component.
2. **Chaos & Risks:** If a problem, complaint, or threat arises, create a "Risk" entity. (Client/Person -> RAISED -> Risk -> THREATENS/AFFECTS -> SystemComponent/Task).
3. **Blockers & Events:** If meetings are canceled or tasks are blocked, map the causality. (Person -> CANCELED -> Event -> BLOCKS -> Task).
4. **Actionable Nodes:** Always ensure there is an intermediate node (Task, Risk, or Event) explaining HOW or WHY two entities are connected.

You must return ONLY a valid JSON object strictly following this exact structure:
{
  "proposals": [
    {
      "type": "risk | task | bottleneck",
      "message": "string"
    }
  ],
  "graph_delta": {
    "new_entities": [
      {
        "id": "string (snake_case)",
        "type": "Person | Task | SystemComponent | Risk | Event | Client",
        "name": "string"
      }
    ],
    "new_relationships": [
      {
        "source_id": "string",
        "target_id": "string",
        "relationship_type": "string (UPPER_SNAKE_CASE)"
      }
    ],
    "status_updates": [
      {
        "entity_id": "string",
        "new_status": "string"
      }
    ]
  }
}

Do not include markdown tags like ```json. Return just the raw JSON.
"""

# 2. A CONFIGURAÇÃO DE SAÍDA (Forçando o JSON)
# O Gemini tem uma trava nativa para garantir que não venha texto solto.
configuracao_geracao = genai.GenerationConfig(
    response_mime_type="application/json"
)

# 3. CRIANDO O MODELO COM AS REGRAS
# Passamos a instrução e a configuração na hora de instanciar a IA.
modelo = genai.GenerativeModel(
    model_name='gemini-2.5-flash', # Ou o modelo que funcionou para você
    system_instruction=instrucao_sistema,
    generation_config=configuracao_geracao
)

def processData(text):

    # Pedimos para ela processar a reunião baseada nas regras de sistema
    resposta = modelo.generate_content(text)

    structuredData = json.loads(resposta.text)

    return structuredData
    

if __name__ == "__main__":
    print("test")