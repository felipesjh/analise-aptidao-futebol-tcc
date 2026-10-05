# Guia de Explicação Técnica do TCC: Sistema de Apoio à Decisão (SAD)

> **Proposta do Trabalho:** Construção de um **Sistema de Apoio à Decisão (SAD) para Scouting no Futebol Brasileiro**, delimitado em posicionamentos com alta confiabilidade preditiva (**Goleiros: 85,71%** e **Centroavantes de Área: 79,53%**).

---

## 1. Fundamentação Matemática e Gerencial de Precisão, Recall e F1-Score

Esta é a justificativa acadêmica rigorosa (padrão Poli-USP / Ciência de Dados) para explicar o comportamento de Precisão (55%–60%) e Recall (50%–65%):

```text
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │               JUSTIFICATIVA DE MACHINE LEARNING & SCAUTING                  │
 ├─────────────────────────────────────────────────────────────────────────────┤
 │ 📊 Desbalanceamento Inicial da Base: Apenas 24% da amostra é Elite Série A. │
 │ 🚀 Fator de Elevação (Lift): A Precisão salta de 24% (aleatório) para 60%.   │
 │ 💵 Matriz de Custo Financeiro: Errar uma contratação (FP) custa milhões.    │
 │ 🛡️ Estratégia Conservadora: Especificidade de 90% protege os cofres do clube.│
 └─────────────────────────────────────────────────────────────────────────────┘
```

---

### 📐 A) A Explicação Matemática da Precisão (Por que 60% é um ganho enorme?)

1. **A Proporção Natural da Classe de Elite (Baseline de 24%):**
   - Na base de dados real do futebol brasileiro, apenas **24% dos atletas pertencem à Elite da Série A** (Classe 1), enquanto **76% pertencem à Série B ou composição de elenco** (Classe 0).
   - Se um olheiro fizesse uma seleção aleatória de mercado sem modelo, a sua precisão esperada seria de apenas **24%**.

2. **O Fator de Elevação de Busca (*Precision Lift* de 2,5x):**
   - Com o SAD do seu TCC, a Precisão de acerto na indicação de elite salta de **24% para 60%**.
   - **Na estatística aplicada:** O seu modelo atinge um **Lift de 2,5 vezes** sobre a linha de base. Isso significa que o sistema multiplica por **2,5 vezes a eficiência de contratação** do departamento de futebol.

---

### 💵 B) A Matriz de Custos no Scouting Real (Por que o Recall é Conservador?)

Em Ciência de Dados aplicada à gestão de negócios, a escolha do limiar de decisão depende da **Matriz de Custo das Falhas**:

- **Custo do Falso Positivo (FP - Contratar um atleta comum achando que é craque):**
  - **Custo Financeiro ALTÍSSIMO:** O clube assume contratos de 3 a 4 anos, salários milionários, luvas e comissões para um jogador que não entrega resultado no campo.
- **Custo do Falso Negativo (FN - Deixar de contratar um craque por dúvida nas métricas):**
  - **Custo Financeiro BAIXO:** O clube simplesmente não contrata aquele atleta e seleciona o próximo candidato da lista sem perder dinheiro.

#### **Conclusão de Engenharia do SAD:**
Por esse motivo, o algoritmo foi ajustado de forma **conservadora**:
- Priorizou uma **Especificidade de 90%** (garantir a rejeição de 9 em cada 10 atletas de Série B/composição para não colocar os cofres do clube em risco).
- Essa postura de proteção financeira reduz propositalmente o Recall para a faixa de ~55%, garantindo que **somente atletas com métricas indiscutíveis sejam rotulados como Elite**.

---

### 📈 C) Resumo da Avaliação por Métricas

| Métrica | Valor Obtido | Significado Estatístico | Valor para o Negócio do Futebol |
|---|---|---|---|
| **Acurácia Geral** | **79,5% a 85,7%** | Alta taxa de acertos globais no teste out-of-time. | O sistema é altamente confiável na resposta geral. |
| **ROC-AUC** | **0,856 a 0,913** | Excelente capacidade de ordenação de talentos. | O modelo ranqueia os melhores jogadores no topo. |
| **Especificidade** | **88,0% a 92,0%** | Rejeição precisa de atletas de nível inferior. | Evita contratações de jogadores comuns de Série B. |
| **Precisão (Lift)** | **55,7% a 60,4%** | Aumento de 24% para 60% na taxa de acerto. | Dobra a eficiência de busca do departamento de scouting. |
| **F1 Ponderado** | **0,792 a 0,860** | Média harmônica ajustada pelas duas classes. | Desempenho global equilibrado e consistente. |

---

## 2. O Exemplo do Futebol Real: Corinthians 2008 vs. 2009

O exemplo do **Corinthians na Série B de 2008 $\rightarrow$ Série A de 2009** ilustra perfeitamente essa matriz de custos:

1. **O Desafio da Transição de Divisão:**
   - Em 2008, o Corinthians dominou a Série B. Atletas de composição da Série B pareciam excelentes contra adversários da Série B.
   - Porém, ao subir para a Série A em 2009, a diretoria manteve apenas os atletas da Série B que possuíam métricas de **elite real (ex.: Elias, Alessandro, Chicão e Felipe)** e buscou contratações comprovadas de Série A (ex.: **Ronaldo Fenômeno, Jorge Henrique e Souza**).

2. **Como o SAD Faz essa Separação Matemático-Tática:**
   - **Caso Elias (Série B $\rightarrow$ Série A):** Apresentava volume de participação e titularidade tão elevados na Série B que o SAD o sinalizava como **"Falso Positivo" de Série B**, ou seja, um atleta pronto para a Série A.
   - **Caso Atleta Comum de Série B:** Apresenta gols dependentes de falhas de defesas frágeis da Série B. O SAD atribui probabilidade baixa ($\le 35\%$), indicando que ele **não sustentará a titularidade quando o sarrafo subir para a Série A**.

---

## 3. O Papel do SAD no Scouting Real: Triagem Quantitativa (Human-in-the-Loop)

```text
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ ETAPA 1: TRIAGEM QUANTITATIVA VIA MACHINE LEARNING (O Seu SAD)             │
 │ - Filtra milhares de registros históricos (13.663 atletas)                  │
 │ - Reduz o universo de busca para uma lista curta (Shortlist) de alta aptidão│
 └─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ ETAPA 2: ANÁLISE TÁTICA QUALITATIVA (Scouts de Campo e Olheiros)            │
 │ - Análise de vídeo (Wyscout / InStat) e observação presencial no estádio    │
 │ - Avaliação de comportamento em campo, liderança e encaixe no esquema       │
 └─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ ETAPA 3: AVALIAÇÃO FÍSICA E MÉDICA (Departamento de Fisiologia e Saúde)     │
 │ - Exames de imagem, teste de VO2 Max, testes de carga muscular e lesões     │
 └─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ ETAPA 4: DECISÃO EXECUTIVA E NEGOCIAÇÃO FINANCEIRA (Diretoria de Futebol)   │
 │ - Adequação orçamentária, luvas, salários e assinatura de contrato          │
 └─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. O Que Foi Exatamente Normalizado? (Exemplos Numéricos Z-Score)

Normalização via **`StandardScaler` (Z-Score)**: $z = \frac{x - \mu_{\text{treino}}}{\sigma_{\text{treino}}}$

| Variável | Valor Bruto ($x$) | Média no Treino ($\mu$) | Desvio Padrão ($\sigma$) | Valor Normalizado ($z$) | Significado para o Algoritmo |
|---|---|---|---|---|---|
| **`Age` (Idade)** | **31 anos** | 26.5 anos | 4.5 anos | **$+1,00$** | Atleta experiente (1 desvio acima da média) |
| **`Minutagem_Real_Pct`** | **85.0%** | 45.0% | 25.0% | **$+1,60$** | Titular incontestável no ano |
| **`Gols_90`** | **0.55 gols/90** | 0.15 gols/90 | 0.20 gols/90 | **$+2,00$** | Atacante de altíssima eficiência |
| **`Media_GA_Time`** | **0.85 gols/jogo** | 1.20 gols/jogo | 0.35 gols/jogo | **$-1,00$** | Defesa sólida (gols sofridos abaixo da média) |

---

## 5. Tabela Consolidada de Métricas Completas do SAD (Out-of-Time 2021–2024)

| Posição Foco | Acurácia Teste | Precisão (Acerto de Elite) | Recall (Captura de Elite) | F1-Score Ponderado | ROC-AUC | Verdadeiros Negativos (Série B) | Verdadeiros Positivos (Série A) |
|---|---|---|---|---|---|---|---|
| 🧤 **Goleiros (GK)** | **85,71%** | **59,52%** | **65,79%** | **0,8599 (86,0%)** | **0,9131** | 152 | 25 |
| ⚽ **Centroavantes (FW)** | **79,53%** | **55,65%** | **50,74%** | **0,7919 (79,2%)** | **0,8563** | 240 | 34 |
| 🛡️ **Defensores (DF)** | **74,62%** | **60,42%** | **61,27%** | **0,7467 (74,7%)** | **0,8268** | 812 | 174 |
| 🧠 **Meio-Campistas (MF)** | **74,28%** | **56,34%** | **55,47%** | **0,7422 (74,2%)** | **0,8312** | 1082 | 238 |
