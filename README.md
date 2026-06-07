# Sistema Preditivo: Aptidão de Jogadores para as Divisões Brasileiras

Este projeto é fruto de um Trabalho de Conclusão de Curso (TCC) em Ciência de Dados, desenvolvido para avaliar a aptidão de jogadores de futebol para atuar nas Séries A, B e C do campeonato brasileiro, com base em dados detalhados extraídos do FBref.

## Visão Geral

Através do levantamento histórico (2010 a 2024), utilizamos algoritmos de Machine Learning interpretáveis (como *Random Forest* e *Logistic Regression*) para mapear os KPIs (indicadores) que formam um jogador típico para cada divisão, testando um modelo "Out-of-Time", ou seja, treinamos com dados de uma década e testamos a eficácia nas transferências recentes.

## Estrutura do Projeto

* `data/raw`: Dados não estruturados, diretamente obtidos do portal original.
* `data/processed`: Dados tratados e limpos, prontos para a Ingestão do Modelo.
* `src/coleta`: Scripts responsáveis pela coleta de informações, respeitando as políticas do provedor dos dados.
* `src/tratamento`: ETL (Extração, Transformação e Carga) e uniformização dos atributos.
* `src/modelagem`: Processo de Machine Learning e geração dos arquivos binários (`.pkl`).
* `app/`: Front-End construído utilizando o Framework Streamlit para facilitar as inferências dos usuários.
* `docs/`: Documentação adicional e detalhes da metodologia do TCC.

## Como começar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Para executar o Web-App:
   ```bash
   streamlit run app/app.py
   ```
