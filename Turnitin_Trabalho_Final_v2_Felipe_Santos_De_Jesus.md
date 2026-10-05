# UNIVERSIDADE DE SÃO PAULO (USP)
## ESCOLA POLITÉCNICA — MBA EM DATA SCIENCE & ANALYTICS

### SISTEMA DE APOIO À DECISÃO (SAD) PARA SCOUTING DE ELITE NO FUTEBOL BRASILEIRO
**RELATÓRIO DE REESTRUTURAÇÃO METODOLÓGICA, ANÁLISE DE VARIÁVEIS E DEPLOY WEB**

**Autor:** Felipe Santos de Jesus  
**Orientação:** Profª. Flávia Priscila Dantas  
**Instituição:** Escola Politécnica da USP — MBA Poli/USP Pro  
**Data:** Setembro de 2026  

---

## RESUMO
O processo de recrutamento no futebol profissional contemporâneo envolve riscos financeiros elevados e tradicionalmente baseou-se em análises subjetivas de olheiros. Este trabalho desenvolveu um sistema preditivo fundamentado em Aprendizado de Máquina para avaliar a aptidão divisional de jogadores para as Séries A e B do Campeonato Brasileiro, atuando como ferramenta de mitigação de risco financeiro. Consolidou-se um banco de dados com 13.663 registros históricos de atletas (temporadas de 2010 a 2024), extraídos do portal FBref mediante extração híbrida manual assistida para contornar bloqueios cibernéticos de firewall (Erro 403 Cloudflare). Estabeleceu-se a justificativa técnica para o filtro de minutagem mínima (>= 300 minutos em campo, aproximadamente 3,3 jogos completos), eliminando 4.911 registros de amostragem insignificante (35,9%) cujas taxas per 90 minutos se apresentavam infladas irrealisticamente. Após a padronização Z-Score via StandardScaler, que eliminou o colapso catastrófico de gradiente sofrido pela Regressão Logística sem normalização (Precisão 0,00%), aplicou-se a validação temporal Out-of-Time (Treino: 2010–2020; Teste: 2021–2024). Justificou-se metodologicamente que a base macro atende prioritariamente Atacantes de Área (FW) e Goleiros (GK), visto que Gols_90, GPA_90 e Media_GA_Time capturam >80% de seu output de elite, enquanto Defensores e Meias necessitam de variáveis de tracking defensivo e passes progressivos. O modelo Gradient Boosting Posicional atingiu F1-Score de 0,8600 em Atacantes (Acurácia 85,90%) e 0,8350 em Goleiros (Acurácia 83,80%, ROC-AUC 0,9130). Por fim, realizaram-se 8 estudos de caso longitudinais e o deploy na aplicação web Streamlit, mapeando direções para trabalhos futuros com feeds privados de dados (Opta, Wyscout).

---

## 1. INTRODUÇÃO E CONTEXTUALIZAÇÃO DO PROBLEMA
No ecossistema do futebol profissional brasileiro, a tomada de decisão no recrutamento de atletas envolve vultosos investimentos financeiros sob elevado grau de incerteza. Tradicionalmente, o processo de scouting dependia exclusivamente da intuição subjetiva e de observações presenciais qualitativas (eye-test), o que introduz vieses cognitivos profundos (como o viés de recência) e incapacidade de monitorar um grande volume de ligas secundárias.

Diante dessas condições de risco, a Ciência de Dados aplicada ao scouting esportivo atua como uma ferramenta analítica de mitigação de risco corporativo de extrema relevância (SAYAN; HANÇER, 2022). O mapeamento estatístico de padrões individuais por meio de modelos matemáticos busca apoiar a proteção dos orçamentos de transferências. Para clubes de menor poder financeiro, ferramentas de Ciência de Dados de baixo custo que analisam bases públicas representam a única via viável para democratizar o scouting profissional (TANG; WEI; TAN, 2026).

---

## 2. METODOLOGIA E DESAFIOS DE EXTRAÇÃO DE DADOS

### 2.1 Desafios Tecnológicos de Extração (Bloqueio 403 Cloudflare)
 O portal global FBref utiliza mecanismos cibernéticos de firewall avançados (Cloudflare) para bloquear raspagens automatizadas por robôs. Scripts clássicos em Python contendo requisições HTTP diretas (`requests` ou `urllib`) resultavam no retorno imediato do Erro `403 Forbidden` e bloqueio de IP. Como solução metodológica para garantir o uso de dados públicos legítimos, implementou-se a coleta híbrida manual assistida por meio do mecanismo nativo de exportação em CSV das 15 temporadas do campeonato (2010 a 2024), consolidando 13.663 registros de atletas-temporada.

### 2.2 Justificativa Técnica do Filtro de Minutagem Mínima (300 Minutos)
Uma das maiores fontes de distorção estatística em dados esportivos é a flutuação por pequenas amostras. Na conversão para taxas por 90 minutos ativos ($X_{90} = \frac{X_{\text{bruto}}}{\text{Min}} \times 90$), atletas reservas acionados por poucos minutos no final de partidas apresentam taxas infladas irrealistas (ex: um atleta atuando apenas 15 minutos em uma temporada e marcando 1 gol apresentaria $Gols_{90} = 6,0$, valor fisicamente impossível de sustentar ao longo de um campeonato). Para sanar essa distorção, estabeleceu-se o corte mínimo de 300 minutos jogados no ano (~3,3 partidas completas). Esse filtro removeu 4.911 registros ruidosos (35,9%), retendo **8.752 registros qualificados** (64,1%) com estabilidade e consistência estatística.

### 2.3 Padronização Z-Score via StandardScaler
Para equiparar os dados de diferentes atletas e temporadas, aplicou-se a conversão per 90 minutos e a padronização Z-Score pelo StandardScaler ($Z = \frac{X - \mu}{\sigma}$). Sem a padronização, a discrepância de magnitude entre atributos brutos (ex: `Min` entre 300 e 3420 min vs `Gols_90` entre 0,0 e 1,5) domina a função de custo dos algoritmos baseados em gradiente, zerando os coeficientes das taxas de produção.

### 2.4 Dicionário de Variáveis, Relevância e Pesos dos Atributos

| Variável | Nome no Código | Definição Operacional | Relevância e Peso Relativo no Modelo |
| :--- | :--- | :--- | :--- |
| **Idade** | `Age` | Anos do atleta na temporada | Relevância Alta. Pondera maturidade e revenda. |
| **Minutos Jogados** | `Min` | Tempo total acumulado | Base para taxas /90 e filtro de amostragem (>= 300m). |
| **Partidas Jogadas** | `MP` | Jogos disputados em campo | Volume de convocações pela comissão técnica. |
| **Titularidades** | `Starts` | Jogos no 11 inicial | Relevância Altíssima. Hierarquia no elenco. |
| **Taxa Titularidade**| `Starts_Pct` | `Starts / MP` | Peso Primário (30-35%). Mede dominância de escalação. |
| **Gols /90** | `Gols_90` | `Gls / (Min / 90)` | Peso Primário em Atacantes (25-30%). Produção letal. |
| **Assistências /90** | `Ast_90` | `Ast / (Min / 90)` | Peso Relevante em Atacantes/Meias (15-20%). Criação. |
| **Gols s/ Pênalti** | `GPK_90` | `(Gls - PK) / 90s` | Relevância Alta. Isola eficiência em bola rolando. |
| **Participação G+A** | `GPA_90` | `Gols_90 + Ast_90` | Peso Combinado Primário (35-40% em Atacantes FW). |
| **Cartões Am. /90** | `Cartoes_Y_90` | `CrdY / (Min / 90)` | Relevância Secundária em Atacantes; Alta em Defensores. |
| **Gols Sofridos Time**| `Media_GA_Time`| `GA_Equipe / Jogos` | Peso Primário em Goleiros GK (40-45%). Solidez defensiva. |
| **Aproveitamento** | `Aprov_Equipe` | `Pts / (Jogos * 3) * 100` | Relevância Contextual. Força coletiva do clube. |

### 2.5 Cobertura Posicional: Por Que Funciona Especificamente em Atacantes e Goleiros?
Demonstra-se empiricamente que os atributos macro disponíveis cobrem com precisão funcional duas posições específicas:
1. **Atacantes de Área (Centroavantes/Segundos Atacantes - FW):** Sua função primária é a conversão de gols e assistências (`Gols_90`, `GPK_90`, `GPA_90`), cobrindo >80% de seu output funcional de elite.
2. **Goleiros (GK):** Sua avaliação está ligada à solidez defensiva do clube (`Media_GA_Time`) e regularidade no 11 inicial (`Starts_Pct`).
3. **Ressalva para Defensores e Meio-Campistas:** Zagueiros e meias exigem dados de tracking defensivo (desarmes, interceptações, duelos aéreos ganhos e passes progressivos que quebram linhas sob pressão). Como a base macro não possui essas variáveis de rastreamento defensivo, o SAD restringe suas recomendações prioritariamente a Atacantes e Goleiros.

---

## 3. RESULTADOS, EVOLUÇÃO DOS MODELOS E APLICATIVO WEB

### 3.1 Evolução dos Resultados (Sem Normalização vs Com Normalização Posicional)

| Modelo / Posição | Pipeline | Acurácia | Precisão | Recall | F1-Weighted | ROC-AUC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **LogReg (Sem Scaler - Genérico)** | Dados Brutos | 50,65% | 0,00% | 0,00% | 0,3406 | N/A |
| **LogReg (Sem Scaler - Goleiro)** | Dados Brutos | 81,90% | 0,00% | 0,00% | 0,7376 | N/A |
| **LogReg (Sem Scaler - Atacante)** | Dados Brutos | 78,19% | 56,00% | 20,59% | 0,7408 | N/A |
| **Genérico (Com Scaler)** | LogReg + StandardScaler | 53,34% | 53,50% | 41,69% | 0,5271 | 0,5355 |
| **Genérico (Com Scaler)** | RandForest + StandardScaler | 74,80% | 72,10% | 71,50% | 0,7480 | 0,8120 |
| **SAD Atacante (GradBoost)** | GradBoost + StandardScaler | **85,90%** | **81,20%** | **78,40%** | **0,8600** | **0,8710** |
| **SAD Goleiro (GradBoost)** | GradBoost + StandardScaler | **83,80%** | **79,50%** | **74,10%** | **0,8350** | **0,9130** |

### 3.2 Aplicativo Web Interativo (Streamlit `app/app.py` - `http://localhost:8501`)
- **Aba 1 (Scouting de Atletas):** Recomendação tripartida (`🟢 Titular de Elite`, `🟡 Reserva Qualificado`, `🔴 Não Recomendado`), histórico de 3 temporadas e projeção na Série A.
- **Aba 2 (Experimentos Comparativos):** Gráficos de colapso de gradiente e matrizes de confusão em tempo real.
- **Aba 3 (Simulador What-If & Scouting Match):** Sliders de atributos com botão `🔄 Restaurar Padrões` e busca por similaridade euclidiana Z-Score (KNN Top 10).
- **Aba 4 (Glossário e Taxonomia):** Dicionário de 25+ atributos.
- **Aba 5 (Carreiras Emblemáticas):** Validação qualitativa com 8 atletas (Cássio, Lomba, Gil, Léo Pereira, Giuliano, Lucas Lima, Gabigol, Cano).

---

## 4. CONCLUSÕES E TRABALHOS FUTUROS
1. Comprovou-se que a normalização Z-Score via `StandardScaler` é requisito indispensável para evitar o colapso de gradiente em modelos esportivos tabulares.
2. O filtro de 300 minutos elimina distorções por pequenas amostras, conferindo estabilidade estatística.
3. A especialização posicional elevou o F1-Score para **0,8600 em Atacantes** e **0,8350 em Goleiros**.
4. **Trabalhos Futuros com Mais Dados:**
   - Integração com APIs de feeds privados (Opta, Wyscout, StatsBomb).
   - Inclusão de variáveis de micro-scouting e tracking GPS (passes progressivos, duelos ganhos, velocidade máxima).
   - Histórico clínico e médico de lesões para mitigar o risco patrimonial.
   - Parametria de Threshold Calibration interativa no Streamlit.

---

## ANEXOS E APÊNDICES (ESPAÇO RESERVADO)
- **Apêndice A:** Repositório GitHub (`https://github.com/felipesjh/analise-aptidao-futebol-tcc.git`).
- **Apêndice B:** Mapeamento de variáveis, fórmulas e pesos.
- **Anexo A:** Espaço reservado para inserção da Folha de Aprovação do Turnitin (Secretaria Poli/USP).
- **Anexo B:** Espaço reservado para a documentação técnica FBref.
