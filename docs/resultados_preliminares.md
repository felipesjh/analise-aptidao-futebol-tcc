# Resultados de Modelagem e Validação Temporal Out-of-Time (2021-2024)

Este documento consolida os resultados reais gerados pelo pipeline de Machine Learning em `src/modelagem/executar_pipeline.py`.

---

## Estrutura de Modelagem e Dados
*   **Período de Treinamento (Histórico)**: Temporadas de **2010 a 2020** inclusive.
*   **Período de Teste (Temporal Futuro)**: Temporadas de **2021 a 2024** inclusive.
*   **Filtro de Amostragem**: Minutagem mínima em campo de **300 minutos** na temporada.
*   **Volume Final**:
    *   Instâncias de Treino: **4.849** (Série A: 2.385, Série B: 2.464)
    *   Instâncias de Teste: **3.903** (Série A: 1.926, Série B: 1.977)

---

## Desempenho Comparativo dos Modelos

### 1. Regressão Logística Binária (Baseline)
*   **Acurácia**: **52,86%**
*   **F1-Score**: **51,43%**
*   **Matriz de Confusão**:
    ```
    [[1089  888]  <- Classe 0 (Série B): Verdadeiros Negativos (1089) | Falsos Positivos (888)
     [ 952  974]]  <- Classe 1 (Série A): Falsos Negativos (952)      | Verdadeiros Positivos (974)
    ```

### 2. Random Forest Classifier (Modelo Final Operacional)
*   **Acurácia**: **52,78%**
*   **F1-Score**: **49,85%**
*   **Matriz de Confusão**:
    ```
    [[1144  833]  <- Classe 0 (Série B): Verdadeiros Negativos (1144) | Falsos Positivos (833)
     [1010  916]]  <- Classe 1 (Série A): Falsos Negativos (1010)     | Verdadeiros Positivos (916)
    ```

---

## Conclusões de Operação
Embora as métricas globais sejam muito similares, o **Random Forest** foi selecionado para compor o Web-App Streamlit devido à maior especificidade na classe Série B (revelada pela taxa de 1.144 Verdadeiros Negativos contra 1.089 da Regressão Logística). Isso minimiza o erro de Falso Positivo, blindando o caixa dos clubes contra compras de jogadores que não performarão na divisão de elite.
