# Prompt Master para Execução no Antigravity

> **Como usar:** Copie e cole este prompt no chat do Antigravity (ou execute diretamente no ambiente) para reestruturar os scripts de treinamento e a aplicação Streamlit conforme as exigências da banca examinadora.

---

```text
Você é um especialista em Machine Learning para Sports Analytics e Engenharia de Software Python.
Estamos refatorando o repositório do TCC "Análise de Aptidão no Futebol Brasileiro" (Mestrado/MBA Poli-USP) para atender aos apontamentos da banca de defesa (nota 5,8 em recuperação).

### CONTEXTO & CORREÇÕES SOLICITADAS PELA BANCA:
1. "Transformação /90 não é normalização estatística": Implementar obrigatoriamente `StandardScaler` (Z-score) dentro de um `Pipeline` do scikit-learn. O `fit` do scaler deve ocorrer EXCLUSIVAMENTE nos dados de treino (2010–2020), aplicando apenas `transform` nos dados de teste out-of-time (2021–2024).
2. "Ausência de análise por posição": Substituir o modelo universal único por 4 MODELOS ESPECIALIZADOS INDEPENDENTES:
   - Atacantes (FW)
   - Meio-Campistas (MF)
   - Defensores (DF)
   - Goleiros (GK)
3. "Baixa capacidade discriminativa (~52%)": Avaliar e exportar os 4 modelos posicionais (Regressão Logística com StandardScaler, Random Forest e GradientBoosting/LightGBM), registrando Acurácia, F1-Score, ROC-AUC e Matrizes de Confusão por posição.
4. "Web-App Streamlit genérico": Atualizar a interface do Streamlit (`app/app.py`) para permitir a seleção inicial da Posição do jogador, ajustando dinamicamente os sliders de entrada e acionando o modelo preditivo específico daquela posição.

---

### ETAPAS DE EXECUÇÃO SOLICITADAS:

#### 1. Criar o pipeline de modelagem posicional (`src/modelagem/executar_pipeline_posicional.py`):
- Carregar os dados consolidados em `data/processed_tcc/jogadores_consolidado.csv` e `campeonato_consolidado.csv`.
- Mapear a posição para os 4 grupos (`FW`, `MF`, `DF`, `GK`).
- Filtrar jogadores com `Min >= 300`.
- Para cada grupo de posição:
  - Isolar a base correspondente.
  - Dividir em Treino (`Ano <= 2020`) e Teste (`Ano >= 2021`).
  - Treinar pipelines contendo `StandardScaler` + `LogisticRegression`, `RandomForestClassifier` e `GradientBoostingClassifier`.
  - Selecionar o melhor modelo por F1-Score / ROC-AUC para a posição.
  - Salvar o modelo em `app/assets/modelo_{posicao}.pkl` (ex.: `modelo_fw.pkl`, `modelo_mf.pkl`, `modelo_df.pkl`, `modelo_gk.pkl`).
- Salvar um dicionário consolidado em `app/assets/metricas_posicionais.pkl` contendo as métricas de treino/teste por posição.

#### 2. Atualizar a aplicação Streamlit (`app/app.py`):
- Criar seletor de posição (`Atacante`, `Meio Campo`, `Defensor`, `Goleiro`).
- Carregar dinamicamente o modelo correspondente da pasta `app/assets/`.
- Renderizar sliders e campos de entrada específicos para a posição escolhida.
- Exibir a predição da divisão (Série A ou Série B) e a probabilidade associada.
- Adicionar uma seção visual "Validação Metodológica do Modelo (Banca)", apresentando as métricas individuais daquele modelo posicional (Acurácia, F1-Score, Matriz de Confusão) e a explicação sobre a utilização do `StandardScaler` e split Out-of-Time.

Execute a refatoração, salve os arquivos nos caminhos indicados e valide a execução do script de treinamento.
```
