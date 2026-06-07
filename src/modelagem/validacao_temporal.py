import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
import pickle
import os

def carregar_modelo_treinado(caminho: str):
    """Carrega o classificador salvo."""
    if os.path.exists(caminho):
        with open(caminho, 'rb') as f:
            return pickle.load(f)
    print("Modelo não encontrado.")
    return None

def validar_transferencias(caminho_modelo: str, caminho_dados_teste: str):
    """
    Aplica o classificador preditivo (treinado em 2010-2020)
    sobre os dados de teste (2021-2024).
    """
    print("-----------------------------------------------------")
    print(" VALIDAÇÃO TEMPORAL OUT-OF-TIME (ESTUDO DE CASO)     ")
    print("-----------------------------------------------------")
    
    modelo = carregar_modelo_treinado(caminho_modelo)
    if not modelo: return
    
    if not os.path.exists(caminho_dados_teste):
        print(f"Base de teste {caminho_dados_teste} não existe.")
        return
        
    df_teste = pd.read_csv(caminho_dados_teste)
    
    # 1. Separar as features da variável alvo
    target = 'Divisao_Alvo'
    # Features serão as colunas que têm '_p90' + algumas básicas, isso varia base no processo
    X_test = df_teste[[c for c in df_teste.columns if c.endswith('_p90') or c == 'Age']]
    X_test.fillna(0, inplace=True)
    y_test = df_teste[target]
    
    # 2. Realizar a predição real
    print(f"\\nAvaliando {len(X_test)} jogadores do período recente...")
    previsoes = modelo.predict(X_test)
    
    # 3. Reportar Matriz
    print("\\n[Acurácia e Métricas F1-Score: Realidade vs Predito]")
    print(classification_report(y_test, previsoes))
    
    print("Matriz de Confusão:")
    print(confusion_matrix(y_test, previsoes))
    
if __name__ == "__main__":
    validar_transferencias(
        "../../app/assets/modelo_logreg_2010_2020.pkl", 
        "../../data/processed/dados_finais_teste_2021_2024.csv"
    )
