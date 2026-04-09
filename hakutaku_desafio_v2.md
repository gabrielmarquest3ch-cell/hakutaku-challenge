# 🧠 Hakutaku AI — Desafio Técnico

## Sobre a Hakutaku

A Hakutaku AI está construindo um **Organizational Intelligence Layer**.

A premissa é simples: empresas produzem enormes quantidades de conhecimento todos os dias — em reuniões, documentos, conversas, tickets — mas quase nada disso se transforma em ação de forma estruturada. Decisões se perdem. Riscos passam despercebidos. Tarefas ficam sem dono.

Nós acreditamos que existe um caminho entre **conhecimento organizacional bruto** e **ação operacional**, e que esse caminho passa por modelagem ontológica + IA.

Não estamos construindo um chatbot. Não estamos construindo um sistema de notas. Estamos construindo um sistema que **modela como uma organização pensa e opera**.

---

## O Problema

Organizações geram conhecimento continuamente. Esse conhecimento está preso em formatos não-estruturados — atas de reunião, transcrições, docs, threads. Dentro desse conteúdo existem **objetos operacionais reais**: decisões, riscos, tarefas, dependências, compromissos, perguntas sem resposta.

O problema é que ninguém extrai esses objetos de forma sistemática, e muito menos os conecta entre si ao longo do tempo.

Sua missão é construir um sistema que resolva isso.

---

## O que Esperamos

Construa um sistema que:

1. **Receba conhecimento organizacional não-estruturado** (transcrições de reunião, documentos, ou qualquer formato que você escolher)

2. **Modele esse conhecimento como um grafo ontológico** — entidades tipadas com estados, metadados e relações entre si

3. **Raciocine sobre esse grafo** — detecte padrões, gaps, inconsistências, evoluções temporais

4. **Proponha ações** — a partir do raciocínio sobre o grafo, gere sugestões concretas de próximos passos

5. **Mostre tudo isso em uma interface** que permita a um humano entender o estado da organização e agir

6. **Aprenda com o tempo** — o sistema deve ficar mais inteligente quanto mais conhecimento organizacional ele processa. Ele não apenas armazena, ele acumula contexto. Na décima reunião, ele deveria entender a organização melhor do que na primeira.

---

## O que NÃO Esperamos

- Não esperamos que você construa algo production-ready
- Não esperamos deploy, CI/CD, ou infraestrutura sofisticada
- Não esperamos cobertura de testes de 90%

Esperamos que você **pense profundamente sobre o problema**, tome **decisões de modelagem fundamentadas**, e construa algo que **funcione end-to-end** mesmo que com escopo reduzido.

---

## Decisões que São Suas

Este desafio é intencionalmente aberto. As seguintes decisões são **suas**:

**Modelagem ontológica** — Quais tipos de entidade existem? Quais estados cada tipo pode ter? Quais relações fazem sentido? Você pode usar a ontologia que quiser, desde que justifique suas escolhas. Não existe resposta certa — existe resposta fundamentada.

**Formato de input e estratégia de ingestion** — O sistema precisa lidar com pelo menos dois formatos diferentes de input (transcrições de reunião e threads de chat). Como você normaliza conhecimento que vem de fontes com estruturas completamente diferentes? Uma reunião tem começo, meio e fim. Um chat é um fluxo contínuo de mensagens ao longo de dias. As decisões de como tratar isso são suas.

**Stack tecnológica** — Use o que quiser. Qualquer linguagem, qualquer banco, qualquer framework, qualquer LLM. A escolha é sua, mas esteja preparado para explicar o porquê.

**Estratégia de extraction** — Um prompt? Vários prompts em cadeia? Um pipeline diferente por tipo de source? A abordagem é sua.

**Profundidade vs. Amplitude** — Prefere cobrir muitos tipos de entidade com extraction rasa, ou poucos tipos com extraction profunda? Prefere um grafo visualmente rico ou um engine de proposals sofisticado? Você decide onde investir seu tempo.

---

## O Sistema Aprende

Esse é talvez o ponto mais importante do desafio.

Um sistema de inteligência organizacional que processa a décima reunião da mesma forma que processou a primeira está falhando. Na décima reunião, o sistema já deveria saber quem são as pessoas, quais projetos existem, quais riscos estão abertos, quem costuma tomar quais tipos de decisão, quais clientes são recorrentes.

O que isso significa na prática: conforme o Knowledge Layer acumula entidades, relações e histórico, o sistema deveria usar esse contexto acumulado para:

- Fazer extraction mais precisa (se o sistema já sabe que "Marina" é "Marina Costa, engenheira de backend", ele não deveria precisar inferir isso de novo)
- Gerar proposals mais relevantes (se o sistema sabe que tasks do Pedro costumam atrasar, ele pode gerar alertas preventivos)
- Detectar padrões que só emergem com volume (o cliente TechNova é mencionado como risco em 3 reuniões seguidas, isso é um padrão)
- Resolver ambiguidades com mais confiança (se alguém menciona "o projeto" sem especificar qual, o contexto recente deveria resolver)

Não esperamos que você implemente tudo isso. Mas esperamos que você **pense** sobre isso, **proponha** uma abordagem, e **implemente** pelo menos uma forma concreta do sistema usar conhecimento acumulado para ficar melhor.

---

## Dados de Teste

Use as transcrições abaixo para testar seu sistema. São duas reuniões fictícias da mesma equipe, separadas por 4 dias. Existem sobreposições intencionais entre elas — mesmas pessoas, mesmo projeto, evolução de decisões e riscos.

### Reunião 1 — Sprint Planning (24/03/2025)

```
Participantes: João Silva, Marina Costa, Pedro Almeida, Ana Ferreira
Duração: 45 minutos

João abre a reunião dizendo que precisam definir as prioridades do sprint para a integração com CRM.

Marina sugere começar pelo módulo de sincronização de contatos antes de deals. João concorda e aprova — contatos são pré-requisito e 3 clientes já pediram.

João decide alocar Marina exclusivamente pro backend da integração nas próximas 2 semanas, já que ela é a única com experiência na API do Salesforce.

Tarefas definidas:
- Marina vai criar o schema de mapeamento entre campos do CRM e entidades internas (deadline 28/03)
- Alguém precisa configurar o ambiente de staging pra testes (deadline 31/03, sem dono definido)
- Pedro vai documentar os endpoints disponíveis na API do cliente TechNova (deadline 02/04)

Pedro levanta um risco: o cliente TechNova pode cancelar o contrato se a integração não for entregue até abril. Severidade alta.

Ana levanta outro risco: Marina é single point of failure no conhecimento de Salesforce API.

Marina pergunta: devemos usar REST API ou GraphQL pra integração? GraphQL é mais flexível mas o time não tem experiência.

Marina também pergunta sobre rate limiting — precisamos do nosso próprio ou usamos o do CRM?

Dependência identificada: a integração depende do time de infra liberar o ambiente de staging.
```

### Reunião 2 — Weekly Sync (28/03/2025)

```
Participantes: João Silva, Marina Costa, Pedro Almeida, Lucas Mendes
Duração: 30 minutos

Marina reporta que completou o schema de mapeamento mas encontrou inconsistências nos dados do Salesforce.

Pedro informa que o cliente TechNova agendou uma call de escalação para a semana que vem. Situação crítica.

João decide que vão usar REST API (não GraphQL) — time não tem experiência e o prazo é curto.

João decide que Lucas vai fazer pair programming com Marina por 1 semana pra absorver o conhecimento de Salesforce. Isso mitiga o risco de single point of failure.

Pedro propõe antecipar uma entrega parcial pro TechNova — só sync de contatos, sem deals. Ainda não aprovado.

Tarefas novas:
- Marina: corrigir inconsistências no mapeamento do Salesforce (deadline 31/03)
- Pedro: preparar demo parcial de sync para a call com TechNova (deadline 03/04, prioridade crítica)
- Lucas: fazer setup do ambiente local e rodar testes existentes (deadline 31/03)
- Alguém precisa escrever testes de integração pro endpoint de sync (deadline 07/04, sem dono)

Riscos:
- TechNova agendou call de escalação — risco de churn agora é crítico
- Dados do Salesforce têm inconsistências que podem atrasar o mapeamento

Perguntas ainda abertas:
- Rate limiting: próprio ou do CRM? (sem definição ainda)
- Quem será o ponto de contato técnico na call com TechNova?

Dependências:
- Demo pro TechNova depende do staging estar pronto
- Onboarding do Lucas depende de acesso ao sandbox do Salesforce
```

### Thread de Chat — Canal #proj-crm-integration (25/03 a 29/03)

```
#proj-crm-integration

[25/03 09:12] marina.costa: pessoal, comecei o schema de mapeamento. a estrutura de contatos do Salesforce é mais complexa do que imaginei — eles têm Contact e Lead como objetos separados

[25/03 09:15] pedro.almeida: pra TechNova a gente usa qual? eles pediram sync de Contacts

[25/03 09:18] marina.costa: Contacts. mas tem uns campos custom que eles criaram que não mapeiam direto pros nossos. vou precisar de mais 1 dia

[25/03 11:43] joao.silva: @marina.costa sem problema, mas não pode passar de sexta. a gente prometeu pra Q2

[25/03 14:20] ana.ferreira: gente, o time de infra disse que o staging só fica pronto quarta que vem. perguntei pro Ricardo e ele disse que tão com o pipeline de CI travado

[25/03 14:22] pedro.almeida: quarta?? a gente precisa disso pra testar a integração. @joao.silva isso é blocker

[25/03 14:25] joao.silva: vou escalar com o Ricardo. isso não pode atrasar

[25/03 16:30] marina.costa: achei um problema — os dados de teste do Salesforce sandbox tão desatualizados. último refresh foi em janeiro. tem contatos que já foram deletados no prod

[25/03 16:33] pedro.almeida: eu posso pedir refresh pro time do cliente? ou é muito invasivo?

[25/03 16:35] marina.costa: melhor não. vou trabalhar com o que tem e flagar os inconsistentes

[26/03 10:00] pedro.almeida: update TechNova: falei com a Sarah (account manager deles) e ela disse que o VP de ops tá pressionando pra cancelar. ela conseguiu segurar mais 2 semanas mas precisa ver progresso tangível

[26/03 10:05] joao.silva: isso muda tudo. @pedro.almeida agenda uma call com eles pra semana que vem pra mostrar o que temos

[26/03 10:07] pedro.almeida: vou agendar. mas a gente tem algo pra mostrar? sync de contatos funciona?

[26/03 10:10] marina.costa: o mapeamento tá 70%. se eu terminar até sexta e tiver staging, consigo ter um demo parcial rodando segunda ou terça

[26/03 10:12] joao.silva: @marina.costa prioridade máxima nisso

[27/03 08:45] lucas.mendes: oi pessoal! o João me adicionou no projeto. vou fazer pair com a Marina pra pegar contexto de Salesforce. alguém me passa acesso ao repo e ao sandbox?

[27/03 08:50] marina.costa: @lucas.mendes bem-vindo! te mandei o invite pro repo. sandbox precisa pedir pro IT — abre ticket no ServiceDesk, template "External API Access"

[27/03 09:00] lucas.mendes: abri o ticket. disseram que demora 24-48h 😬

[27/03 15:30] ana.ferreira: descobri que o Salesforce tem rate limit de 100 requests por 15 segundos no plano do TechNova. isso é suficiente pra sync em batch?

[27/03 15:35] marina.costa: depende do volume. TechNova tem ~15k contatos. se cada sync pega 100 por request, são 150 requests. com rate limit de 100/15s dá pra fazer em ~25 segundos. acho que tá ok pra batch. mas e sync incremental em real-time?

[27/03 15:40] ana.ferreira: boa pergunta. precisamos definir se o MVP é batch only ou se precisa de webhook

[27/03 15:42] joao.silva: MVP é batch. webhook fica pra v2

[28/03 17:00] pedro.almeida: call com TechNova confirmada pra quinta 03/04 às 14h. vão estar o VP de ops e a Sarah. do nosso lado preciso de alguém técnico comigo

[28/03 17:05] joao.silva: eu vou. @marina.costa prepara uma demo do sync de contatos pra gente mostrar

[28/03 17:08] marina.costa: preciso do staging pra isso. @ana.ferreira tem update do infra?

[28/03 17:15] ana.ferreira: Ricardo disse que staging fica pronto amanhã de manhã. finalmente.

[29/03 09:00] marina.costa: staging tá no ar! começando a rodar os testes de mapeamento

[29/03 11:30] marina.costa: 🚨 achei um bug sério — o mapeamento tá duplicando contatos que têm caracteres especiais no nome (acentos, ç). preciso corrigir antes da demo

[29/03 11:35] lucas.mendes: consigo ajudar com isso, é provavelmente encoding UTF-8 vs Latin-1. me manda o código que olho

[29/03 14:00] marina.costa: @lucas.mendes boa! era isso mesmo. corrigimos juntos. sync rodando com 14.823 de 15.102 contatos mapeados corretamente. os 279 restantes têm dados incompletos no source

[29/03 14:05] pedro.almeida: 98.1% de accuracy no primeiro run. isso é ótimo pra demo. vou montar os slides

[29/03 16:00] joao.silva: bom trabalho pessoal. status final da semana: schema pronto, staging no ar, sync rodando com 98% accuracy. segunda refinamos e quinta é a demo pro TechNova. semana decisiva.
```

---

### Sobre os dados de teste

O sistema deve ser capaz de processar **ambos os formatos** — transcrições de reunião e threads de chat. A natureza do conhecimento contido em cada um é diferente:

- **Reuniões** tendem a conter decisões formais, atribuição de tarefas, levantamento explícito de riscos
- **Chats** contêm evolução em tempo real: status updates, descobertas técnicas, blockers emergentes, informação informal que nunca entra em ata

Um bom sistema extrai conhecimento de ambos e **cruza** as informações. Esses três inputs contam uma história contínua — e o desafio é fazer o sistema enxergar isso.

Alguns exemplos de nuances (não exaustivos):

- O risco de churn do TechNova **escalou** de "alto" para "crítico" entre as reuniões, o sistema deveria capturar essa mudança de estado
- A open question sobre REST vs GraphQL da reunião 1 foi **respondida** por uma decision na reunião 2, são duas entidades que se conectam
- O pair programming decidido na reunião 2 **acontece de fato** no chat (Lucas e Marina corrigem o bug juntos), conhecimento cruza fontes diferentes

Quanto mais dessas nuances seu sistema capturar e representar, melhor.

---

## Critérios de Avaliação

### 1. Pensamento sobre o problema (30%)

- Como você modelou a ontologia? Por que esses tipos, esses estados, essas relações?
- Quais trade-offs você identificou e como decidiu?
- Você antecipou problemas reais que surgem quando o sistema processa múltiplas fontes ao longo do tempo?
- Demonstrou compreensão do problema real ou apenas seguiu instruções?

### 2. Funciona end-to-end (30%)

- Input entra e output sai?
- Extraction produz entidades corretas?
- Relações fazem sentido?
- Proposals são relevantes?
- O sistema lida com múltiplos documentos sem quebrar?

### 3. Qualidade técnica (20%)

- Código organizado e legível
- Schema de banco coerente com a ontologia proposta
- Prompts bem construídos
- Tratamento de erros nos pontos críticos

### 4. Interface (20%)

A interface é onde a tese vira produto. É o que alguém de fora olha e entende (ou não) o valor do que foi construído.

- O design importa. Tipografia, espaçamento, hierarquia visual, cores com propósito. Não precisa ser obra de arte, mas precisa ser intencional
- A apresentação dos proposals deve ser clara o suficiente pra um gestor não-técnico entender e agir
- Nos impressione. A interface é o que a gente vai mostrar pra investidor, pra cliente, pra equipe. Se ela não impressiona, o sistema perde metade do impacto

---

## Entrega

### Prazo: 7 dias corridos

### Repositório no GitHub

- README com:
  - Como rodar o projeto
  - **Documento de decisões técnicas**: explique sua ontologia, sua estratégia de extraction, seu schema de banco, e os trade-offs que encontrou. Este documento é tão importante quanto o código.
- Código fonte completo
- Prompts utilizados (versionados, não hardcoded e escondidos)

---

## Última Coisa

Esse desafio não tem gabarito. Não existe uma ontologia certa, um schema certo, ou uma arquitetura certa. Existem decisões boas e decisões ruins, e a diferença entre elas é **fundamentação**.

Nos impressione.

*— Hakutaku AI*
