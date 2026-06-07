# Metodologia de Modelagem e Arquitetura de Dados

# 1. Fonte dos Dados e Restrições de Aquisição (Web Scraping)
As estatísticas utilizadas neste projeto foram inteiramente provenientes do portal de estatísticas globais esportivas **FBref**. O foco incide em dados tabulares consolidados por temporada de jogadores de nível profissional.

### 1.1 Limitações de Acesso e Justificativa Metodológica (Block 403 Forbidden)
Durante o desenvolvimento do mecanismo de extração autônoma via Python HTTP (`requests` / `BeautifulSoup`), constatou-se que o portal FBref utiliza severas camadas de proteção anti-Bot e anti-DDoS (como o Cloudflare). A requisição massiva e sequencial de dados tabulares resulta no imediato bloqueio do IP do requisitante retornando o Erro de Servidor `403 Forbidden`, inviabilizando a ingestão em grande escala automatizada.

Para contornar isso de forma acadêmica e metodológica (garantindo a integridade e completude da base), definiu-se que a extração primária dos dados brutos deve ocorrer de forma híbrida ou manual: recorrendo às ferramentas de *"Share / Export as CSV"* (fornecidas nativamente na interface web do próprio portal para evitar quebra de regras) ou utilizando bases abertas no *Kaggle* derivadas de atualizações permitidas do portal. Isso assegura que o escopo de dados (Série A, B e C) chegue à fase de Tratamento do pipeline totalmente livre de ruídos ou bloqueios.

## 2. Divisão Temporal (Out-of-Time Validation)
Para refletir um cenário realístico de tomada de decisão (Scouting), os dados foram separados temporalmente:
- **Treinamento e Validação Interna:** Temporadas de 2010 até 2020.
- **Teste Independente Temporal:** Temporadas de 2021 até 2024. Este particionamento temporal visa garantir que o modelo não faça vazamento de dados do futuro (data leakage) e nos permita aferir se os padrões encontrados em anos anteriores ainda garantem performance em casos recentes.

## 3. Seleção dos Algoritmos de Machine Learning
Para problemas compostos por dados tabulares numéricos com um número discreto de instâncias, e demandando rigorosa explicação para os parceiros de negócios (clubes / olheiros), o escopo foi restrito a:

- **Regressão Logística (Multinomial)**: Atua como um *baseline*. Muito valorizado pela extrema facilidade em observar as probabilidades proporcionais associadas aos coeficientes (peso das variáveis).
- **Algoritmos Ensemble de Árvores (Random Forest e XGBoost)**: Lidam de maneira inigualável com relações não-lineares, sem que haja necessidade extrema de transformar todas as *features*, além de fornecerem a importante métrica de *Feature Importance* com Gini/Shap values.

### Por que a exclusão de Deep Learning?
Modelos pautados em Redes Neurais (*Deep Learning*) requerem grandes volumes para justificar a superação dos limiares de *Ensembles*. Segundo diversos autores de aprendizado para dados tabulares pequenos, o uso de Deep Learning incorre em dois grandes riscos em um cenário de TCC como este:
1. **Riscos de Overfitting**: Com base em poucas dezenas de milhares de registros esparsos.
2. **Deficiência na Interpretabilidade ("Black Box")**: Dificuldade substancial em convencer ou provar de modo trivial para o conselho (Banca Examinadora / Departamento de Scout) porque o algoritmo pontuou a adequação à Série A.

## 4. Avaliação
Neste limiar de classificação multiclasse e desbalanceada, usaremos como referencial de desempenho a F1-Score (média Harmônica entre Recall e Precision).
