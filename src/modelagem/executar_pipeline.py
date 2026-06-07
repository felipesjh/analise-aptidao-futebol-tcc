import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score

def carregar_e_preparar_dados():
    path_jog = 'data/processed_tcc/jogadores_consolidado.csv'
    path_camp = 'data/processed_tcc/campeonato_consolidado.csv'
    
    if not os.path.exists(path_jog) or not os.path.exists(path_camp):
        raise FileNotFoundError("Bases consolidadas não encontradas em data/processed_tcc/")
        
    df_jog = pd.read_csv(path_jog)
    df_camp = pd.read_csv(path_camp)
    
    # Padronização e limpeza
    df_jog['Posicao_Original'] = df_jog['Pos']
    df_jog = df_jog.rename(columns={'Player': 'Nome', 'Squad': 'Time', 'Pos': 'Posicao'})
    
    mapa_pos = {'FW': 'Atacante', 'MF': 'Meio Campo', 'DF': 'Defensor', 'GK': 'Goleiro'}
    df_jog['Posicao_Grupo'] = df_jog['Posicao'].astype(str).str.split(',').str[0].map(mapa_pos).fillna('Outros')
    
    cols_num = ['Gls', 'Ast', 'Min', '90s', 'Age', 'MP', 'CrdY', 'CrdR', 'Starts']
    for col in cols_num:
        if col in df_jog.columns:
            df_jog[col] = pd.to_numeric(df_jog[col], errors='coerce').fillna(0)
            
    # Filtro de Minutagem Mínima (evitar distorções bizzaras de /90 com pouquíssimos minutos)
    df_jog = df_jog[df_jog['Min'] >= 300].copy()
    
    # Calcular Métricas por 90 minutos
    df_jog['Gols_90'] = df_jog['Gls'] / df_jog['90s'].replace(0, 1)
    df_jog['Ast_90'] = df_jog['Ast'] / df_jog['90s'].replace(0, 1)
    df_jog['Cartoes_Y_90'] = df_jog['CrdY'] / df_jog['90s'].replace(0, 1)
    df_jog['Cartoes_R_90'] = df_jog['CrdR'] / df_jog['90s'].replace(0, 1)
    df_jog['Starts_Pct'] = (df_jog['Starts'] / df_jog['MP'].replace(0, 1)).clip(0, 1)
    
    # Mesclar com os dados de classificação das equipes para dar o contexto de tabela
    df_camp = df_camp.rename(columns={
        'Squad': 'Time', 
        'GA': 'Gols_Sofridos_Equipe_Total', 
        'MP': 'Jogos_Totais_Equipe', 
        'Rk': 'Posicao_Tabela_Equipe',
        'W': 'Vitorias_Time',
        'D': 'Empates_Time',
        'L': 'Derrotas_Time',
        'Pts': 'Pontos_Time'
    })
    
    cols_sel_camp = ['Time', 'Ano', 'Divisao', 'Gols_Sofridos_Equipe_Total', 'Jogos_Totais_Equipe', 'Posicao_Tabela_Equipe', 'Vitorias_Time', 'Empates_Time', 'Derrotas_Time', 'Pontos_Time']
    df_final = df_jog.merge(df_camp[cols_sel_camp], on=['Time', 'Ano', 'Divisao'], how='left')
    
    # Preencher dados vazios do time se houver
    for col in ['Gols_Sofridos_Equipe_Total', 'Jogos_Totais_Equipe', 'Posicao_Tabela_Equipe', 'Vitorias_Time', 'Empates_Time', 'Derrotas_Time', 'Pontos_Time']:
        df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(0)
        
    df_final['Aproveitamento_Equipe_Pct'] = (df_final['Pontos_Time'] / (df_final['Jogos_Totais_Equipe'].replace(0, 38) * 3) * 100).clip(0, 100)
    df_final['Minutagem_Real_Pct'] = (df_final['Min'] / (df_final['Jogos_Totais_Equipe'].replace(0, 38) * 90) * 100).clip(0, 100)
    df_final['Media_GA_Time'] = df_final['Gols_Sofridos_Equipe_Total'] / df_final['Jogos_Totais_Equipe'].replace(0, 1)
    df_final['Gols_Sofridos_Atleta_Estimado'] = (df_final['Gols_Sofridos_Equipe_Total'] * (df_final['Minutagem_Real_Pct'] / 100)).round(0)
    
    return df_final

def treinar_e_avaliar():
    df = carregar_e_preparar_dados()
    
    # Criar variáveis Dummy de Posição
    df_dummies = pd.get_dummies(df['Posicao_Grupo'], prefix='Pos', dtype=float)
    df = pd.concat([df, df_dummies], axis=1)
    
    # Garantir que todas as colunas de posição possíveis existam no dataset
    for pos_col in ['Pos_Atacante', 'Pos_Meio Campo', 'Pos_Defensor', 'Pos_Goleiro']:
        if pos_col not in df.columns:
            df[pos_col] = 0.0
            
    # Definir as features de treinamento
    features = [
        'Age', 'Gols_90', 'Ast_90', 'Cartoes_Y_90', 'Cartoes_R_90', 'Starts_Pct',
        'Pos_Atacante', 'Pos_Meio Campo', 'Pos_Defensor', 'Pos_Goleiro'
    ]
    
    target = 'Divisao' # Alvo
    
    # Codificar alvo: Série A = 1, Série B = 0
    df['target'] = df[target].map({'Série A': 1, 'Série B': 0}).fillna(0).astype(int)
    
    # Divisão Temporal Out-of-Time
    # Treino: 2016-2020
    # Teste: 2021-2024
    df_train = df[df['Ano'] <= 2020].copy()
    df_test = df[df['Ano'] >= 2021].copy()
    
    X_train = df_train[features].fillna(0)
    y_train = df_train['target']
    
    X_test = df_test[features].fillna(0)
    y_test = df_test['target']
    
    print(f"Instâncias de Treino (2016-2020): {len(X_train)} (Série A: {sum(y_train == 1)}, Série B: {sum(y_train == 0)})")
    print(f"Instâncias de Teste (2021-2024): {len(X_test)} (Série A: {sum(y_test == 1)}, Série B: {sum(y_test == 0)})")
    
    # 1. Regressão Logística (Baseline)
    lr = LogisticRegression(class_weight='balanced', max_iter=2000, random_state=42)
    lr.fit(X_train, y_train)
    y_pred_lr = lr.predict(X_test)
    
    # 2. Random Forest (Classificador Avançado)
    rf = RandomForestClassifier(n_estimators=150, max_depth=12, class_weight='balanced', random_state=42)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    
    # Avaliação
    acc_lr = accuracy_score(y_test, y_pred_lr)
    f1_lr = f1_score(y_test, y_pred_lr)
    
    acc_rf = accuracy_score(y_test, y_pred_rf)
    f1_rf = f1_score(y_test, y_pred_rf)
    
    print("\n" + "="*40)
    print("MÉTRICAS DO MODELO BASELINE (REGRESSÃO LOGÍSTICA)")
    print("="*40)
    print(f"Acurácia: {acc_lr:.4f}")
    print(f"F1-Score: {f1_lr:.4f}")
    print("\nRelatório de Classificação:")
    print(classification_report(y_test, y_pred_lr, target_names=['Série B', 'Série A']))
    print("Matriz de Confusão:")
    cm_lr = confusion_matrix(y_test, y_pred_lr)
    print(cm_lr)
    
    print("\n" + "="*40)
    print("MÉTRICAS DO MODELO AVANÇADO (RANDOM FOREST)")
    print("="*40)
    print(f"Acurácia: {acc_rf:.4f}")
    print(f"F1-Score: {f1_rf:.4f}")
    print("\nRelatório de Classificação:")
    print(classification_report(y_test, y_pred_rf, target_names=['Série B', 'Série A']))
    print("Matriz de Confusão:")
    cm_rf = confusion_matrix(y_test, y_pred_rf)
    print(cm_rf)
    
    # Salvar modelos na pasta app/assets/ para que o streamlit use
    os.makedirs('app/assets', exist_ok=True)
    with open('app/assets/modelo_rf_final.pkl', 'wb') as f:
        pickle.dump(rf, f)
        
    with open('app/assets/modelo_lr_final.pkl', 'wb') as f:
        pickle.dump(lr, f)
        
    # Salvar as métricas reais em formato texto/json para que o streamlit possa exibir
    metrics_summary = {
        'lr_accuracy': acc_lr,
        'lr_f1': f1_lr,
        'lr_cm': cm_lr.tolist(),
        'rf_accuracy': acc_rf,
        'rf_f1': f1_rf,
        'rf_cm': cm_rf.tolist(),
        'features': features
    }
    with open('app/assets/metricas_modelos.pkl', 'wb') as f:
        pickle.dump(metrics_summary, f)
        
    print("\nModelos e métricas reais exportados com sucesso em app/assets/")
    
if __name__ == "__main__":
    treinar_e_avaliar()
