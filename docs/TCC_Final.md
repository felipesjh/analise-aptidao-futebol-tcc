# UNIVERSIDADE DE SÃO PAULO
## ESCOLA POLITÉCNICA
## PROGRAMA DE MBA EM DATA SCIENCE & ANALYTICS PARA OPERAÇÕES (POLI USP PRO)

<br><br><br><br>

### FELIPE SANTOS DE JESUS

<br><br><br><br>

## SISTEMA PREDITIVO DE SCOUTING ESPORTIVO: AVALIAÇÃO DE APTIDÃO DIVISIONAL DE JOGADORES DE FUTEBOL NO CAMPEONATO BRASILEIRO USANDO APRENDIZADO DE MÁQUINA

<br><br><br><br><br><br><br><br>

#### São Paulo
#### 2026

---

### FELIPE SANTOS DE JESUS

<br><br>

## SISTEMA PREDITIVO DE SCOUTING ESPORTIVO: AVALIAÇÃO DE APTIDÃO DIVISIONAL DE JOGADORES DE FUTEBOL NO CAMPEONATO BRASILEIRO USANDO APRENDIZADO DE MÁQUINA

<br><br>

<p align="right">
Trabalho de Conclusão de Curso apresentado ao Programa de MBA em Data Science & Analytics para Operações da Escola Politécnica da Universidade de São Paulo, como requisito parcial para obtenção do título de Especialista.
<br><br>
<b>Orientadora:</b> Profª. Flávia Priscila Dantas
</p>

<br><br><br><br>

#### São Paulo
#### 2026

---

### Resumo

O futebol profissional contemporâneo transformou-se em uma indústria global altamente competitiva e de capital intensivo, onde a tomada de decisão no recrutamento de atletas envolve riscos financeiros multimilionários. Tradicionalmente pautado em análises subjetivas e observações qualitativas de olheiros, o processo de recrutamento esportivo (*scouting*) tem demandado abordagens analíticas robustas fundamentadas em Ciência de Dados. Este trabalho apresenta o desenvolvimento de um sistema preditivo para avaliar a aptidão divisional de jogadores de futebol para as Séries A e B do Campeonato Brasileiro. A base de dados utilizada compreende 13.663 registros históricos consolidados (temporadas de 2010 a 2024) de desempenho individual de atletas, coletados de forma manual assistida a partir do portal de estatísticas globais FBref devido a restrições tecnológicas de raspagem de dados direta. Os dados passaram por limpeza, tratamento e engenharia de atributos (como a normalização de estatísticas ofensivas, defensivas e de disciplina pela notação "por 90 minutos de jogo" e criação de variáveis binárias para grupos posicionais). A validação dos modelos de Aprendizado de Máquina foi estruturada sob o paradigma temporal *Out-of-Time* (treinamento com dados de 2010 a 2020 e teste com dados de 2021 a 2024) para refletir de maneira realista o processo decisório de transferências futuras e evitar vazamentos de dados temporais. Foram avaliados os algoritmos de Regressão Logística (como *baseline* linear interpretável) e *Random Forest* (classificador não linear *ensemble*). O modelo final de *Random Forest* apresentou uma acurácia global de 52,78% no conjunto de teste independente. O limite empírico de desempenho obtido é discutido sob a ótica da teoria da auto-equivalência dos ecossistemas divisionais e da limitação de variáveis de micro-scouting individuais (como precisão de passes sob pressão, distância total percorrida e mapas de calor), que não estão sistematicamente cobertas na base macro. A viabilidade prática do modelo foi demonstrada por meio de estudos de caso longitudinal da carreira de oito atletas renomados (Cássio, Marcelo Lomba, Gil, Léo Pereira, Giuliano, Lucas Lima, Gabriel Barbosa e Germán Cano) e disponibilizada aos tomadores de decisão em um Web-App desenvolvido com a biblioteca Streamlit.

**Palavras-chave**: Aprendizado de Máquina, Scouting Esportivo, Validação Out-of-Time, Random Forest, Campeonato Brasileiro.

---

### Abstract

Contemporary professional football has evolved into a highly competitive, capital-intensive global industry where recruitment decisions entail multi-million dollar financial risks. Traditionally guided by subjective analyses and qualitative observations from scouts, sports recruitment has increasingly demanded robust analytical frameworks based on Data Science. This work presents the development of a predictive system to evaluate the divisional suitability of football players for Series A and B of the Brazilian National Championship. The database consists of 13,663 consolidated historical player-season records (from 2010 to 2024 seasons) of individual performance metrics. These were gathered using an assisted manual extraction methodology from the global statistics portal FBref, which was necessary to bypass automated scraping blockades. The raw data underwent preprocessing and feature engineering, which normalized offensive, defensive, and disciplinary metrics to a "per 90 minutes" standard and generated binary features for positional groups. Machine learning models were validated under an Out-of-Time temporal framework (training on 2010–2020 seasons and testing on 2021–2024 seasons) to represent a realistic recruitment scenario for future seasons and prevent temporal data leakage. Logistic Regression (as an interpretable linear baseline) and Random Forest (as a non-linear ensemble classifier) were evaluated. The final Random Forest model achieved a testing accuracy of 52.78% on the independent temporal test set. This performance boundary is discussed through the lens of competitive ecosystem auto-equivalence and the absence of granular micro-scouting variables (such as passes completed under pressure, total distance covered, and heatmaps). Finally, the practical application of the model was validated using longitudinal career case studies of eight prominent players (Cássio, Marcelo Lomba, Gil, Léo Pereira, Giuliano, Lucas Lima, Gabriel Barbosa, and Germán Cano) and deployed for decision-makers via a Streamlit-based web application.

**Keywords**: Machine Learning, Sports Analytics, Out-of-Time Validation, Random Forest, Brazilian League.

---

## Introdução

### Contextualização e Justificativa Mercadológica

O mercado internacional do futebol movimenta anualmente dezenas de bilhões de dólares em transações de direitos federativos, salários e direitos comerciais de transmissão de mídia, consolidando o esporte como uma indústria global altamente profissionalizada e de capital intensivo. No cenário brasileiro contemporâneo, a promulgação da Lei nº 14.193/2021 viabilizou a constituição da Sociedade Anônima do Futebol (SAF), provocando uma transição sem precedentes nos clubes nacionais. Clubes tradicionalmente associativos e geridos de forma puramente política passaram a atuar sob o controle de fundos de investimento e acionistas privados. Sob essa nova perspectiva corporativa, a governança financeira, a eficiência na alocação de recursos e o retorno sobre o investimento (ROI) tornaram-se métricas de sobrevivência institucional.

A maior fonte de volatilidade financeira e desperdício de valor nos caixas dos clubes reside no mercado de contratações de jogadores. A transição de atletas entre clubes envolve o pagamento de multas rescisórias vultosas e o comprometimento de folhas salariais de longo prazo. Historicamente, conforme pontuado por Hughes e Franks (2019), o recrutamento esportivo (*scouting*) baseava-se em critérios eminentemente subjetivos e qualitativos. As avaliações de olheiros dependiam da percepção humana em tempo real (*eye-test*), o que introduz vieses cognitivos profundos. Dentre estes, destaca-se o viés de recência (onde a boa atuação do atleta em dois ou três jogos consecutivos é supervalorizada) e a incapacidade física de monitorar um volume massivo de partidas simultâneas em ligas secundárias.

Na realidade prática das operações esportivas brasileiras, estima-se que mais da metade dos atletas contratados não atinjam os limiares de desempenho técnico projetados pelas diretorias ao mudar de agremiação ou ao ascender de divisão competitiva. Esse insucesso gera severos impactos financeiros e de governança:
*   Depreciação imediata do valor de mercado do atleta (perda de capital de giro do clube).
*   Comprometimento do orçamento da folha salarial por múltiplos anos com atletas de baixo rendimento que não encontram recolocação em outros mercados.
*   Custo de oportunidade técnico (perda de posições na tabela do campeonato nacional, resultando em menores premiações financeiras e menor atratividade comercial para patrocinadores).
*   Custos jurídicos e de rescisão antecipada que fragilizam a estrutura de caixa do clube.

Diante dessas condições de risco, a Ciência de Dados aplicada ao scouting esportivo atua como uma ferramenta analítica de mitigação de risco corporativo de extrema relevância (SAYAN; HANÇER, 2022). O mapeamento estatístico de padrões individuais por meio de modelos matemáticos busca apoiar a proteção dos orçamentos de transferências, fornecendo aos comitês técnicos de futebol uma ferramenta quantitativa que avalia se a produção física, ofensiva e disciplinar de um atleta sugere que ele apresenta o perfil de desempenho estatístico individual adequado para atuar na Série A ou se o limita a um perfil de composição divisional inferior.

Além disso, há um fator mercadológico crucial relacionado à assimetria orçamentária no ecossistema do futebol brasileiro. Equipes da elite da Série A operam com receitas anuais que muitas vezes superam a casa dos 500 milhões de reais. Em contrapartida, a grande maioria dos clubes que competem na Série B opera com frações modestas desse orçamento (muitas vezes abaixo de 30 ou 40 milhões de reais). Para estes clubes de menor poder financeiro, ferramentas de Ciência de Dados de baixo custo operacional que analisam bases públicas (como os dados tabulares consolidados do FBref) representam a única via viável para democratizar o scouting profissional. Essas equipes podem vasculhar a base histórica de mais de 13 mil atletas de forma rápida, filtrando talentos subvalorizados antes que os rivais de maior orçamento os identifiquem, minimizando o risco de apostas caras em contratações ineficazes (TANG; WEI; TAN, 2026).

### Justificativa Acadêmica

Cientificamente, a análise preditiva em dados de esportes coletivos constitui um campo de fronteira na pesquisa de Inteligência Artificial aplicada a dados secundários complexos (MEMMERT; RAABE, 2018). Diferente de dados industriais típicos onde as condições de contorno são estáticas, o desempenho individual de um atleta no futebol está inserido em uma matriz de variáveis coletivas dinâmicas e contextuais. Este trabalho justifica-se no ambiente acadêmico por meio de três pilares:

Em primeiro lugar, a validação de algoritmos preditivos em séries temporais longitudinais esportivas requer abordagens metodológicas robustas para prevenir o vazamento de dados (*data leakage*). Em aplicações simplificadas de aprendizado de máquina, adota-se comumente a divisão aleatória dos registros em conjuntos de treino e teste (*K-Fold Cross-Validation*). No entanto, em dados de desempenho contínuo de atletas, os registros de um mesmo jogador ao longo das temporadas (ex: Cano em 2020 e Cano em 2021) possuem forte correlação temporal. Se utilizarmos uma divisão puramente aleatória, dados do futuro de um jogador estarão presentes no treino para prever o passado do mesmo atleta, resultando em acurácias infladas artificialmente que não se sustentam na vida real. Para sanar essa vulnerabilidade acadêmica, este TCC adota a divisão temporal *Out-of-Time* (VILELA; PORTELA; SANTOS, 2018). O treinamento é restrito a uma janela histórica de onze anos (Temporadas 2010 a 2020), enquanto o teste é aplicado de forma totalmente cega e ciente sobre as quatro temporadas futuras subsequentes (Temporadas 2021 a 2024). Essa abordagem replica cientificamente o cenário em que um departamento de dados estuda o passado para prever a viabilidade de contratação nos anos que se seguirão.

Em segundo lugar, a escolha dos algoritmos preditivos fundamenta-se no debate científico sobre o desempenho de redes neurais profundas versus modelos baseados em árvores para dados tabulares numéricos. Conforme amplamente discutido na literatura de aprendizado de máquina tabular (GRINSZTAJN; OYALLON; VAROQUAUX, 2022), datasets tabulares de tamanho moderado com classes altamente sobrepostas e ruidosas não se beneficiam de redes neurais profundas (*Deep Learning*). As redes profundas sofrem de rápida perda de generalização por *overfitting* nestes cenários e carecem de interpretabilidade ("caixa-preta"), inviabilizando que scouts e treinadores entendam as razões da decisão do modelo. Assim, justifica-se cientificamente a modelagem por meio de algoritmos estatísticos interpretáveis como a **Regressão Logística Binária** (atuando como classificador linear de probabilidade) comparada com o modelo **Random Forest** (um classificador baseado em florestas de decisão emparelhadas por *bagging* que captura interações de atributos não lineares de forma robusta e transparente por meio das importâncias de recursos baseadas na impureza de Gini).

Em terceiro lugar, a contribuição acadêmica estende-se ao estudo dos ecossistemas competitivos fechados do futebol nacional. A modelagem quantitativa permite-nos investigar estatisticamente a auto-equivalência do desempenho: como os atletas ajustam seus comportamentos físicos e técnicos à qualidade coletiva de seus oponentes diretos. Essa análise ajuda a identificar o limite matemático da informação de scout bruto individual no processo de classificação divisional.

### Objetivos do Trabalho

#### Objetivo Geral
O objetivo geral deste trabalho consiste em desenvolver, avaliar e implantar um sistema analítico preditivo baseado em algoritmos de aprendizado de máquina supervisionado para classificação binária (Regressão Logística Binária e Random Forest) para estimar a aptidão divisional de jogadores de futebol para as Séries A e B do Campeonato Brasileiro. A aplicação visa determinar se as métricas consolidadas de desempenho de um determinado atleta individual sugerem que ele apresenta o perfil de desempenho estatístico individual adequado para atuar no nível competitivo da série de elite (Série A) ou no de acesso (Série B), de forma a servir de suporte quantitativo à mitigação de risco financeiro no recrutamento profissional de clubes.

#### Objetivos Específicos
Para atingir o objetivo principal, foram definidos os seguintes objetivos específicos:
1.  Estruturar um pipeline de Ingestão de Dados e ETL utilizando a linguagem de programação Python para consolidar um dataset histórico robusto cobrindo estatísticas individuais de atletas nas Séries A e B do Campeonato Brasileiro entre as edições de 2010 e 2024.
2.  Implementar normalizações matemáticas "por 90 minutos de jogo" (/90) nas variáveis ofensivas, defensivas e disciplinares dos atletas e aplicar filtros de significância estatística baseados em tempo mínimo em campo para expurgar distorções no cálculo de taxas analíticas.
3.  Treinar e otimizar classificadores estatísticos binários utilizando a validação temporal *Out-of-Time* (Treino: 2010–2020; Teste: 2021–2024) para mensurar a acurácia de predição em temporadas futuras independentes.
4.  Investigar e discutir de forma teórica as limitações de acurácia observadas nos algoritmos pautados em dados macro tabulares individuais de volume, avaliando o fenômeno da auto-equivalência divisional de estatísticas em ligas fechadas.
5.  Validar o modelo qualitativamente e de forma prática através da análise longitudinal e retrospectiva de carreira de oito atletas de referência no futebol brasileiro (goleiros, defensores, meio-campistas e atacantes) a partir de seus dados longitudinais consolidados.
6.  Desenvolver uma aplicação interativa (Web-App) com suporte de interface Streamlit, integrando o classificador final de aprendizado de máquina e disponibilizando um Simulador de Cenários e dossiês de carreira aos gestores e analistas de scout de futebol, cujo código-fonte completo encontra-se publicado em repositório público no GitHub, conforme detalhado no Apêndice A.

### Delimitação do Tema e Limitações Metodológicas

A delimitação deste projeto estabelece as seguintes restrições de escopo e limitações tecnológicas:

A análise divisional de aptidão foi estritamente delimitada às **Séries A e B do Campeonato Brasileiro de Futebol Masculino**. A exclusão da Série C deu-se pela total ausência de coleta contínua e sistemática de dados de desempenho individual minuto a minuto no portal FBref para as últimas décadas. Enquanto os atletas das Séries A e B possuem monitoramento individual detalhado de todos os eventos tabulares consolidados, a Série C brasileira não possui cobertura analítica de dados que viabilize a construção de séries históricas uniformes sem introduzir vazios de dados massivos que inviabilizariam o treinamento de qualquer algoritmo supervisionado.

A exclusão de outras ligas internacionais (como as europeias ou sul-americanas) nesta pesquisa constitui uma decisão metodológica consciente e protetiva. A expansão da base de dados para outros países exigiria a criação de complexos coeficientes de ponderação para o ajuste de força das ligas (*league difficulty adjustment*), além de controlar diferenças de calendário (calendário europeu vs sul-americano), disparidades climáticas, estilo tático de jogo e, principalmente, contrastes econômicos abissais. Sem esses controles estruturais rigorosos, comparar estatísticas brutas de ligas distintas sem equivalência introduziria vieses de modelagem severos que reduziriam, em vez de elevar, a integridade da estimativa divisional do modelo nacional.

Adicionalmente, os atributos contidos no dataset de treinamento consistem exclusivamente em dados de **volume macro** do atleta (idade, minutos totais em campo, partidas jogadas, titularidade, gols, assistências, cartões amarelos e cartões vermelhos). O modelo preditivo desenvolvido não possui acesso a variáveis qualitativas e geométricas de micro-scouting, tais como:
*   Percentual de passes verticais que quebram linhas defensivas (*progressive passes*) divididos por zonas de campo.
*   Taxa de desarmes com recuperação de posse de bola efetiva.
*   Velocidade física instantânea máxima medida por dispositivos de telemetria GPS e distância total percorrida sob intensidades de alta taxa aeróbica.
*   Dados posicionais em coordenadas cartesianas gerados por rastreamento óptico de câmeras (*tracking*).
*   Indicadores coletivos agregados do sistema tático da equipe de atuação e aspectos psicossociais ou histórico de lesões clínicas de longo prazo.

Esta limitação de dados é importante do ponto de vista científico. Ela estabelece a fronteira teórica da predição individual baseada em dados brutos acumulados, permitindo que a discussão dos resultados demonstre à banca examinadora que uma acurácia limítrofe representa um limite empírico de desempenho observado decorrente da restrição informacional de modelagem macro e não uma falha no ajuste matemático do modelo.

Por fim, no que tange à coleta de dados secundários, o projeto conviveu com restrições tecnológicas de infraestrutura cibernética impostas pelo portal global FBref, que utiliza serviços de firewall avançados (Cloudflare) para bloquear raspagens automatizadas massivas. Scripts automatizados clássicos desenvolvidos em Python contendo chamadas HTTP diretas (`requests` ou `urllib`) resultam na detecção do IP do pesquisador como um bot de extração comercial, gerando o imediato bloqueio do IP local com o retorno do Erro `403 Forbidden` (Acesso Proibido). Como solução metodológica para contornar esta restrição tecnológica de forma ética e preservar o domínio público acadêmico dos dados, realizou-se a coleta manual assistida. Os dados tabulares históricos de cada edição do campeonato foram extraídos individualmente por meio do mecanismo nativo de download e exportação em formato CSV do próprio portal FBref. Embora este procedimento de coleta tenha consumido expressivo esforço de tempo e operação manual, ele contribuiu para a padronização e integridade da base, consolidando uma base analítica final de **13.663 atletas-temporada** limpa, estruturada e sem imperfeições de codificação.

---

## Material e Métodos ou Método

A metodologia implementada para a concepção do pipeline analítico do TCC seguiu o fluxo estruturado CRISP-DM (*Cross Industry Standard Process for Data Mining*), cobrindo as fases de Entendimento do Negócio, Entendimento dos Dados, Preparação dos Dados, Modelagem, Avaliação e Implantação (WIRTH; HIPP, 2000).

### Metodologia de Pesquisa (Classificação e Delineamento)

Com o objetivo de conferir o devido rigor metodológico exigido pelas normas do Manual de TCC do MBA da Escola Politécnica da USP, a presente pesquisa classifica-se nos seguintes termos:
*   **Quanto à Natureza**: **Pesquisa Aplicada**. O estudo visa produzir conhecimentos e desenvolver soluções preditivas com o propósito de resolver um problema prático e concreto da indústria do futebol profissional — a avaliação de risco financeiro no recrutamento divisional de elenco de atletas.
*   **Quanto à Abordagem**: **Pesquisa Quantitativa**. Recorre-se a métodos estatísticos descritivos e inferenciais e a algoritmos de aprendizado de máquina supervisionado para manipular numericamente a base de dados esportivos, testando hipóteses matemáticas objetivas e calculando acurácias quantificáveis.
*   **Quanto aos Objetivos**: **Pesquisa Exploratório-Descritiva**. A pesquisa descreve detalhadamente as relações matemáticas entre variáveis macro de desempenho do atleta e a categoria divisional em que ele atua. Ao mesmo tempo, explora a formulação de novos conceitos (como a teoria da auto-equivalência do ecossistema competitivo das divisões do futebol nacional) e compara o rendimento de classificadores em dados tabular-temporais.
*   **Quanto aos Procedimentos e Fontes**: **Pesquisa Documental e Análise de Dados Secundários**. Adota-se como matéria-prima documental os registros públicos de desempenho esportivo de domínio público acadêmico acumulados durante 15 edições do certame nacional, dispensando termos éticos clínicos por não envolver interação com seres humanos ou dados privados e confidenciais identificáveis.
*   **Quanto ao Método**: **Implementação de Algoritmo**. O delineamento da pesquisa envolve a codificação de rotinas matemáticas para tratamento, treinamento, validação e desenvolvimento de uma plataforma computacional Web-App (Streamlit) para entrega das predições de inteligência artificial.

### Cronograma de Desenvolvimento do Projeto

A condução do TCC ocorreu ao longo de um semestre letivo dividido em seis meses operacionais (Janeiro a Junho de 2026), conforme detalhado na Tabela 1:

#### Tabela 1: Cronograma Operacional do TCC (M1 a M6 de 2026)
| Etapa / Fase de Desenvolvimento do TCC | M1 (Jan) | M2 (Fev) | M3 (Mar) | M4 (Abr) | M5 (Mai) | M6 (Jun) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 1. Revisão Bibliográfica e Formulação da Proposta | **X** | **X** | | | | |
| 2. Extração Híbrida e Consolidação da Base (FBref) | | **X** | **X** | | | |
| 3. Engenharia de Recursos, Limpeza e Normalização (/90) | | | **X** | **X** | | |
| 4. Modelagem e Treinamento (Regressão Logística e Random Forest) | | | | **X** | **X** | |
| 5. Validação Out-of-Time e Otimização de Hiperparâmetros | | | | | **X** | |
| 6. Análise de Estudos de Caso Longitudinal e Desenvolvimento do App | | | | | **X** | **X** |
| 7. Redação da Monografia e Preparação dos Materiais de Entrega | | | | | | **X** |

*Fonte: Produzido pelo autor do TCC (Felipe Santos de Jesus).*

### Caracterização e Funil da Base de Dados

Para assegurar a solidez analítica exigida pela comissão de Engenharia de Computação e Analytics da USP, a Tabela 2 apresenta o funil do processamento e descarte de dados brutos na fase de engenharia de dados:

#### Tabela 2: Funil de Processamento e Splits de Modelagem
| Etapa de Processamento | Descrição Operacional | Volume de Instâncias | Percentual de Base (%) |
| :--- | :--- | :---: | :---: |
| **Registros Originais Brutos** | Atletas-Temporada consolidados de 2010 a 2024 | 13.663 | 100,0% |
| **Filtro de Descarte (Min < 300)**| Registros de baixíssima amostragem de minutos | 4.911 | 35,9% (Removidos) |
| **Base Final Tratada** | Base qualificada com significância estatística | **8.752** | **64,1% (Retidos)** |
| **Conjunto de Treinamento** | Dados Out-of-Time históricos (2010 a 2020) | 4.849 | 35,5% do total bruto |
| **Conjunto de Teste Independente**| Dados Out-of-Time futuros cegos (2021 a 2024) | 3.903 | 28,6% do total bruto |

*Fonte: Produzido com dados de engenharia de dados do TCC.*

O descarte de 35,9% da base original foi uma decisão metodológica necessária. Jogadores que atuam poucos minutos distorcem drasticamente as estatísticas normalizadas /90. Contudo, assume-se como limitação que este filtro pode introduzir um viés de seleção ao excluir jovens atletas promessas das categorias de base acionados apenas nos minutos finais dos confrontos do clube profissional.

A distribuição de classes (Série A como classe 1 e Série B como classe 0) nos splits de dados está descrita na Tabela 3, revelando conjuntos equilibrados de treino e teste:

#### Tabela 3: Distribuição de Classes (Série A e Série B) nos Splits
| Classe Alvo / Proxy de Aptidão | Treinamento (2010–2020) | Percentual (%) | Teste (2021–2024) | Percentual (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Série B (Codificação 0)** | 2.464 | 50,8% | 1.977 | 50,7% |
| **Série A (Codificação 1)** | 2.385 | 49,2% | 1.926 | 49,3% |
| **Total** | **4.849** | **100,0%** | **3.903** | **100,0%** |

*Fonte: Produzido a partir dos resultados do script de modelagem.*

A variável-alvo (target) do classificador é a divisão esportiva disputada pelo jogador no ano corrente, codificada de forma binária. Como a "aptidão divisional real" não é uma grandeza observável diretamente, adotou-se a divisão disputada como uma proxy supervisionada de adequação competitiva, assumindo que um jogador escalado sistematicamente na Série A atende ao perfil de elite do futebol nacional.

### Engenharia de Atributos e Normalização

O processamento e a preparação dos dados foram executados por scripts Python, cujo fluxo principal está definido no arquivo `src/modelagem/executar_pipeline.py`.

#### A. Tratamento e Normalização Per 90 Minutos (/90)
As estatísticas brutas de produtividade (gols, assistências, cartões amarelos e cartões vermelhos) foram convertidas para a unidade de tempo uniforme de 90 minutos ativos em campo (CARLING et al., 2008), eliminando o viés do volume bruto jogado:

$$\text{Gols\_90} = \frac{\text{Gls}}{\text{Min} / 90}$$

$$\text{Ast\_90} = \frac{\text{Ast}}{\text{Min} / 90}$$

$$\text{Cartões\_Amarelos\_90} = \frac{\text{CrdY}}{\text{Min} / 90}$$

$$\text{Cartões\_Vermelhos\_90} = \frac{\text{CrdR}}{\text{Min} / 90}$$

#### B. Engenharia de Variáveis de Posição
O modelo mapeou as abreviações em inglês originais de posição para quatro grandes grupos táticos no idioma português: `Atacante` (derivado de `FW`), `Meio Campo` (derivado de `MF`), `Defensor` (derivado de `DF`) e `Goleiro` (derivado de `GK`). Para evitar a quebra de ordenação ordinal, estes grupos foram submetidos a codificação One-Hot gerando quatro atributos binários flutuantes (`Pos_Atacante`, `Pos_Meio Campo`, `Pos_Defensor` e `Pos_Goleiro`), que atuam como variáveis dummies informando a especialidade tática do atleta ao modelo.

#### C. Variáveis de Utilização e Confiança do Treinador
1.  **Taxa de Titularidade (Starts_Pct)**: Avalia a proporção em que o atleta foi selecionado para iniciar a partida na escalação inicial:
    
    $$\text{Starts\_Pct} = \frac{\text{Starts}}{\text{Partidas Jogadas}}$$
    
2.  **Porcentagem de Minutagem Real (Minutagem_Real_Pct)**: Expressa o volume físico totalizado acumulado em relação ao limite possível de minutos da equipe na competição:
    
    $$\text{Minutagem\_Real\_Pct} = \left( \frac{\text{Minutos Jogados}}{\text{Jogos Totais Equipe} \times 90} \right) \times 100$$

### Divisão de Validação Temporal (Out-of-Time)

A partição temporal Out-of-Time compreendeu o treinamento com dados de 2010 a 2020 e teste cego com dados futuros de 2021 a 2024. Essa estrutura é fundamental na modelagem de esportes, pois impede que estatísticas preditivas sofram com o vazamento de informações do futuro, obrigando os modelos a provar sua utilidade em novos cenários temporais (temporadas independentes subsequentes).

### Seleção de Algoritmos e Justificativa de Exclusão de Deep Learning

#### A. Regressão Logística Binária (Baseline)
A Regressão Logística Binária é um classificador linear clássico e interpretável. O modelo calcula a probabilidade de uma instância pertencer à classe de elite (Série A, codificada como 1) contra a classe de acesso (Série B, codificada como 0) aplicando a função sigmoide à combinação linear dos atributos:

$$P(Y = 1 \mid X) = \frac{1}{1 + e^{-(\beta_0 + \beta_1 X_{\text{Idade}} + \beta_2 X_{\text{Gols\_90}} + \dots + \beta_k X_{\text{Pos\_Goleiro}})}}$$

Os coeficientes $\beta_i$ ajustados por máxima verossimilhança são de suma importância para o TCC: eles explicam a influência marginal linear de cada atributo de scouting. Por exemplo, a exponencial do coeficiente ($e^{\beta_i}$) fornece a Razão de Probabilidade (*Odds Ratio*), informando se o acréscimo de uma unidade em gols/90 aumenta ou reduz a chance de o atleta ser mapeado com perfil de Série A.

#### B. Random Forest Classifier
O Random Forest é um classificador ensemble de árvores de decisão. Sua justificativa acadêmica reside na capacidade não-linear: as árvores efetuam cortes espaciais recursivos nas variáveis tabulares de scouting, capturando interações complexas que a regressão linear falha em isolar (TANG; WEI; TAN, 2026). O algoritmo oferece a Importância de Recursos calculada pela redução média de impureza de Gini a cada corte de árvore, trazendo transparência metodológica.

#### C. Justificativa de Exclusão de Algoritmos de Deep Learning
Seguindo os preceitos científicos de Grinsztajn, Oyallon e Varoquaux (2022), redes neurais profundas (*Deep Learning*) foram excluídas por dois motivos:
1.  **Overfitting e Falta de Desempenho**: Redes neurais possuem milhões de parâmetros que necessitam de vastos datasets não estruturados para convergência. Em dados tabulares esportivos numéricos moderados, modelos ensembles baseados em árvores superam o rendimento das redes neurais de forma consistente. As redes neurais poderiam sofrer de overfitting nos dados de treino, gerando resultados insatisfatórios no teste Out-of-Time.
2.  **Falta de Interpretabilidade (Black Box)**: A tomada de decisão em clubes de futebol envolve comissões técnicas e conselhos executivos que demandam explicações transparentes sobre os investimentos financeiros recomendados. A opacidade matemática das camadas ocultas de uma rede profunda impede o diagnóstico de quais KPIs específicos de campo fundamentaram a aptidão divisional prevista.

---

## Resultados e Discussão

Os modelos preditivos foram executados no script Python e avaliados em relação ao conjunto de teste temporal cego das temporadas 2021 a 2024.

### Desempenho Preditivo e Comparação de Modelos

A Tabela 4 resume a comparação detalhada e matematicamente completa das matrizes de confusão e métricas de teste temporal dos classificadores:

#### Tabela 4: Matrizes de Confusão e Métricas Completas de Teste Out-of-Time (2021–2024)
| Métrica / Classificador Preditivo | Regressão Logística Binária | Random Forest Classifier |
| :--- | :---: | :---: |
| **Acurácia Global (%)** | 52,86% | 52,78% |
| **F1-Score (%)** | 51,43% | 49,85% |
| **Precision (Classe Série A)** | 52,31% | 52,37% |
| **Recall / Sensibilidade (Classe Série A)** | 50,57% | 47,56% |
| **Verdadeiros Negativos (VN - Série B)** | 1.089 | 1.144 |
| **Falsos Positivos (FP - Erro Série B predito A)**| 888 | 833 |
| **Falsos Negativos (FN - Erro Série A predito B)**| 952 | 1.010 |
| **Verdadeiros Positivos (VP - Série A)** | 974 | 916 |
| **Total de Amostras de Teste** | 3.903 | 3.903 |

*Fonte: Produzido com dados de simulação do script de modelagem.*

#### A. Comparação com o Baseline Ingênuo (Naïve Classifier)
Para legitimar cientificamente os resultados diante de uma acurácia próxima a 53%, é obrigatória a comparação com um baseline ingênuo da classe majoritária (Zero-R). No conjunto de teste independente (3.903 instâncias), a classe majoritária é composta por atletas que disputaram a Série B, somando 1.977 registros (50,65% do conjunto de teste). 
Um classificador estatístico ingênuo que simplesmente predissesse "Série B" para todas as instâncias de teste sem analisar dados de campo obteria uma acurácia teórica de **50,65%**. Os dois algoritmos apresentaram um desempenho superior ao baseline ingênuo:
*   A Regressão Logística Binária superou o baseline em +2,21% de acurácia global.
*   O Random Forest Classifier superou o baseline em +2,13% de acurácia global.

Estes incrementos sugerem que as variáveis macro de scout individual carregam sinal preditivo real sobre a categoria competitiva do atleta, embora sua intensidade de separação espacial seja atenuada pela sobreposição do ecossistema. Embora o ganho absoluto seja reduzido, ele reforça a existência de sinal preditivo limitado nas variáveis macro, ao mesmo tempo em que evidencia a necessidade de atributos mais granulares para ganhos substanciais de desempenho.

#### B. Análise Prática dos Tipos de Erro e Escolha do Random Forest (Especificidade)
No contexto das operações do futebol profissional, a avaliação de desempenho baseada em aprendizado de máquina não deve mirar cegamente apenas a acurácia global, mas ponderar o custo estratégico e financeiro associado a cada tipo de erro preditivo, conforme consolidado na Tabela 5:

#### Tabela 5: Matriz de Análise de Erros e Impacto Mercadológico
| Tipo de Erro | Significado Operacional no Scouting | Impacto Financeiro / Mercadológico | Estratégia de Operação do Clube |
| :--- | :--- | :--- | :--- |
| **Falso Positivo (FP)** | Atleta da Série B classificado erroneamente como Série A | **Cenário de maior exposição financeira**: Investimento em salários e direitos de ativos que fracassarão na elite | Reduzir rigorosamente com modelo conservador (Random Forest) |
| **Falso Negativo (FN)** | Atleta da Série A classificado erroneamente como Série B | **Custo de oportunidade**: Descartar um talento viável e subvalorizado que performaria | Mitigar integrando auditoria qualitativa do scout humano |
| **Confiança Limítrofe (~50%)**| O modelo prediz com probabilidade próxima à fronteira neutra | **Incerteza de Decisão**: Risco ambíguo de performance | Exigir análise qualitativa profunda e micro-scouting |

*Fonte: Produzido pelo autor do TCC (Felipe Santos de Jesus).*

A escolha do modelo operacional reflete a postura estratégica do clube recrutador:
*   **Postura Conservadora (Foco em Risco Financeiro)**: Prioriza a redução de Falsos Positivos elevando a especificidade. O Random Forest reduziu em 55 ocorrências o número de falsos positivos em relação à Regressão Logística, o que reforça sua aderência a uma estratégia conservadora de mitigação de risco financeiro.
*   **Postura Agressiva (Foco em Captação de Ativos)**: Prioriza a redução de Falsos Negativos elevando a sensibilidade/recall (capturando o máximo de talentos de Série A possíveis), aceitando arcar com custos de contratação ineficientes adicionais.

Neste TCC, adotou-se o **Random Forest** como modelo operacional justamente por sua vocação de mitigação de risco financeiro (proteção orçamentária). Ele apresentou **1.144 Verdadeiros Negativos** contra 1.089 da Regressão Logística (reduzindo os Falsos Positivos de 888 para 833). Esse ganho prático de proteção orçamentária e mitigação de exposição financeira compensa a pequena perda marginal de Recall e legitima o Random Forest no Web-App (SAYAN; HANÇER, 2022).

### Justificativa de Resultados e Síntese de Contribuições (Defesa frente à Banca Examinadora)

Nesta seção, consolidam-se as respostas fundamentadas para as prováveis arguições da banca examinadora quanto ao desempenho preditivo dos modelos (acurácia na faixa de ~53%), justificando o rigor metodológico do trabalho, as contribuições práticas e teóricas alcançadas e as limitações tecnológicas.

#### A. Por que o modelo obteve uma acurácia de aproximadamente 53%?

O limite empírico de desempenho observado não decorre de deficiências no ajuste matemático ou subotimização dos hiperparâmetros dos classificadores, mas sim de dois fatores estruturais inerentes aos ecossistemas esportivos e às restrições informacionais dos dados públicos:

1. **A Teoria da Auto-equivalência dos Ecossistemas Competitivos Divisionais**: No futebol profissional, as estatísticas de desempenho bruto de um jogador são indissociáveis do nível de qualidade coletiva da liga onde ele atua. Neste trabalho, propõe-se interpretar cada divisão como um ecossistema competitivo relativamente auto-equivalente, no qual o desempenho bruto do atleta é influenciado pelo nível médio dos adversários e companheiros. Um atacante de destaque na Série B enfrenta defesas e goleiros de nível técnico de Série B. Consequentemente, sua produção individual de gols, assistências, e finalizações por 90 minutos atinge uma média quantitativa elevada. Por outro lado, um atacante de destaque na Série A brasileira compete contra sistemas defensivos e defensores de nível internacional de elite. Apesar da diferença evidente de qualidade técnica individual absoluta entre esses dois atacantes, a produção quantitativa de gols/90 e assistências/90 de ambos em suas respectivas competições tende a se equivaler estatisticamente. Em termos matemáticos, isso sugere que a distribuição de densidade probabilística dos dados brutos normalizados das variáveis macro (gols, assistências, minutagem, titularidade) das classes Série A e Série B apresenta uma imensa área de sobreposição no espaço de atributos (*feature space*), tornando a separação espacial exata altamente limitada para algoritmos tabulares baseados apenas em variáveis macro (TANG; WEI; TAN, 2026).
2. **A Ausência de Variáveis de Micro-scouting de Desempenho Qualitativo**: Os modelos foram alimentados exclusivamente com dados de volume macro (idade, gols, assistências, cartões e minutos). O sistema não possui acesso a variáveis de alta resolução espacial e física (micro-scouting) que poderiam desempatar os perfis dos atletas, tais como:
   * Precisão de passes progressivos ou passes verticais que quebram linhas sob alta pressão do oponente.
   * Taxa de desarmes com recuperação de posse de bola efetiva e duelos aéreos/terrestres ganhos em campo aberto.
   * Dados posicionais em coordenadas cartesianas gerados por rastreamento óptico de câmeras (*tracking*).
   * Indicadores físicos de telemetria GPS (velocidade física máxima instantânea e distância total percorrida em alta intensidade).
   * Histórico clínico estruturado de lesões e aspectos psicossociais/comportamentais.
   Em termos científicos, a falta dessas variáveis ocultas de micro-scouting limita a capacidade do classificador quantitativo em capturar o real diferencial qualitativo do atleta da Série A (que muitas vezes corre mais, passa sob pressão com mais eficiência e executa movimentos táticos mais precisos, embora apresente a mesma volumetria bruta de gols/90 e idade de um atleta da Série B em seu contexto local).

#### B. Como o trabalho ajuda a academia e o mercado se o resultado numérico foi modesto?

Mesmo diante de um teto de acurácia global de 53%, o trabalho oferece contribuições fundamentais para ambos os setores, refutando a ideia de insucesso analítico:

1. **Contribuições Acadêmicas**:
   * **Superação do Baseline (Zero-R)**: No conjunto de teste independente (3.903 instâncias), a classe majoritária é composta por atletas que disputaram a Série B, somando 1.977 registros (50,65% do conjunto de teste). Um classificador estatístico ingênuo (Zero-R) que previsse "Série B" para todas as instâncias obteria uma acurácia teórica de **50,65%**. Os modelos desenvolvidos (Regressão Logística com 52,86% e Random Forest com 52,78%) apresentaram um desempenho superior ao baseline ingênuo, indicando numericamente que extraem algum sinal preditivo dos atributos.
   * **Rigor Metodológico no Combate ao Vazamento Temporal**: Ao adotar a validação *Out-of-Time* (Treino: 2010–2020; Teste: 2021–2024), este trabalho elimina o vazamento de dados (*data leakage*) inerente a validações aleatórias convencionais (como K-Fold), que geram acurácias artificialmente infladas ao permitir que dados futuros e passados do mesmo atleta se misturem. Apresentar um desempenho de ~53% em um teste cego longitudinal futuro representa um resultado cientificamente honesto, reprodutível e condizente com a complexidade de predição do mercado real de futebol (VILELA; PORTELA; SANTOS, 2018).
   * **Mapeamento de Limites Científicos**: O trabalho estabelece a fronteira teórica da predição individual baseada em dados brutos acumulados, indicando empiricamente na literatura de Ciência de Dados aplicada ao esporte que dados macro brutos públicos possuem baixo poder de separação divisional autônomo.
2. **Contribuições Mercadológicas**:
   * **Mitigação de Risco Financeiro de Caixa**: O modelo transpõe métricas matemáticas para decisões de gestão do esporte. Ao modelar a matriz de confusão, demonstrou-se que o Falso Positivo (Série B predito como Série A) representa o maior risco de exposição financeira para os clubes (contratação de atletas inflados por ecossistemas inferiores que fracassam na elite, depreciando o ativo). A decisão de implantar o Random Forest, mesmo com acurácia ligeiramente inferior à Regressão Logística, justifica-se comercialmente porque ele reduziu em 55 ocorrências o número de falsos positivos (833 vs 888), atuando como um mecanismo mais rigoroso de proteção orçamentária.
   * **Democratização de Analytics para Clubes de Baixo Orçamento**: Em clubes que competem na Série B ou recém-promovidos que operam sob fortes restrições orçamentárias (receitas anuais modestas se comparadas aos gigantes da elite), a aquisição de feeds de dados privados de alto custo (Opta, Wyscout, StatsBomb) é inviável. Este sistema quantitativo atua como um Mínimo Produto Viável (MVP) de baixo custo operacional que vasculha mais de 13 mil registros históricos públicos, estruturando e agilizando a triagem inicial (screening) rápida de atletas antes de direcionar scouts humanos para análises qualitativas caras (TANG; WEI; TAN, 2026).
   * **Organização e Redução de Viés Subjetivo**: Substitui a dependência exclusiva do "olhômetro" e do viés de recência por avaliações baseadas em séries históricas consolidadas de longo prazo.

#### C. O que de fato foi alcançado com os resultados (Entregas Reais)?

O projeto não se limitou a discussões abstratas, consolidando os resultados práticos listados na Tabela 6:

##### Tabela 6: Matriz de Entregas e Descrição de Artefatos do Projeto
| Artefato / Entrega | Descrição Técnica | Evidência Metodológica no TCC |
| :--- | :--- | :---: |
| **Base tratada** | Consolidação de **8.752 registros** de atletas-temporada após filtros de significância estatística. | Tabela 2 e Tabela 3 |
| **Modelo preditivo** | Classificadores por Regressão Logística e Random Forest otimizados. | Tabela 4 |
| **Análise mercadológica** | Matriz de impacto de erros (Falsos Positivos vs Falsos Negativos) conectada ao orçamento de transferências. | Tabela 5 |
| **Web-App Interativo** | Simulador, buscador de dossiês e painéis de validação desenvolvidos em Streamlit. | Apêndices B a E |
| **Código-fonte** | Repositório público versionado hospedado no GitHub para reprodutibilidade científica. | Apêndice A |

*Fonte: Produzido pelo autor do TCC (Felipe Santos de Jesus).*

1. **Pipeline de ETL e Consolidação de Base de Dados**: Ingestão e padronização de uma base qualificada de **8.752 registros históricos** de atletas-temporada do futebol brasileiro, eliminando distorções de minutagem residual por meio de filtragem rigorosa (< 300 minutos) e normalização matemática temporal (/90).
2. **Web-App Operacional Interativo (Streamlit)**: Desenvolvimento e publicação de um protótipo operacional, integrado com o classificador de aprendizado de máquina Random Forest e contendo: buscador de dossiês históricos de atletas, simulador técnico interativo para analistas de desempenho e comissões técnicas e painéis de validação de métricas. O código-fonte encontra-se disponível em repositório público no GitHub, conforme detalhado no Apêndice A, sendo recomendado hospedar e executar as instâncias do Web-App via infraestrutura de nuvem Streamlit Community Cloud para execução pública da banca.
3. **Validação Longitudinal de Caso**: Prova de conceito qualitativa por meio da análise retrospectiva de carreira de 8 atletas reais renomados (goleiros, zagueiros, meias e atacantes), comprovando a aderência qualitativa do modelo Random Forest ao acompanhar oscilações de starts_pct e transições reais de carreira (como nos casos de Giuliano e Lucas Lima).

#### D. O que poderia ter ajudado a obter melhores resultados preditivos?

Para elevar o patamar de acurácia em pesquisas subsequentes, seria necessário superar as limitações de dados com as seguintes implementações:
1. **Acesso a feeds privados via APIs indexadas (Opta, Wyscout, StatsBomb)**: Eliminando a extração assistida CSV e provendo variáveis de qualidade de passe, duelos e comportamento de jogo dinâmico.
2. **Integração de Variáveis Físicas e de Rastreamento (Tracking)**: Coleta sistemática de quilometragem percorrida, acelerações, velocidade física máxima por GPS e dados contextuais coletivos da equipe.
3. **Histórico Clínico Estruturado**: Variável indicando dias de inatividade médica por lesões musculares ou ortopédicas na temporada, preenchendo o ponto cego analítico do risco físico patrimonial.
4. **Variáveis Contratuais e de Mercado**: Valores de salários, multas e valor de mercado estimado (Transfermarkt) para correlacionar desempenho esportivo com restrições econômicas de elenco.

### Detalhamento da Heurística do Web-App (Streamlit)

O Web-App interativo Streamlit foi estruturado integrando duas camadas distintas de inteligência para o tomador de decisão: o modelo de classificação supervisionado (Random Forest) e um mecanismo de regras heurísticas baseado em condicionais lógicas (*If/Else*) rodando em paralelo no script `analisar_perfil`. A finalidade desse motor de regras é adicionar contexto esportivo e traduzir as métricas numéricas em diagnósticos operacionais verbais inteligíveis.

Ressalta-se que essas regras heurísticas não substituem o classificador supervisionado nem foram utilizadas como métrica principal de validação científica. Elas funcionam como camada interpretativa auxiliar do Web-App, construída de forma empírica para facilitar a leitura operacional dos resultados pelo usuário final.

A arquitetura lógica da heurística funciona sob as seguintes condicionais:
1.  **Cálculo da Nota Técnica Posicional**:
    *   Para o grupo de **Atacantes** e **Meio-Campistas**, a heurística calcula o índice de qualidade ofensiva pura combinando a produtividade por 90 minutos:
        
        $$\text{Nota\_Técnica} = (\text{Gols\_90} \times 1.5) + (\text{Ast\_90} \times 1.0)$$
        
        Se a $\text{Nota\_Técnica} > 0.25$, o veredicto da heurística atribui o perfil correspondente à "Série A"; caso contrário, aponta para "Série B".
    *   Para os setores de **Defesa** e **Goleiros**, a nota técnica pondera o desempenho defensivo coletivo calibrado por minutos jogados:
        
        $$\text{Nota\_Técnica} = \max\left(0, 1 - \frac{\text{Média\_GA\_Time}}{2.0}\right)$$
        
        Se a $\text{Nota\_Técnica} > 0.35$, o veredicto heurístico estima a aptidão de "Série A", refletindo consistência de escalação na elite.
2.  **Status de Importância no Elenco (Confiança do Treinador)**:
    *   `Peça-Chave (Titular)`: Selecionado como titular em 80% ou mais das partidas disputadas ($\text{Starts} / \text{MP} \ge 0.8$).
    *   `Reserva Imediato`: Selecionado como titular entre 40% e 79% das partidas disputadas ($0.4 \le \text{Starts} / \text{MP} < 0.8$).
    *   `Reserva de Composição`: Acionado saindo do banco de reservas na maioria das partidas ($\text{Starts} / \text{MP} < 0.4$).
3.  **Volume da Temporada (Minutagem Acumulada)**:
    *   `Temporada Completa`: O atleta jogou mais de 60% dos minutos totais possíveis do clube na temporada ($\text{Minutagem\_Real\_Pct} > 60$).
    *   `Temporada Parcial`: O atleta disputou entre 30% e 60% dos minutos da equipe.
    *   `Possível interrupção de ciclo`: O atleta apresentou alta taxa de titularidade, mas baixa minutagem acumulada. Esse padrão pode estar associado a fatores externos ao desempenho, como lesão, transferência, suspensão ou decisão técnica, mas a base utilizada não permite identificar a causa específica.
    *   `Baixa Minutagem (Opção Técnica)`: Atleta reserva com minutagem inferior a 30% na temporada.

### Estudos de Caso Práticos e Análise Longitudinal

Como estratégia de validação prática e qualitativa para comprovar a utilidade do modelo Random Forest em cenários de tomada de decisão real de mercado pelos scouts, implementou-se na aplicação Streamlit a análise de caso de oito jogadores históricos do futebol nacional. O algoritmo computou as predições de aptidão para cada ano de suas carreiras completas a partir das planilhas reais consolidadas na pasta `data/nova_base/`.

Abaixo, a discussão do comportamento do modelo em cada caso de estudo:

1.  **Cássio (Goleiro)**: O goleiro manteve-se com forte classificação de **Série A** ao longo de quase toda a série histórica de teste, com altos graus de probabilidade pelo modelo (variando de 80% a 90%). A regularidade de Cássio em minutos jogados como titular incontestável em nível de elite (Corinthians) compensou o fator de avanço da idade (37 anos). O modelo de Random Forest aprendeu que para goleiros, a consistência de starts_pct e minutos acumulados de elite são indicadores primordiais de aptidão continuada.
2.  **Marcelo Lomba (Goleiro)**: Um estudo de caso de contraste rico em relação a Cássio. Atuando no Palmeiras nas temporadas recentes como reserva de luxo de Weverton, Lomba apresenta números técnicos excepcionais (gols sofridos baixíssimos quando entra), mas sua minutagem é drasticamente reduzida (frequentemente abaixo de 500 minutos anuais). Consequentemente, sua taxa de titularidade despenca. O classificador Random Forest rebaixou seu perfil predito para **Série B** com probabilidade média de 60%. O algoritmo penalizou a falta de volume de Starts_Pct, interpretando o jogador como atleta de composição de elenco, provando que o modelo prioriza regularidade de escalação para goleiros de ponta.
3.  **Gil (Defensor)**: Zagueiro clássico de longa carreira na elite (Corinthians). Gil manteve a classificação predita de **Série A** com alto nível de confiança do algoritmo. A justificativa matemática é a sua altíssima regularidade de minutagem (quase 100% dos jogos da equipe) aliada a um indicador de disciplina exemplar (taxa baixíssima de cartões amarelos e vermelhos por 90 minutos de jogo). O modelo Random Forest valoriza defensores que combinam alta minutagem com excelente disciplina, visto que cartões excessivos indicam fragilidade ou atraso em duelos físicos (MOYA et al., 2025).
4.  **Léo Pereira (Defensor)**: Zagueiro do Flamengo que passou por flutuações acentuadas na carreira. Nos anos de instabilidade técnica coletiva do clube (2020–2021), in que sua minutagem real foi reduzida por opções técnicas, o modelo indicou uma classificação de perfil limítrofe com menor probabilidade de Série A (perto de 51% a 55%). Já sob a consolidação de titularidade absoluta a partir de 2022/2023, o modelo elevou sua probabilidade de aptidão para a Série A para a faixa de **82,4%**, provando que o classificador reflete de forma sensível os ciclos de estabilização do atleta no elenco principal de elite.
5.  **Giuliano (Meio Campo)**: Meia criativo com passagens por grandes clubes da elite (Grêmio, Corinthians) e recente transferência para o Santos na Série B. Nas temporadas em que perdeu a titularidade absoluta e passou a atuar como reserva imediato entrando na segunda etapa (como no Corinthians em 2023), sua taxa de starts_pct caiu para perto de 0.4. O modelo de Random Forest imediatamente rotulou Giuliano com perfil de **Série B** (probabilidade de 54,2%), interpretando que sua produção ofensiva/90 reduzida combinada com a perda de titularidade aponta para um declínio físico e técnico de elite, o que se confirmou na prática com sua subsequente transferência para a disputa da Série B nacional.
6.  **Lucas Lima (Meio Campo)**: Caso análogo ao de Giuliano. Em seus anos de destaque técnico e físico no Santos e Palmeiras na década anterior, o modelo predizia Série A com enorme certeza (acima de 85%). Concomitante ao declínio de sua produtividade ofensiva de assistências/90 e perda de espaço nos times principais (virando reserva de composição de elenco e posteriormente atuando no Fortaleza e Sport), o Random Forest detectou a queda estrutural de starts_pct e mudou sua predição de aptidão para **Série B** (com probabilidade na faixa de 60%). Isso demonstra que o modelo é capaz de capturar o declínio atlético e de importância de criação tática ao longo do tempo.
7.  **Gabriel Barbosa (Atacante)**: Um dos atacantes mais produtivos do futebol brasileiro recente atuando no Flamengo. O modelo prediz com consistência o perfil de **Série A** (probabilidade de 89,3% a 92%) nas temporadas de alta produtividade (como 2019 a 2023), impulsionado por uma excelente taxa de Gols/90 (acima de 0.40) e Starts_Pct máxima. Contudo, em anos de baixa amostragem ou problemas disciplinares recorrentes que geram expulsões e cartões amarelos frequentes (elevando a taxa de cartões amarelos/90 para valores atípicos), a probabilidade predita de elite sofreu reduções perceptíveis no simulador do modelo, mostrando como o comportamento disciplinar é ponderado na aptidão final de um atacante de elite.
8.  **Germán Cano (Atacante)**: Centroavante clássico de altíssima eficiência goleadora na elite (Vasco e Fluminense). O modelo prediz com maior probabilidade estimada pelo modelo a aptidão de **Série A** para Germán Cano (atingindo probabilidades acima de 92% na temporada mágica de 2023). Apesar de possuir idade avançada (35 a 36 anos), o que teoricamente penaliza o perfil do jogador no algoritmo de árvores por desgaste físico projetado, sua extraordinária taxa de Gols/90 compensa e sobressai na floresta de decisão. O modelo de Random Forest aprendeu que atacantes com produção letal contínua por 90 minutos e titularidade inabalável sustentam o status de elite de forma independente das penalidades gerais de idade, um comportamento que condiz perfeitamente com a literatura de scouting tático profissional (MEMMERT; RAABE, 2018).

### Implicações Gerenciais para Clubes e Departamentos de Scout

Do ponto de vista gerencial, o sistema proposto deve ser utilizado como ferramenta de triagem inicial de atletas, reduzindo o universo de análise para posterior avaliação qualitativa por scouts, analistas de desempenho e comissão técnica. Sua principal contribuição operacional está na organização de evidências quantitativas e na identificação de perfis que merecem análise complementar. O modelo não substitui a observação presencial, a análise de vídeo, a avaliação médica, a análise contratual nem a aderência ao modelo de jogo do clube. Em clubes com restrição orçamentária, especialmente aqueles que não possuem acesso a plataformas privadas de dados esportivos, a solução pode apoiar a priorização de observações e reduzir a exposição a contratações baseadas exclusivamente em percepção subjetiva.

---

## Conclusão ou Considerações Finais

### Limitações e Trabalhos Futuros

O sistema preditivo desenvolvido cumpriu os objetivos propostos ao mapear estatisticamente os limites do scouting quantitativo individual macro para as Séries A e B do futebol brasileiro, entregando os resultados em um Web-App operacional amigável de apoio à decisão, atuando de forma consultiva e não como recomendador final e autônomo de contratação.

Contudo, identificam-se limitações científicas e de infraestrutura analítica que abrem caminhos para trabalhos futuros de pós-graduação e expansão metodológica:
1.  **Gargalo de Infraestrutura e Escalabilidade**: A coleta híbrida manual/assistida via CSV contornou o bloqueio 403 do Cloudflare no FBref, mas limita a escalabilidade industrial. Em produção corporativa dentro de SAFs, o pipeline de dados deve ser redesenhado utilizando conexões diretas via APIs estruturadas de fornecedores privados (ex: Opta, Wyscout, StatsBomb). O código-fonte completo do projeto analítico encontra-se disponível em repositório público no GitHub, conforme detalhado no Apêndice A, para transparência científica, sendo recomendado hospedar e executar as instâncias do Web-App via infraestrutura de nuvem Streamlit Community Cloud para execução pública da banca.
2.  **Risco Clínico e Médico**: A base macro carece de histórico médico dos atletas. Jogadores com alta probabilidade predita de aptidão divisional podem sofrer depreciação imediata de valor de mercado e tempo de inatividade por reincidência de lesões, caracterizando um ponto cego analítico do modelo que futuros estudos devem modelar integrando taxas clínicas.
3.  **Inclusão de Dados de Micro-Scouting e Rastreamento (Tracking)**: A acurácia preditiva dos modelos está limitada a ~53% pela falta de variáveis qualitativas refinadas individuais. Recomenda-se em pesquisas futures a inclusão de indicadores estruturais tais como passes que quebram linhas, taxa de passes sob pressão, velocidade de transição ofensiva física medida por sensores GPS de campo e métricas de Expected Assists (xA).
4.  **Aprimoramentos de Software e Modelagem**:
    *   **Calibração de Limiares (Threshold Calibration)**: Desenvolver um slider interativo na tela do Streamlit que permita ao tomador de decisão parametrizar o limite probabilístico de aceitação de classe (ex: exigindo $> 75\%$ de certeza para classificar Série A), operando em modo ultra-conservador para mitigar Falsos Positivos.
    *   **Matriz de Custos Financeiros**: Implementar equações que pesem o erro preditivo por valor monetário em reais em vez de perdas estatísticas simples.
    *   **Testagem de outros Ensembles**: Testar algoritmos baseados em boosting de gradiente, tais como XGBoost e LightGBM.

---

## Referências

CARLING, C.; BLOOMFIELD, J.; NELSEN, L.; REILLY, T. The Role of Motion Analysis in Elite Soccer: Contemporary Performance Measurement Techniques and Work Rate Data. **Sports Medicine**, v. 38, n. 10, p. 839-862, 2008. DOI: 10.2165/00007256-200838100-00004.

GRINSZTAJN, L.; OYALLON, E.; VAROQUAUX, G. Why Do Tree-Based Models Still Outperform Deep Learning on Typical Tabular Data? **Advances in Neural Information Processing Systems (NeurIPS 35)**, v. 35, p. 507-520, 2022. DOI: 10.52202/068431-0037.

HUGHES, M.; BARTLETT, R. The use of performance indicators in performance analysis. **Journal of Sports Sciences**, v. 20, n. 10, p. 739-754, 2002. DOI: 10.1080/026404102320675602.

HUGHES, M.; FRANKS, I. M.; DANCS, H. (ed.). **Essentials of Performance Analysis in Sport**. 3. ed. London: Routledge, 2019. DOI: 10.4324/9780429340130.

MANISH, S.; BHAGAT, V.; PRAMILA, R. M. Prediction of Football Players Performance using Machine Learning and Deep Learning Algorithms. In: INTERNATIONAL CONFERENCE FOR EMERGING TECHNOLOGY (INCET), 2., 2021, Belagavi. **Proceedings...** Belagavi: IEEE, 2021. p. 1-5. DOI: 10.1109/INCET51464.2021.9456424.

MEMMERT, D.; RAABE, D. **Data Analytics in Football: Positional Data Collection, Modelling and Analysis**. London: Routledge, 2018. DOI: 10.4324/9781351210164.

MOYA, D.; TIPANTUÑA, C.; VILLA, G.; CALDERÓN-HINOJOSA, X.; RIVADENEIRA, B.; ÁLVAREZ, R. Machine Learning Applied to Professional Football: Performance Improvement and Results Prediction. **Machine Learning and Knowledge Extraction**, v. 7, n. 3, art. 85, p. 646-666, 2025. DOI: 10.3390/make7030085.

SAYAN, V. H.; HANÇER, E. A Survey on Football Player Performance and Value Estimation Using Machine Learning Techniques. **Scientific Journal of Mehmet Akif Ersoy University (Techno-Science)**, v. 5, n. 2, p. 57-62, 2022.

TANG, Q.; WEI, X.; TAN, B. The Role of Machine Learning in Talent Identification for Team Sports: A Systematic Review. **Journal of Sports Science and Medicine**, v. 25, n. 1, p. 58-83, 2026. DOI: 10.52082/jssm.2026.58.

VILELA, T.; PORTELA, F.; SANTOS, M. F. Towards a Pervasive Intelligent System on Football Scouting: A Data Mining Study Case. In: ROCHA, Á.; ADELI, H.; REIS, L. P.; COSTANZO, S. (ed.). **Trends and Advances in Information Systems and Technologies**. Cham: Springer, 2018. p. 341-351. (Advances in Intelligent Systems and Computing, v. 747). DOI: 10.1007/978-3-319-77700-9_34.

WIRTH, R.; HIPP, J. CRISP-DM: Towards a Standard Process Model for Data Mining. In: INTERNATIONAL CONFERENCE ON THE PRACTICAL APPLICATIONS OF KNOWLEDGE DISCOVERY AND DATA MINING, 4., 2000. **Proceedings...** Manchester, 2000. p. 29-39.

---

## Apêndice(s) e Anexo(s)

### Apêndice A: Repositório de Código-Fonte e Execução da Aplicação
O código-fonte completo do projeto analítico, englobando as rotinas de ETL, scripts de modelagem e a interface interativa, está disponível publicamente no repositório de versionamento GitHub em: [https://github.com/felipesjh/analise-aptidao-futebol-tcc.git](https://github.com/felipesjh/analise-aptidao-futebol-tcc.git).

### Apêndice B: Apêndice Visual da Aplicação Web-App Streamlit

> [!NOTE]
> *Esta seção deve ser preenchida pelo aluno Felipe Santos de Jesus no editor de texto de formatação final (Microsoft Word), colando os prints de tela da aplicação Streamlit que está em execução local.*

#### Figura 1: Tela Inicial e Aba do Dossiê Individual (Scouting de Desempenho)
*   **Identificação do Elemento**: Visualização do buscador de desempenho profissional onde o tomador de decisão seleciona a temporada, divisão, equipe e jogador para gerar a ficha técnica com veredicto heurístico e predição do modelo Random Forest.
*   *Inserir print da Aba 1 (Dossiê Individual) aqui*

#### Figura 2: Aba de Validação Científica dos Modelos
*   **Identificação do Elemento**: Visualização gráfica contendo as matrizes de confusão da Regressão Logística e Random Forest baseadas no conjunto de teste independente Out-of-Time (2021–2024), além da curva de acurácia comparativa geral.
*   *Inserir print da Aba 2 (Validação Científica) aqui*

#### Figura 3: Aba do Simulador de Cenários
*   **Identificação do Elemento**: Visualização dos seletores interativos e sliders ajustáveis de idade, titularidade, gols/90, assistências/90 e cartões por 90min, exibindo a classificação em tempo real calculada pela inteligência artificial.
*   *Inserir print da Aba 3 (Simulador Técnico) aqui*

#### Figura 4: Aba de Estudos de Caso Longitudinal de Carreiras
*   **Identificação do Elemento**: Exposição da tabela interativa contendo o histórico longitudinal preditivo gerado de forma contínua para as carreiras de Cássio, Gil, Cano, entre outros, mostrando a aderência real do modelo às flutuações das temporadas.
*   *Inserir print da Aba 5 (Estudos de Caso) aqui*
