from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import xgboost as xgb
import pandas as pd
import pickle
import os

def treinar_modelo_baseline(X_train, y_train):
    """Regressão Logística como Baseline Interpretável"""
    clf = LogisticRegression(class_weight='balanced', max_iter=1000)
    clf.fit(X_train, y_train)
    return clf

def treinar_modelo_avancado(X_train, y_train):
    """Random Forest atuando como classificador robusto para dados tabulares"""
    clf = RandomForestClassifier(n_estimators=150, class_weight='balanced', random_state=42)
    clf.fit(X_train, y_train)
    return clf

def salvar_modelo(modelo, caminho_salvamento: str):
    with open(caminho_salvamento, 'wb') as f:
        pickle.dump(modelo, f)

if __name__ == "__main__":
    print("Preparando infraestrutura de Modelagem (TCC)...")
    os.makedirs("../../app/assets", exist_ok=True)
    # Fluxo principal de ingestão será chamado daqui
