# 📋 Contexto do Projeto e Instruções para a Próxima Conversa

---

## 📌 1. Resumo do Estado Atual do Sistema (SAD Scouting Futebol - TCC USP)

O sistema de **Apoio à Decisão de Scouting de Futebol (SAD)** foi totalmente revisado, aprimorado e validado. Ele funciona como uma aplicação web interativa em Streamlit (`app/app.py`), utilizando uma base de dados consolidada com **8.752 registros históricos (2010–2024)** de atletas que disputaram o Campeonato Brasileiro (Séries A e B), além de modelos de Machine Learning especializados (**Gradient Boosting** e **Random Forest**) pré-treinados por posição.

### 🌟 Principais Funcionalidades Implementadas na Aplicação Web (`http://localhost:8501`)

1. **Aba 1: ⚽ Scouting de Atletas (Fluxo de Decisão em 3 Passos)**
   - **Passo 1 (Meu Time):** Seleção do clube contratante (ex: *Athletico Paranaense*).
   - **Passo 2 (Time Alvo & Atleta):** Filtro por Divisão (Série A/B), Clube Origem e Posição.
   - **Passo 3 (Veredito & Histórico):**
     - Exibição da recomendação para o clube contratante (ex: `🟢 Apto para Titularidade`, `🟡 Reserva Qualificado`, `🔴 Não Recomendado`).
     - Tabela de estatísticas da **Temporada Atual Selecionada**.
     - **Histórico Longitudinal das últimas 3 temporadas** registradas do jogador.
     - **Projeção de Enquadramento em Clubes da Série A** (G-6, Zona Intermediária, Luta Z-4).

2. **Aba 2: 🧪 Experimentos Comparativos (Justificativa Científica)**
   - **Demarcação da Falha Sem Normalização:** Explicação teórica e empírica do **colapso de gradiente** sofrido pela Regressão Logística sem escalonamento (Precisão 0.00%).
   - **Solução via StandardScaler:** Demonstração dos ganhos de acurácia, F1-Score e ROC-AUC.
   - **Matrizes de Confusão Reais:** Exibição dos cards de desempenho para Regressão Logística (Raw vs Scaled), Random Forest e **SAD Gradient Boosting por Posição (Atacante e Goleiro)**.

3. **Aba 3: ⚙️ Simulador Técnico ("What-If") & Scouting Match**
   - **Banner Explicativo:** Esclarecimento do propósito acadêmico/tático da Análise de Sensibilidade.
   - **Barra de Multi-Filtros:**
     - **Posição:** *Atacante*, *Goleiro*, *Defensor*, *Meio Campo*.
     - **Ano / Temporada:** Seleção por ano específico (ex: `2023`, `2022`) ou `Todas as Temporadas (2010–2024)`.
     - **Série / Divisão:** `Série A`, `Série B` ou `Todas as Divisões`.
   - **Botão `🔄 Restaurar Padrões`:** Reseta filtros e sliders para os valores padrão com 1 clique.
   - **Tabela de Scouting Match (Top 10 Atletas Reais):** Varre a base e traz os 10 jogadores reais com perfil estatístico mais próximo dos sliders ajustados, exibindo a coluna de **`Ano (Temporada)`** e a **`Similaridade (%)`**.
   - **Fórmula Matemática e Pesos das Variáveis ($w_i$):**
     - **Distância Euclidiana Ponderada:** $D_j = \sum w_i \times \frac{|X_{i, \text{atleta}} - X_{i, \text{simulado}}|}{\sigma_i}$
     - **Pesos por Posição:**
       - *Atacante / Meio Campo:* $w_{\text{Gols}} = 3,0$, $w_{\text{Ast}} = 1,5$, $w_{\text{Starts}} = 1,0$, $w_{\text{Minutagem}} = 1,0$, $w_{\text{Idade}} = 0,5$.
       - *Goleiro:* $w_{\text{GolsSofridos}} = 3,0$, $w_{\text{Starts}} = 1,0$, $w_{\text{Minutagem}} = 1,0$, $w_{\text{Idade}} = 0,5$.
       - *Defensor:* $w_{\text{CartoesAmarelos}} = 2,0$, $w_{\text{GolsSofridos}} = 2,0$, $w_{\text{Starts}} = 1,0$, $w_{\text{Minutagem}} = 1,0$, $w_{\text{Idade}} = 0,5$.
     - **Fórmula de Similaridade (%):** $\text{Similaridade}_j (\%) = \max\left(50\%, 100\% - D_j \times 15\%\right)$.

4. **Aba 4: 📖 Glossário, Passo a Passo e Justificativa Tática**
   - **Delimitação de Alta Confiança:** Destaque para a alta precisão em **Goleiros** e **Atacantes de Área**, e nota metodológica para Defensores e Meio-Campistas.
   - **Dicionário Completo de 25+ Atributos:** Descrição de cada variável da base FBref.
   - **Taxonomia Tripartida:** Explicação dos níveis (`🟢 Titular de Elite`, `🟡 Reserva Qualificado`, `🔴 Inapto`).

5. **Aba 5: 🏆 Carreiras Emblemáticas (15 Anos)**
   - Validação qualitativa com histórico longo de atletas consagrados (*Gabriel Barbosa, Germán Cano, Cássio, Marcelo Lomba, Gil, Léo Pereira, Giuliano, Lucas Lima*).

---

## 🚀 2. Como Executar a Aplicação Localmente

Para subir a aplicação Streamlit em qualquer momento:

```bash
# No diretório do projeto d:\tcc-usp\analise-aptidao-futebol-tcc
.venv\bin\python.exe -m streamlit run app/app.py --server.headless true --server.port 8501
```

Acesse no navegador: `http://localhost:8501`

---

## 🎯 3. Instruções para a Próxima Conversa (Apresentação para a Professora / Orientadora)

Quando você abrir uma **nova conversa**, basta colar o seguinte comando/orientação inicial para o assistente:

> *"Estou continuando o desenvolvimento do TCC do SAD de Scouting de Futebol. Por favor, leia o arquivo `INSTRUCOES_PROXIMA_CONVERSA.md` no diretório raiz do projeto para carregar o contexto completo. Nosso objetivo agora é gerar os documentos/relatórios finais (DOCX/PDF) para apresentar para a professora."*

### 📝 Roteiro Sugerido para a Próxima Sessão:

1. **Gerar/Atualizar o Relatório Escrito em DOCX/PDF:**
   - Atualizar os scripts de geração de relatório (`src/modelagem/update_tcc_docx_v2.py` ou `generate_turnitin_v2_fpdf.py`) incorporando os novos resultados da taxonomia tripartida, os gráficos comparativos e os testes de similaridade (Top 10).
2. **Preparar a Estrutura da Apresentação:**
   - Criar um roteiro de tópicos da apresentação oral (Introdução, Problema do Scouting, Base FBref, Experimentos com Normalização, Demarcação Posicional e Demonstração Prática do App).
3. **Checklist da Demonstração ao Vivo do App:**
   - Mostrar a navegação na **Aba 1** simulando a busca por um atacante de Série A para o time do aluno.
   - Mostrar a **Aba 2** destacando o gráfico comparativo de modelos e as matrizes de confusão.
   - Mostrar a **Aba 3** alterando o slider de gols para 0.45, selecionando `Ano: 2023` e `Série: Série A`, demonstrando a lista dos 10 atacantes mais próximos (*Tiquinho Soares, Vitor Roque, Paulinho, Pedro, etc.*).

---
*Arquivo gerado em 29/09/2026 para preservação integral de contexto do TCC - USP.*
