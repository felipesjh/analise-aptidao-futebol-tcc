# Plano de Revisão do TCC — Diagnóstico, Checklist e Prompt para o Antigravity

> Documento gerado para apoiar a revisão solicitada pela banca (nota 5,8, em recuperação).
> Parecer central: **Arthur Henrique De Andrade Melani** — falta de normalização adequada, variáveis
> insuficientes/pouco representativas, ausência de análise por posição, baixa capacidade discriminativa.

---

## 1. Diagnóstico técnico dos 3 problemas apontados

### 1.1 "Não foi realizada normalização adequada"

**O que o professor quis dizer:** a transformação `/90` (ex: `Gols_90 = Gols / (Min/90)`) é uma
**conversão de taxa** — ela controla o tempo em campo, não a escala estatística da variável. Isso é
uma etapa de *engenharia de atributos*, não de *normalização/padronização*.

Normalização (no sentido estatístico que ele cobrou) significa colocar todas as variáveis numéricas
em uma escala comparável antes de entrar no modelo — tipicamente via `StandardScaler` (média 0,
desvio-padrão 1) ou `MinMaxScaler`.

**Por que isso importa, tecnicamente:**
- A `LogisticRegression` do scikit-learn aplica regularização L2 por padrão (parâmetro `C`). A
penalidade atua sobre a magnitude bruta dos coeficientes. Variáveis com faixa de valores grande
(ex: `Idade`, 16–40) e variáveis com faixa pequena (ex: `Cartões_Vermelhos_90`, ~0–0,05) recebem
penalização desproporcional se não forem escalonadas — isso distorce quais variáveis "parecem"
importantes pelos coeficientes e pode prejudicar a convergência do solver.
- **Isso não afeta o Random Forest da mesma forma.** Árvores de decisão cortam por limiar em cada
variável isoladamente — são invariantes a escala monotônica. Portanto, escalonar as features
provavelmente **não vai mudar significativamente os 52,78% do Random Forest**. O ganho de
padronizar é sobretudo para a Regressão Logística (interpretabilidade dos coeficientes/Odds Ratio
e estabilidade de otimização).

**Implicação prática para a meta de acurácia:** trate a padronização como correção metodológica
obrigatória (ela estava de fato ausente e é uma falha real), mas **não a trate como a alavanca
principal para sair de ~52% para 80%**. Essa alavanca está nos itens 1.2 e 1.3 abaixo.

**Como implementar sem vazamento de dados:** ajuste (`fit`) o `StandardScaler` **apenas no conjunto
de treino (2010–2020)** e aplique (`transform`) essa mesma transformação ao teste (2021–2024). Nunca
ajuste o scaler nos dados de teste — isso seria vazamento temporal, o mesmo erro conceitual que você
já evitou com o Out-of-Time.

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression

colunas_numericas = ["Idade", "Gols_90", "Ast_90", "Cartões_Amarelos_90",
                      "Cartões_Vermelhos_90", "Starts_Pct", "Minutagem_Real_Pct"]
colunas_dummy = ["Pos_Atacante", "Pos_Meio Campo", "Pos_Defensor", "Pos_Goleiro"]

preprocessador = ColumnTransformer([
    ("num", StandardScaler(), colunas_numericas),
    ("dummy", "passthrough", colunas_dummy),
])

pipeline_lr = Pipeline([
    ("preprocessamento", preprocessador),
    ("modelo", LogisticRegression(max_iter=1000)),
])

pipeline_lr.fit(X_treino, y_treino)   # fit só no treino (2010-2020)
pipeline_lr.score(X_teste, y_teste)   # transform aplicado ao teste (2021-2024)
```

Para o Random Forest, mantenha sem scaler (ou use o mesmo `Pipeline` sem alterar o resultado —
serve para consistência de código, não para ganho de acurácia).

---

### 1.2 "Variáveis não são suficientemente relevantes"

O FBref disponibiliza, além das tabelas de estatística padrão (`Standard Stats`) que você usou,
outras tabelas por temporada que agregam métricas mais discriminativas:

| Tabela FBref | Métricas relevantes a incorporar |
|---|---|
| `Shooting` | xG, xG/90, Chutes no gol %, Distância média de finalização |
| `Passing` | Passes progressivos, % de conclusão de passes, Passes-chave, xAG |
| `Passing Types` | Passes sob pressão, cruzamentos |
| `Defensive Actions` | Desarmes, interceptações, bloqueios, duelos aéreos ganhos % |
| `Possession` | Conduções progressivas, toques por terço de campo, dribles bem-sucedidos % |
| `Goal and Shot Creation` | SCA90 (ações de criação de chute), GCA90 (ações de criação de gol) |
| `Keepers` / `Keepers Adv` | Defesas %, PSxG, PSxG+/-, gols sofridos/90, % de lançamentos longos |

**Justificativa a registrar no TCC:** essas variáveis já são "macro" (agregadas por temporada,
públicas, sem necessidade de tracking/GPS) — portanto não contradizem a delimitação de escopo que
você já havia declarado (exclusão de dados de rastreamento óptico). Isso responde diretamente à
crítica sem exigir os feeds privados (Opta/Wyscout/StatsBomb) que você já havia colocado como
"trabalhos futuros" — você está apenas usando mais tabelas do **mesmo portal público** que já
utilizou.

---

### 1.3 "Ausência de análise por posição"

O parecer pede segmentação em **4 grupos: goleiro, defensor, meio-campista, atacante** — os mesmos
grupos que você já usa como dummies one-hot. **Você não precisa (e a banca não pediu) diferenciar
lateral de zagueiro.** O que falta é sair de "posição como covariável dentro de um modelo único" para
"**um pipeline de treino/teste por posição**", cada um com seu próprio conjunto de features
relevantes:

| Grupo | Features específicas prioritárias |
|---|---|
| Goleiro | Defesas %, PSxG+/-, gols sofridos/90, Starts_Pct, Minutagem_Real_Pct |
| Defensor | Desarmes/90, interceptações/90, bloqueios/90, duelos aéreos %, passes progressivos/90, Cartões/90, Gols_90 e Ast_90 (com peso menor, mas presentes) |
| Meio-campista | Passes progressivos/90, % conclusão de passes, SCA90, desarmes+interceptações/90, Ast_90 |
| Atacante | Gols_90, xG/90, SCA90, GCA90, dribles bem-sucedidos %, Starts_Pct |

Isso resolve por construção o caso do "zagueiro que joga de lateral e faz gol": dentro do subconjunto
"Defensor", o próprio modelo (Random Forest, via importância de Gini) vai aprender o peso real de
`Gols_90`/`Ast_90` para aquele grupo — sem você precisar definir pesos manualmente, o que seria
menos defensável estatisticamente do que deixar o algoritmo estimar isso a partir dos dados.

**Métricas a reportar por grupo** (não apenas acurácia global): acurácia, F1, matriz de confusão e
importância de atributos (Gini) **separadamente para cada um dos 4 modelos**, além da acurácia
global ponderada. Isso é o que fecha a lacuna "análise adequada dos resultados por posição".

---

## 1.4 Restrição inegociável: resultado próximo de 50–60% não é aceitável

Um resultado nessa faixa é estatisticamente equivalente a "jogar moeda" e não pode ser entregue de
novo à mesma banca, independentemente de qual narrativa teórica o acompanhe. As alavancas abaixo
estão **ordenadas por impacto esperado sobre a acurácia**, da mais para a menos relevante. Nenhuma
delas garante um número específico isoladamente — mas a combinação das três primeiras é o que tem
maior chance real de tirar o resultado da zona de "coin flip".

### Alavanca 1 (maior impacto esperado): contexto de equipe/adversário

A própria "teoria da auto-equivalência divisional" do trabalho original aponta a causa raiz, só que
na direção errada — ela foi usada para *justificar* o resultado fraco, quando deveria apontar **qual
variável está faltando**. Se o desempenho individual bruto se equivale entre divisões porque cada
jogador se ajusta ao nível médio da própria divisão, então **a qualidade do time/adversário é
exatamente a variável que falta** para separar as classes. Hoje o modelo não enxerga absolutamente
nada sobre o contexto coletivo em que aquela estatística individual foi produzida.

Atributos a incluir (públicos, no FBref, tabela de classificação por temporada):
- Posição final do clube na tabela naquela temporada
- Pontos por jogo do clube
- Saldo de gols do clube (gols pró − gols contra)
- Gols pró/jogo e gols contra/jogo do clube

Isso quebra a sobreposição estatística de forma muito mais direta do que adicionar apenas mais
métricas individuais (Alavanca 2), porque ataca a causa que o próprio trabalho já identificou.

### Alavanca 2: enriquecimento de atributos individuais (xG, SCA/GCA, ações defensivas — seção 1.2)

Aumenta o sinal disponível por jogador, mas sozinha tende a manter a mesma sobreposição entre
divisões se o contexto de equipe continuar ausente.

### Alavanca 3: segmentação por posição (seção 1.3)

Reduz heterogeneidade dentro do modelo (goleiro e atacante têm distribuições muito diferentes sendo
forçadas no mesmo classificador hoje). Tende a ajudar de forma real, não apenas formal — mas o
ganho maior aparece quando combinada com as Alavancas 1 e 2, não isoladamente.

### Alavanca 4: Gradient Boosting (XGBoost/LightGBM) com tuning correto

Ganho tipicamente incremental (poucos pontos percentuais) sobre Random Forest/Regressão Logística
quando o conjunto de features é o mesmo. Vale testar, mas não é a alavanca principal.

### O que NÃO fazer, mesmo sob pressão de prazo

- **Não reajustar hiperparâmetros repetidamente olhando o resultado no teste 2021–2024** até o
número "melhorar" — isso é vazamento de dados por p-hacking e é exatamente o tipo de fragilidade
que este examinador, que já identificou uma justificativa pós-hoc fraca, tem boa chance de detectar
de novo.
- **Não restringir a amostra para excluir casos "difíceis"/de fronteira** sem uma justificativa
metodológica independente do resultado (isso é gerrymandering estatístico).
- Se, mesmo após as três primeiras alavancas aplicadas com rigor, a acurácia agregada ainda ficar
abaixo do aceitável, **não maquiar o número** — estruture a apresentação de resultados em torno da
análise por posição (ver seção 1.3): é comum que alguns grupos (ex: goleiros, pelo sinal forte de
Defesas% e PSxG) discriminem consideravelmente melhor que outros, e isso é uma conclusão legítima
e defensável mesmo que a média global ainda não seja perfeita.

---

## 1.5 Plano de escalonamento, se o Plano A não for suficiente

As alavancas 1–4 da seção 1.4 formam o **Plano A**. Se, mesmo aplicando as três primeiras com
rigor, a acurácia agregada continuar na faixa de 50–60%, escale para o Plano B. Se ainda assim não
sair dessa faixa, vá para o Plano C. Trate isso como uma escada — não pule direto para o Plano C sem
esgotar o A e o B, porque o Plano C exige negociar escopo com a orientadora e consome mais tempo dos
30 dias que você tem.

### Plano B: sinal temporal do próprio jogador (autocorrelação de carreira)

Hoje cada linha (jogador-temporada) é tratada como um evento isolado. Isso ignora um fato estatístico
forte: a maioria dos jogadores permanece na mesma divisão de uma temporada para a outra. Incorporar
isso é legítimo (é informação passada prevendo o presente, não vazamento temporal) e tende a ter alto
impacto na acurácia:

- **`Divisao_Temporada_Anterior`**: divisão em que o jogador atuou na temporada anterior (ou "N/A"
  para estreantes — tratar como categoria própria, não como zero).
- **`Delta_Gols_90`, `Delta_Ast_90`, `Delta_Starts_Pct`**: variação das métricas em relação à
  temporada anterior do mesmo jogador (proxy de tendência de carreira: ascensão, estabilidade ou
  declínio).
- **`Idade_x_Delta`**: interação entre idade e a tendência acima (jogadores mais velhos com tendência
  de queda vs. jovens em ascensão têm dinâmicas diferentes).

**Armadilha a evitar:** não reporte apenas "acurácia subiu ao incluir divisão anterior" como se fosse
mérito do modelo. Reporte como um **baseline mais rigoroso**:

1. Baseline Zero-R (já existe): 50,65%.
2. **Novo baseline "Persistência"**: um classificador ingênuo que prevê "mesma divisão da temporada
   anterior" (sem olhar nenhuma estatística de desempenho). Calcule a acurácia desse baseline.
3. Modelo completo (com estatísticas de desempenho + contexto de equipe + divisão anterior): deve
   superar **o baseline de Persistência**, não apenas o Zero-R. Essa é a prova que realmente importa
   cientificamente — demonstra que o desempenho individual carrega sinal *além* da inércia natural de
   carreira, que é exatamente o que a banca está cobrando.

Isso fortalece o trabalho de duas formas ao mesmo tempo: eleva a acurácia agregada E te dá uma
comparação metodologicamente mais defensável do que a que a banca já criticou.

### Plano C (último recurso — negociar com a orientadora antes de implementar)

Se mesmo com os Planos A e B a acurácia agregada continuar baixa, os problemas passam a ser de
formulação do problema, não de features, e exigem decisão conjunta com a Profª Flávia antes de mudar
o texto do TCC:

- **Valor de mercado como atributo externo** (ex: Transfermarkt, se acessível publicamente): usar o
  valor de mercado do jogador **anterior** à temporada avaliada (nunca concorrente ou posterior, para
  não vazar a variável-alvo, já que valor de mercado já embute percepção de qualidade do jogador).
  Precisa de justificativa explícita no texto sobre por que isso não é redundante com a variável-alvo.
- **Reportar o resultado principal apenas nos grupos posicionais que discriminam bem** (ex: se
  goleiros chegarem a 75% e atacantes a 70%, mas defensores ficarem em 58%), e tratar o grupo fraco
  como um achado honesto e discutido, não escondido — isso é uma conclusão científica legítima e
  ainda assim evita entregar um número agregado de "coin flip" como resultado central do trabalho.
- **Não** tente resolver isso reduzindo a amostra para excluir casos difíceis ou reformulando o alvo
  de um jeito que não passe pela orientadora — mudanças de escopo desse porte, feitas sozinho e sem
  aval, são um risco maior do que apresentar o número atual com uma discussão honesta.

---

## 2. Checklist de revisão metodológica

- [ ] **[SE O PLANO A NÃO FOR SUFICIENTE] Plano B — sinal temporal de carreira**: incorporar
`Divisao_Temporada_Anterior`, `Delta_Gols_90`, `Delta_Ast_90`, `Delta_Starts_Pct`. Implementar
também o **baseline de Persistência** ("mesma divisão do ano anterior") e reportar a acurácia do
modelo completo comparada a esse baseline, não apenas ao Zero-R.
- [ ] **[PRIORIDADE MÁXIMA] Contexto de equipe**: incorporar posição na tabela, pontos/jogo, saldo
de gols e gols pró/contra por jogo do clube do jogador, naquela temporada, extraídos da tabela de
classificação do FBref. Esta é a alavanca com maior potencial de tirar o resultado da faixa de
"coin flip" (ver seção 1.4).
- [ ] **Padronização (StandardScaler)** aplicada via `Pipeline`/`ColumnTransformer`, `fit` apenas
no treino (2010–2020), `transform` no teste (2021–2024). Documentar por que afeta a Regressão
Logística e não o Random Forest.
- [ ] **Enriquecimento de atributos**: baixar/incorporar ao menos as tabelas `Shooting`, `Passing`,
`Defensive Actions`, `Goal and Shot Creation` e `Keepers`/`Keepers Adv` do FBref para as mesmas
temporadas/divisões já coletadas.
- [ ] **Segmentação por posição**: treinar 4 pipelines separados (Goleiro / Defensor / Meio-campista
/ Atacante), cada um com Out-of-Time próprio (treino 2010–2020, teste 2021–2024) e conjunto de
features específico da posição.
- [ ] **Validação de hiperparâmetros sem vazamento**: usar uma fatia de validação dentro do próprio
treino (ex: treinar 2010–2018, validar 2019–2020) ou `TimeSeriesSplit`. **Rodar o teste 2021–2024
uma única vez, no final**, para cada modelo definitivo.
- [ ] **Métricas por posição**: acurácia, F1, precisão, recall, matriz de confusão e importância de
atributos (Gini) reportadas separadamente para cada um dos 4 grupos, além da métrica global agregada.
- [ ] **(Opcional, se der tempo) Testar Gradient Boosting** (XGBoost ou LightGBM) por posição, para
comparar com Random Forest — você já havia citado isso como trabalho futuro; adiantar isso fortalece
a resposta à banca sobre "baixa capacidade discriminativa".
- [ ] **Revisar o Web-App Streamlit**: o buscador/simulador deve refletir a segmentação por posição
(ex: ao selecionar "Goleiro", o simulador mostra sliders de Defesas% e PSxG, não de Gols/90).
- [ ] **Reescrever a seção de "Justificativa dos Resultados"** com um parágrafo explícito respondendo
ponto a ponto ao parecer da banca (modelo de texto abaixo).
- [ ] **Não ajustar hiperparâmetros olhando repetidamente para o teste 2021–2024** — documentar no
texto que a validação seguiu o protocolo acima, para deixar claro à banca que não houve reajuste
até "acertar" o número.

### Modelo de parágrafo para a seção de resultados (adaptar)

> *"Em resposta ao parecer da banca examinadora, esta versão revisada do trabalho incorpora três
> mudanças metodológicas centrais: (i) padronização das variáveis numéricas via StandardScaler,
> ajustada exclusivamente no conjunto de treinamento para evitar vazamento temporal; (ii) inclusão
> de atributos adicionais extraídos de tabelas complementares do FBref (xG, passes progressivos,
> ações de criação de chute/gol, métricas defensivas e de goleiro), ampliando a representatividade
> das variáveis utilizadas; e (iii) segmentação da modelagem em quatro pipelines independentes por
> grupo posicional (goleiros, defensores, meio-campistas, atacantes), cada um treinado e validado
> sob o mesmo paradigma Out-of-Time (2010–2020 / 2021–2024), permitindo que a relevância de cada
> atributo seja aprendida de forma específica ao papel tático do jogador."*

---

## 3. Prompt pronto para o Antigravity

Cole o bloco abaixo integralmente. Ele foi escrito para um agente de codificação (assume acesso ao
repositório do projeto e aos scripts `src/modelagem/executar_pipeline.py` e `analisar_perfil`).

```
Contexto: este é um TCC de MBA em Data Science que prevê a aptidão divisional (Série A vs. Série B)
de jogadores de futebol brasileiro usando Regressão Logística e Random Forest, com validação
Out-of-Time (treino 2010–2020, teste 2021–2024). O trabalho voltou da banca em recuperação com nota
5,8 — a acurácia atual (~52,78%) é estatisticamente equivalente a "jogar moeda" e é INACEITÁVEL na
resubmissão, independentemente de qualquer justificativa teórica. Preciso corrigir o seguinte, na
ordem de prioridade abaixo:

0. [PRIORIDADE MÁXIMA] Falta contexto de equipe/adversário. O modelo hoje só enxerga estatística
   individual bruta, sem nenhuma informação sobre a qualidade do time em que o jogador atuou. Preciso
   incorporar, para o clube do jogador naquela temporada: posição final na tabela, pontos por jogo,
   saldo de gols, gols pró/jogo e gols contra/jogo, extraídos da tabela de classificação do FBref
   (ou de outra fonte pública equivalente, documentando a fonte). Esta é a alavanca com maior
   potencial de elevar a capacidade discriminativa do modelo, porque ataca diretamente o problema de
   sobreposição estatística entre divisões que o próprio trabalho já havia identificado.
1. Falta padronização estatística das variáveis (StandardScaler), distinta da normalização /90 já
   aplicada (que é só conversão de taxa por tempo em campo).
2. As variáveis usadas (idade, gols/90, assistências/90, cartões/90, titularidade, minutagem) são
   insuficientes. Preciso incorporar atributos adicionais das tabelas do FBref: Shooting (xG,
   xG/90), Passing (passes progressivos, % de conclusão, xAG), Defensive Actions (desarmes,
   interceptações, bloqueios, duelos aéreos %), Goal and Shot Creation (SCA90, GCA90), e
   Keepers/Keepers Adv (defesas %, PSxG+/-, gols sofridos/90) para goleiros.
3. Falta segmentar a modelagem por posição: preciso treinar 4 pipelines independentes (Goleiro,
   Defensor, Meio-campista, Atacante), cada um com seu próprio conjunto de features relevantes
   (ver tabela abaixo), mantendo o protocolo Out-of-Time (treino 2010–2020, teste 2021–2024) dentro
   de cada grupo.

IMPORTANTE: não ajuste hiperparâmetros olhando repetidamente o resultado no conjunto de teste
2021–2024, e não restrinja a amostra para excluir casos "difíceis" apenas para inflar a métrica —
ambos seriam vazamento/viés metodológico detectável. Se, mesmo após as mudanças acima aplicadas
corretamente, a acurácia agregada ainda ficar baixa, reporte isso honestamente nas métricas por
posição (item 2 das tarefas abaixo) em vez de mascarar o número.

Tabela de features por posição:
- Goleiro: Defesas_Pct, PSxG_Diff, Gols_Sofridos_90, Starts_Pct, Minutagem_Real_Pct, Idade
- Defensor: Desarmes_90, Interceptacoes_90, Bloqueios_90, Duelos_Aereos_Pct, Passes_Progressivos_90,
  Cartoes_Amarelos_90, Cartoes_Vermelhos_90, Gols_90, Ast_90, Starts_Pct, Idade
- Meio-campista: Passes_Progressivos_90, Pct_Conclusao_Passes, SCA90, Desarmes_90, Interceptacoes_90,
  Ast_90, Gols_90, Starts_Pct, Idade
- Atacante: Gols_90, xG_90, SCA90, GCA90, Dribles_Sucesso_Pct, Starts_Pct, Idade

Tarefas que preciso que você execute no repositório:

1. Revisar `src/modelagem/executar_pipeline.py` para:
   a0. Criar/atualizar um script de ingestão para a tabela de classificação do FBref (ou fonte
      pública equivalente) por temporada e divisão, extraindo posição final, pontos/jogo, saldo de
      gols, gols pró/jogo e gols contra/jogo por clube. Unir esses atributos à base de
      jogadores-temporada pelo campo (clube, temporada, divisão). Tratar temporadas/clubes sem dado
      disponível de forma explícita (não preencher com zero silenciosamente).
   a. Construir um `ColumnTransformer` com `StandardScaler` aplicado às variáveis numéricas contínuas,
      ajustado (`fit`) apenas nos dados de treino (2010–2020) e aplicado (`transform`) ao teste
      (2021–2024). Não escalonar as dummies one-hot de posição. Aplicar esse pré-processamento
      apenas ao pipeline da Regressão Logística (documentar no código, em comentário, por que o
      Random Forest não precisa: é invariante a escala monotônica das features).
   b. Adicionar um passo de ingestão para as tabelas adicionais do FBref listadas acima, unindo-as
      à base existente por (jogador, temporada, equipe). Se alguma tabela não estiver disponível
      nos dados já coletados, criar um script de ingestão separado seguindo o mesmo padrão de
      extração assistida via CSV já usado no projeto (por causa do bloqueio Cloudflare 403 do
      FBref), e documentar isso no README.
   c. Refatorar a modelagem para treinar 4 pipelines independentes por grupo posicional, cada um
      com seu próprio Random Forest e Regressão Logística, seguindo o protocolo Out-of-Time
      (treino 2010–2020, teste 2021–2024) dentro de cada subconjunto.
   d. Para ajuste de hiperparâmetros, usar apenas uma fatia de validação dentro do período de treino
      (ex: treinar em 2010–2018, validar em 2019–2020, via GridSearchCV com um split manual ou
      TimeSeriesSplit) — NUNCA usar o conjunto de teste 2021–2024 para escolher hiperparâmetros.
      O teste 2021–2024 deve ser avaliado uma única vez, no final, por modelo definitivo.

2. Atualizar a geração de métricas para produzir, por grupo posicional: acurácia, F1-score,
   precisão, recall, matriz de confusão, e importância de atributos (Gini) do Random Forest.
   Salvar essas métricas em uma tabela consolidada (ex: `resultados/metricas_por_posicao.csv`).

3. Atualizar o Web-App Streamlit (`analisar_perfil` e as abas relacionadas) para que o Dossiê
   Individual e o Simulador de Cenários usem o pipeline e as features específicas da posição do
   jogador selecionado, em vez do modelo genérico único.

4. Não alterar a estrutura da base de dados de forma que rompa a reprodutibilidade da versão
   anterior — manter compatibilidade com `data/nova_base/` usada nos estudos de caso longitudinais
   dos 8 atletas.

Após implementar os itens 0–4 acima (Plano A), gere a tabela de métricas por posição. SE a acurácia
agregada continuar abaixo de um patamar claramente superior a "chance" (ex: abaixo de ~65%), execute
também o Plano B abaixo antes de me entregar o resultado final:

PLANO B (condicional, só executar se o Plano A não for suficiente):
5. Adicionar as features `Divisao_Temporada_Anterior`, `Delta_Gols_90`, `Delta_Ast_90` e
   `Delta_Starts_Pct` (diferença em relação à temporada anterior do mesmo jogador; usar categoria
   própria "estreante" quando não houver temporada anterior — nunca preencher com zero).
6. Implementar um classificador baseline adicional chamado "Persistência", que prevê simplesmente a
   mesma divisão da temporada anterior do jogador (sem usar nenhuma estatística de desempenho).
   Reportar a acurácia desse baseline lado a lado com o Zero-R (50,65%) e com o modelo completo, para
   cada grupo posicional e agregado. O objetivo é demonstrar que o modelo completo supera não só o
   Zero-R, mas também esse baseline mais rigoroso.

Em nenhuma hipótese remova casos "difíceis" da amostra ou reformule o alvo de classificação para
inflar a métrica — se após os Planos A e B a acurácia agregada ainda for baixa, gere o relatório por
posição mesmo assim, de forma honesta, sinalizando quais grupos discriminam bem e quais não.


Ao final, gere um resumo em markdown (`docs/revisao_banca/log_alteracoes.md`) listando: (a) quais
tabelas/atributos novos foram incorporados, (b) a acurácia obtida por posição antes e depois das
mudanças, e (c) quaisquer limitações remanescentes (ex: atributos que não estavam disponíveis para
todas as temporadas/divisões).
```

---

## 4. Estrutura de pasta sugerida para os pareceres das IAs

Para comparar as respostas de Claude, Gemini e ChatGPT de forma organizada dentro do repositório:

```
docs/
└── revisao_banca/
    ├── parecer_banca_original.md          <- texto do parecer do Arthur Melani (cole aqui)
    ├── checklist_e_prompt_claude.md       <- este arquivo
    ├── pitacos_gemini.md
    ├── pitacos_chatgpt.md
    ├── pitacos_claude_seguimento.md       <- respostas de acompanhamento, se pedir mais rodadas
    ├── log_alteracoes.md                  <- gerado pelo Antigravity ao final (item 4 do prompt)
    └── metricas_por_posicao.csv           <- métricas finais, para anexar à monografia revisada
```

Sugestão: ao terminar de rodar as mudanças, cole as métricas finais (`metricas_por_posicao.csv`)
de volta em uma nova conversa aqui e eu te ajudo a comparar se os números batem com o que os outros
dois modelos de IA sugeriram, e a redigir a seção final de "Justificativa de Resultados" da
monografia revisada.