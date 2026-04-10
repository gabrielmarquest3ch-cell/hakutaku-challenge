# Hakutaku Challenge — Organizational Intelligence Layer

## Como rodar

### Pré-requisitos

- Python 3.11+ (instalado via [python.org](https://python.org), não Microsoft Store)
- Uma instância Neo4j rodando (local ou Aura)
- Chave de API do Google Gemini

### Configuração

1. Clone o repositório e instale as dependências:

```bash
pip install -r requirements.txt
```

2. Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
GEMINI_API_KEY=sua_chave_aqui
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=sua_senha_aqui
```

3. Inicie a aplicação:

```bash
streamlit run main.py
```

### Uso

1. Na sidebar, faça upload de um arquivo `.txt` com uma transcrição de reunião ou thread de chat
2. Clique em **Extract Knowledge**
3. O sistema extrai entidades, salva no Neo4j e atualiza os grafos automaticamente
4. Para múltiplos documentos, processe-os em ordem cronológica — o sistema usa o contexto acumulado de cada um para melhorar a extração seguinte

---

## Documento de Decisões Técnicas

### Ontologia

A modelagem partiu de uma pergunta central: *quais são os objetos operacionais reais que vivem dentro do conhecimento organizacional?*

Cheguei em seis tipos de entidade:

| Tipo | Descrição |
|---|---|
| `Person` | Quem age — toma decisões, executa tarefas, levanta riscos |
| `Task` | Unidade de trabalho com estado rastreável |
| `Risk` | Ameaça identificada com potencial de impacto operacional |
| `Event` | Acontecimento pontual que altera o estado do sistema (reunião, incidente) |
| `Client` | Entidade externa com poder de pressionar ou cancelar |
| `SystemComponent` | Componente técnico ou de processo afetado por tarefas e riscos |

A decisão mais importante foi a de **nunca conectar duas entidades diretamente sem um nó intermediário**. Uma `Person` não se liga a um `SystemComponent` — ela executa uma `Task` que afeta o componente. Isso forçou o grafo a ter semântica em cada aresta, não apenas topologia.

Os estados seguem uma progressão simples: `Pending → Active → Done | Resolved`. Todo nó nasce com estado e pode ser atualizado conforme novos documentos são processados.

**Trade-off:** a exigência de nós intermediários aumenta a densidade do grafo, mas torna cada conexão interpretável por humanos. Um grafo com arestas diretas seria mais simples de gerar, mas perderia a narrativa de *por que* duas entidades estão conectadas.

---

### Estratégia de Extração

O pipeline de extração tem dois estágios:

**1. Extração por LLM (Gemini 2.5 Flash)**

O modelo recebe um system prompt com as regras ontológicas e retorna um JSON estruturado com três seções: `new_entities`, `new_relationships` e `status_updates`. A escolha por structured output (forçando `application/json` via `response_mime_type`) elimina a necessidade de parsing defensivo e torna o pipeline determinístico.

Usei um único prompt em vez de uma cadeia de prompts. A vantagem é simplicidade e menor latência. O custo é que um prompt único tem menos espaço para raciocinar sobre cada entidade individualmente — mas para o escopo do MVP, a qualidade foi satisfatória.

**2. Contexto acumulado (sistema aprende)**

Antes de cada extração, o sistema busca no Neo4j todas as entidades com status ativo e injeta essa lista no prompt como "EXISTING KNOWLEDGE BASE". O modelo é instruído a reutilizar os IDs existentes em vez de criar duplicatas.

Isso resolve o problema mais concreto de aprendizado: na décima reunião, o modelo já sabe que "Marina" é `marina_costa` com experiência em Salesforce API, e não precisa inferir isso novamente. Também permite que o modelo detecte evoluções de estado — se um risco aparece pela segunda vez com mais gravidade, ele pode gerar um `status_update` em vez de criar uma entidade duplicada.

**Trade-off de formato:** reuniões e chats têm estruturas diferentes, mas optei por não criar pipelines separados. O mesmo prompt lida com os dois — reuniões tendem a gerar mais `new_entities` formais e chats geram mais `status_updates` e riscos emergentes. Na prática isso funcionou bem nos testes, mas um pipeline específico por tipo provavelmente extrairia nuances de chat (timestamps, tom informal, blockers emergentes) com mais precisão.

---

### Schema do Banco

Usei Neo4j como banco de grafos. A escolha foi direta: o dado é intrinsecamente um grafo, e forçá-lo em um modelo relacional ou documento implicaria joins ou lookups artificiais para reconstruir as relações.

Cada nó tem:
- `id` (snake_case, gerado pelo LLM, usado como chave de MERGE)
- `name`
- `status`
- `created_at` (ISO timestamp, definido na primeira inserção via `coalesce`)
- `completed_at` (ISO date, definido quando o status muda para `Done` ou `Resolved`, extraído do documento quando disponível)

Proposals são armazenados como nós `:Proposal` separados, fora do grafo principal. O ID é um hash MD5 da mensagem — isso garante idempotência ao reprocessar o mesmo documento.

**Trade-off:** usar o ID gerado pelo LLM como chave de MERGE é conveniente mas frágil. Se o modelo gerar `marina_costa` numa extração e `marina` na seguinte, cria um nó duplicado. O contexto acumulado mitiga isso, mas não elimina completamente — em produção, um sistema de resolução de entidades (entity resolution) seria necessário.

---

### Raciocínio sobre o Grafo

O sistema propõe ações em dois níveis:

1. **Proposals por documento** — gerados pelo Gemini durante a extração, com base no conteúdo imediato do documento. Classificados em `risk`, `task` e `bottleneck`.

2. **Visualização de estado** — dois grafos complementares: o estado ativo (apenas entidades `Pending`/`Active`) e o histórico completo (incluindo `Done`/`Resolved` em cinza). A distinção permite que um gestor veja o que precisa de atenção agora versus o que já foi resolvido.

O que não foi implementado mas foi considerado: detecção de padrões cross-documentos (ex: "TechNova aparece como risco em 3 reuniões seguidas") exigiria uma query de agregação sobre o histórico do Neo4j e um segundo prompt de raciocínio. A arquitetura suporta isso — é uma extensão natural do contexto acumulado.

---

### Stack

| Componente | Escolha | Motivo |
|---|---|---|
| LLM | Gemini 2.5 Flash | Suporte nativo a structured output via `response_mime_type`, boa capacidade de seguir schemas complexos |
| Banco | Neo4j | Dado é um grafo — modelagem nativa elimina joins artificiais |
| Grafo em memória | NetworkX | Manipulação de componentes conectados para posicionamento visual |
| UI | Streamlit | Prototipagem rápida com componentes interativos sem frontend separado |
| Visualização | streamlit-agraph | Renderização de grafos interativos com física configurável |
