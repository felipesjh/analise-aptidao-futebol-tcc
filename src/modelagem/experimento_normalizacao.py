import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

def carregar_e_preparar_dados():
    path_jog = 'data/processed_tcc/jogadores_consolidado.csv'
    path_camp = 'data/processed_tcc/campeonato_consolidado.csv'
    
    if not os.path.exists(path_jog) or not os.path.exists(path_camp):
        raise FileNotFoundError("Bases consolidadas não encontradas em data/processed_tcc/")
        
    df_jog = pd.read_csv(path_jog)
    df_camp = pd.read_csv(path_camp)
    
    df_jog['Posicao_Original'] = df_jog['Pos']
    df_jog = df_jog.rename(columns={'Player': 'Nome', 'Squad': 'Time', 'Pos': 'Posicao'})
    
    mapa_pos = {'FW': 'Atacante', 'MF': 'Meio Campo', 'DF': 'Defensor', 'GK': 'Goleiro'}
    df_jog['Posicao_Grupo'] = df_jog['Posicao'].astype(str).str.split(',').str[0].map(mapa_pos).fillna('Outros')
    
    cols_num = ['Gls', 'Ast', 'Min', '90s', 'Age', 'MP', 'CrdY', 'CrdR', 'Starts', 'G-PK']
    for col in cols_num:
        if col in df_jog.columns:
            df_jog[col] = pd.to_numeric(df_jog[col], errors='coerce').fillna(0)
            
    # Filtro de 300 minutos
    df_jog = df_jog[df_jog['Min'] >= 300].copy()
    
    # Métricas /90
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

def executar_experimentos():
    df = carregar_e_preparar_dados()
    
    # 1. EXPERIMENTO GENÉRICO (COM TODAS AS POSIÇÕES)
    df_dummies = pd.get_dummies(df['Posicao_Grupo'], prefix='Pos', dtype=float)
    df_gen = pd.concat([df, df_dummies], axis=1)
    for pos_col in ['Pos_Atacante', 'Pos_Meio Campo', 'Pos_Defensor', 'Pos_Goleiro']:
        if pos_col not in df_gen.columns:
            df_gen[pos_col] = 0.0
            
    feats_gen = ['Age', 'Gols_90', 'Ast_90', 'Cartoes_Y_90', 'Cartoes_R_90', 'Starts_Pct',
                 'Pos_Atacante', 'Pos_Meio Campo', 'Pos_Defensor', 'Pos_Goleiro']
                 
    train_gen = df_gen[df_gen['Ano'] <= 2020]
    test_gen = df_gen[df_gen['Ano'] >= 2021]
    
    X_tr_gen = train_gen[feats_gen].fillna(0)
    y_tr_gen = train_gen['target_divisao']
    X_te_gen = test_gen[feats_gen].fillna(0)
    y_te_gen = test_gen['target_divisao']
    
    # Regressão Logística SEM normalização (Genérica)
    lr_raw = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
    lr_raw.fit(X_tr_gen, y_tr_gen)
    pred_lr_raw = lr_raw.predict(X_te_gen)
    acc_lr_raw = accuracy_score(y_te_gen, pred_lr_raw)
    f1_lr_raw = f1_score(y_te_gen, pred_lr_raw, average='weighted', zero_division=0)
    prec_lr_raw = precision_score(y_te_gen, pred_lr_raw, zero_division=0)
    rec_lr_raw = recall_score(y_te_gen, pred_lr_raw, zero_division=0)
    cm_lr_raw = confusion_matrix(y_te_gen, pred_lr_raw)
    
    # Regressão Logística COM normalização (Genérica)
    lr_scaled = Pipeline([('scaler', StandardScaler()), ('lr', LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42))])
    lr_scaled.fit(X_tr_gen, y_tr_gen)
    pred_lr_scaled = lr_scaled.predict(X_te_gen)
    acc_lr_scaled = accuracy_score(y_te_gen, pred_lr_scaled)
    f1_lr_scaled = f1_score(y_te_gen, pred_lr_scaled, average='weighted', zero_division=0)
    prec_lr_scaled = precision_score(y_te_gen, pred_lr_scaled, zero_division=0)
    rec_lr_scaled = recall_score(y_te_gen, pred_lr_scaled, zero_division=0)
    cm_lr_scaled = confusion_matrix(y_te_gen, pred_lr_scaled)

    # Random Forest COM normalização (Genérico)
    rf_gen = Pipeline([('scaler', StandardScaler()), ('rf', RandomForestClassifier(n_estimators=150, max_depth=12, class_weight='balanced', random_state=42))])
    rf_gen.fit(X_tr_gen, y_tr_gen)
    pred_rf_gen = rf_gen.predict(X_te_gen)
    acc_rf_gen = accuracy_score(y_te_gen, pred_rf_gen)
    f1_rf_gen = f1_score(y_te_gen, pred_rf_gen, average='weighted', zero_division=0)
    prec_rf_gen = precision_score(y_te_gen, pred_rf_gen, zero_division=0)
    rec_rf_gen = recall_score(y_te_gen, pred_rf_gen, zero_division=0)
    cm_rf_gen = confusion_matrix(y_te_gen, pred_rf_gen)

    print("=== MODELO GENÉRICO ===")
    print(f"LR Sem Normalização -> Acurácia: {acc_lr_raw*100:.2f}%, F1: {f1_lr_raw:.4f}, Prec: {prec_lr_raw*100:.2f}%, Rec: {rec_lr_raw*100:.2f}%")
    print("CM LR Sem Normalização:\n", cm_lr_raw)
    print(f"LR Com Normalização -> Acurácia: {acc_lr_scaled*100:.2f}%, F1: {f1_lr_scaled:.4f}, Prec: {prec_lr_scaled*100:.2f}%, Rec: {rec_lr_scaled*100:.2f}%")
    print("CM LR Com Normalização:\n", cm_lr_scaled)
    print(f"RF Com Normalização -> Acurácia: {acc_rf_gen*100:.2f}%, F1: {f1_rf_gen:.4f}, Prec: {prec_rf_gen*100:.2f}%, Rec: {rec_rf_gen*100:.2f}%")
    print("CM RF Com Normalização:\n", cm_rf_gen)
    
    # 2. EXPERIMENTOS POSICIONAIS (SEM VS COM NORMALIZAÇÃO)
    features_pos = {
        'Atacante': ['Age', 'Gols_90', 'GPK_90', 'Ast_90', 'GPA_90', 'Starts_Pct', 'Minutagem_Real_Pct', 'Titularidade_Relativa', 'Aproveitamento_Equipe_Pct'],
        'Meio Campo': ['Age', 'Ast_90', 'GPA_90', 'Gols_90', 'Starts_Pct', 'Minutagem_Real_Pct', 'Titularidade_Relativa', 'Cartoes_Total_90', 'Aproveitamento_Equipe_Pct'],
        'Defensor': ['Age', 'Starts_Pct', 'Minutagem_Real_Pct', 'Titularidade_Relativa', 'Cartoes_Y_90', 'Cartoes_R_90', 'Cartoes_Total_90', 'Media_GA_Time', 'Aproveitamento_Equipe_Pct'],
        'Goleiro': ['Age', 'Starts_Pct', 'Minutagem_Real_Pct', 'Titularidade_Relativa', 'Media_GA_Time', 'Aproveitamento_Equipe_Pct']
    }
    
    res_pos = {}
    
    for pos, feats in features_pos.items():
        df_pos = df[df['Posicao_Grupo'] == pos].copy()
        df_tr = df_pos[df_pos['Ano'] <= 2020]
        df_te = df_pos[df_pos['Ano'] >= 2021]
        
        X_tr = df_tr[feats].fillna(0)
        y_tr = df_tr['target_aptidao']
        X_te = df_te[feats].fillna(0)
        y_te = df_te['target_aptidao']
        
        # Posicional Sem Normalização (Regressão Logística)
        lr_pos_raw = LogisticRegression(max_iter=1000, random_state=42)
        lr_pos_raw.fit(X_tr, y_tr)
        pred_lr_pos_raw = lr_pos_raw.predict(X_te)
        acc_pos_raw = accuracy_score(y_te, pred_lr_pos_raw)
        f1_pos_raw = f1_score(y_te, pred_lr_pos_raw, average='weighted', zero_division=0)
        cm_pos_raw = confusion_matrix(y_te, pred_lr_pos_raw)
        
        # Posicional Com Normalização (Gradient Boosting + StandardScaler)
        pipe_pos_norm = Pipeline([
            ('scaler', StandardScaler()),
            ('gb', GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42))
        ])
        pipe_pos_norm.fit(X_tr, y_tr)
        pred_pos_norm = pipe_pos_norm.predict(X_te)
        prob_pos_norm = pipe_pos_norm.predict_proba(X_te)[:, 1]
        
        acc_pos_norm = accuracy_score(y_te, pred_pos_norm)
        prec_pos_norm = precision_score(y_te, pred_pos_norm, zero_division=0)
        rec_pos_norm = recall_score(y_te, pred_pos_norm, zero_division=0)
        f1_pos_norm = f1_score(y_te, pred_pos_norm, average='weighted', zero_division=0)
        auc_pos_norm = roc_auc_score(y_te, prob_pos_norm)
        cm_pos_norm = confusion_matrix(y_te, pred_pos_norm)
        
        res_pos[pos] = {
            'raw': {'acc': acc_pos_raw, 'f1_weighted': f1_pos_raw, 'cm': cm_pos_raw.tolist()},
            'norm': {
                'acc': acc_pos_norm, 'prec': prec_pos_norm, 'rec': rec_pos_norm,
                'f1_weighted': f1_pos_norm, 'roc_auc': auc_pos_norm, 'cm': cm_pos_norm.tolist()
            }
        }
        
        print(f"\n=== POSIÇÃO: {pos} ===")
        print(f"Sem Normalização (LR) -> Acurácia: {acc_pos_raw*100:.2f}%, F1-W: {f1_pos_raw:.4f}")
        print("CM Raw:\n", cm_pos_raw)
        print(f"Com Normalização (GB) -> Acurácia: {acc_pos_norm*100:.2f}%, F1-W: {f1_pos_norm:.4f}, Prec: {prec_pos_norm*100:.2f}%, Rec: {rec_pos_norm*100:.2f}%, AUC: {auc_pos_norm:.4f}")
        print("CM Norm:\n", cm_pos_norm)
        
    # Salvar para uso no Streamlit e na documentação
    os.makedirs('app/assets', exist_ok=True)
    comp_metrics = {
        'generic': {
            'lr_raw': {'acc': acc_lr_raw, 'f1_w': f1_lr_raw, 'prec': prec_lr_raw, 'rec': rec_lr_raw, 'cm': cm_lr_raw.tolist()},
            'lr_scaled': {'acc': acc_lr_scaled, 'f1_w': f1_lr_scaled, 'prec': prec_lr_scaled, 'rec': rec_lr_scaled, 'cm': cm_lr_scaled.tolist()},
            'rf_scaled': {'acc': acc_rf_gen, 'f1_w': f1_rf_gen, 'prec': prec_rf_gen, 'rec': rec_rf_gen, 'cm': cm_rf_gen.tolist()}
        },
        'positional': res_pos
    }
    
    with open('app/assets/experimentos_comparativos.pkl', 'wb') as f:
        pickle.dump(comp_metrics, f)
        
    print("\nExperimentos concluídos e salvos em app/assets/experimentos_comparativos.pkl")

if __name__ == '__main__':
    executar_experimentos()
