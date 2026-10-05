import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score, roc_auc_score, precision_score, recall_score

def carregar_e_preparar_dados():
    path_jog = 'data/processed_tcc/jogadores_consolidado.csv'
    path_camp = 'data/processed_tcc/campeonato_consolidado.csv'
    
    if not os.path.exists(path_jog) or not os.path.exists(path_camp):
        raise FileNotFoundError("Bases consolidadas não encontradas em data/processed_tcc/")
        
    df_jog = pd.read_csv(path_jog)
    df_camp = pd.read_csv(path_camp)
    
    # Padronização de colunas
    df_jog['Posicao_Original'] = df_jog['Pos']
    df_jog = df_jog.rename(columns={'Player': 'Nome', 'Squad': 'Time', 'Pos': 'Posicao'})
    
    mapa_pos = {'FW': 'Atacante', 'MF': 'Meio Campo', 'DF': 'Defensor', 'GK': 'Goleiro'}
    df_jog['Posicao_Grupo'] = df_jog['Posicao'].astype(str).str.split(',').str[0].map(mapa_pos).fillna('Outros')
    
    cols_num = ['Gls', 'Ast', 'Min', '90s', 'Age', 'MP', 'CrdY', 'CrdR', 'Starts', 'G-PK']
    for col in cols_num:
        if col in df_jog.columns:
            df_jog[col] = pd.to_numeric(df_jog[col], errors='coerce').fillna(0)
            
    df_jog = df_jog[df_jog['Min'] >= 300].copy()
    
    df_jog['Gols_90'] = df_jog['Gls'] / df_jog['90s'].replace(0, 1)
    df_jog['Ast_90'] = df_jog['Ast'] / df_jog['90s'].replace(0, 1)
    df_jog['GPK_90'] = (df_jog['G-PK'] / df_jog['90s'].replace(0, 1)) if 'G-PK' in df_jog.columns else df_jog['Gols_90']
    df_jog['GPA_90'] = df_jog['Gols_90'] + df_jog['Ast_90']
    df_jog['Cartoes_Y_90'] = df_jog['CrdY'] / df_jog['90s'].replace(0, 1)
    df_jog['Cartoes_R_90'] = df_jog['CrdR'] / df_jog['90s'].replace(0, 1)
    df_jog['Cartoes_Total_90'] = df_jog['Cartoes_Y_90'] + df_jog['Cartoes_R_90']
    df_jog['Starts_Pct'] = (df_jog['Starts'] / df_jog['MP'].replace(0, 1)).clip(0, 1)
    
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
    
    for col in ['Gols_Sofridos_Equipe_Total', 'Jogos_Totais_Equipe', 'Posicao_Tabela_Equipe', 'Vitorias_Time', 'Empates_Time', 'Derrotas_Time', 'Pontos_Time']:
        df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(0)
        
    df_final['Aproveitamento_Equipe_Pct'] = (df_final['Pontos_Time'] / (df_final['Jogos_Totais_Equipe'].replace(0, 38) * 3) * 100).clip(0, 100)
    df_final['Minutagem_Real_Pct'] = (df_final['Min'] / (df_final['Jogos_Totais_Equipe'].replace(0, 38) * 90) * 100).clip(0, 100)
    df_final['Titularidade_Relativa'] = (df_final['Starts'] / df_final['Jogos_Totais_Equipe'].replace(0, 38)).clip(0, 1)
    df_final['Media_GA_Time'] = df_final['Gols_Sofridos_Equipe_Total'] / df_final['Jogos_Totais_Equipe'].replace(0, 1)
    
    df_final['target_divisao'] = df_final['Divisao'].map({'Série A': 1, 'Série B': 0}).fillna(0).astype(int)
    df_final['target_aptidao'] = ((df_final['target_divisao'] == 1) & 
                                  (df_final['Starts_Pct'] >= 0.45) & 
                                  (df_final['Minutagem_Real_Pct'] >= 25)).astype(int)
    
    return df_final

def treinar_modelos_posicionais():
    df = carregar_e_preparar_dados()
    
    features_pos = {
        'Atacante': ['Age', 'Gols_90', 'GPK_90', 'Ast_90', 'GPA_90', 'Starts_Pct', 'Minutagem_Real_Pct', 'Titularidade_Relativa', 'Aproveitamento_Equipe_Pct'],
        'Meio Campo': ['Age', 'Ast_90', 'GPA_90', 'Gols_90', 'Starts_Pct', 'Minutagem_Real_Pct', 'Titularidade_Relativa', 'Cartoes_Total_90', 'Aproveitamento_Equipe_Pct'],
        'Defensor': ['Age', 'Starts_Pct', 'Minutagem_Real_Pct', 'Titularidade_Relativa', 'Cartoes_Y_90', 'Cartoes_R_90', 'Cartoes_Total_90', 'Media_GA_Time', 'Aproveitamento_Equipe_Pct'],
        'Goleiro': ['Age', 'Starts_Pct', 'Minutagem_Real_Pct', 'Titularidade_Relativa', 'Media_GA_Time', 'Aproveitamento_Equipe_Pct']
    }
    
    pos_file_map = {'Atacante': 'fw', 'Meio Campo': 'mf', 'Defensor': 'df', 'Goleiro': 'gk'}
    os.makedirs('app/assets', exist_ok=True)
    metricas_pos = {}
    
    print("=" * 75)
    print("MÉTRICAS COMPLETAS DO SAD: ACURÁCIA, PRECISÃO, RECALL, F1-PONDERADO E ROC-AUC")
    print("=" * 75)
    
    for pos, feats in features_pos.items():
        df_pos = df[df['Posicao_Grupo'] == pos].copy()
        
        df_train = df_pos[df_pos['Ano'] <= 2020].copy()
        df_test = df_pos[df_pos['Ano'] >= 2021].copy()
        
        X_train = df_train[feats].fillna(0)
        y_train = df_train['target_aptidao']
        X_test = df_test[feats].fillna(0)
        y_test = df_test['target_aptidao']
        
        pipe_gb = Pipeline([
            ('scaler', StandardScaler()),
            ('model', GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42))
        ])
        pipe_gb.fit(X_train, y_train)
        pred_gb = pipe_gb.predict(X_test)
        prob_gb = pipe_gb.predict_proba(X_test)[:, 1]
        
        acc = accuracy_score(y_test, pred_gb)
        prec = precision_score(y_test, pred_gb, zero_division=0)
        rec = recall_score(y_test, pred_gb, zero_division=0)
        f1_pos = f1_score(y_test, pred_gb, zero_division=0)
        f1_w = f1_score(y_test, pred_gb, average='weighted', zero_division=0)
        auc = roc_auc_score(y_test, prob_gb)
        cm = confusion_matrix(y_test, pred_gb)
        
        print(f"\n---> POSIÇÃO: {pos.upper()} (Treino: {len(X_train)} | Teste: {len(X_test)})")
        print(f" Acurácia:      {acc*100:5.2f}%")
        print(f" Precisão:      {prec*100:5.2f}% (Acerto na indicação de Elite)")
        print(f" Recall:        {rec*100:5.2f}% (Sensibilidade de captura de Elite)")
        print(f" F1 Ponderado:  {f1_w:5.4f} (Visão Global de Desempenho)")
        print(f" ROC-AUC:       {auc:5.4f}")
        
        prefix = pos_file_map[pos]
        with open(f'app/assets/modelo_{prefix}.pkl', 'wb') as f:
            pickle.dump(pipe_gb, f)
            
        metricas_pos[pos] = {
            'features': feats,
            'best_model': 'Gradient Boosting (StandardScaler)',
            'accuracy': acc,
            'precision': prec,
            'recall': rec,
            'f1_score': f1_pos,
            'f1_weighted': f1_w,
            'roc_auc': auc,
            'confusion_matrix': cm.tolist()
        }
        
    with open('app/assets/metricas_posicionais.pkl', 'wb') as f:
        pickle.dump(metricas_pos, f)
        
    print("\n" + "=" * 75)
    print("Modelos e dicionário de métricas completas salvos em app/assets/!")

if __name__ == '__main__':
    treinar_modelos_posicionais()
