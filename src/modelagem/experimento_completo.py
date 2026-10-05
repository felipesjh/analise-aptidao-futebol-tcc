import csv
import math
import pickle
import json
import os

def load_data():
    jog_path = 'data/processed_tcc/jogadores_consolidado.csv'
    camp_path = 'data/processed_tcc/campeonato_consolidado.csv'
    
    with open(jog_path, 'r', encoding='utf-8') as f:
        jogadores = list(csv.DictReader(f))
        
    with open(camp_path, 'r', encoding='utf-8') as f:
        campeonatos = list(csv.DictReader(f))
        
    camp_map = {}
    for c in campeonatos:
        key = (c['Squad'], c['Ano'], c['Divisao'])
        camp_map[key] = c
        
    processed = []
    for j in jogadores:
        try:
            minutos = float(j.get('Min', 0))
        except:
            minutos = 0.0
            
        if minutos < 300:
            continue
            
        try:
            n90s = float(j.get('90s', 0))
            if n90s <= 0: n90s = minutos / 90.0
        except:
            n90s = minutos / 90.0
        if n90s <= 0: n90s = 1.0
        
        try: gls = float(j.get('Gls', 0))
        except: gls = 0.0
        try: ast = float(j.get('Ast', 0))
        except: ast = 0.0
        try: age = float(j.get('Age', 25))
        except: age = 25.0
        try: mp = float(j.get('MP', 1))
        except: mp = 1.0
        try: starts = float(j.get('Starts', 0))
        except: starts = 0.0
        try: crdy = float(j.get('CrdY', 0))
        except: crdy = 0.0
        try: crdr = float(j.get('CrdR', 0))
        except: crdr = 0.0
        try: gpk = float(j.get('G-PK', gls))
        except: gpk = gls
        
        pos_raw = j.get('Pos', '').split(',')[0]
        pos_map = {'FW': 'Atacante', 'MF': 'Meio Campo', 'DF': 'Defensor', 'GK': 'Goleiro'}
        pos_grupo = pos_map.get(pos_raw, 'Outros')
        
        ano = j.get('Ano', '2020')
        divisao = j.get('Divisao', 'Série B')
        time = j.get('Squad', '')
        
        # Merge camp
        c_info = camp_map.get((time, ano, divisao), {})
        try: ga_team = float(c_info.get('GA', 0))
        except: ga_team = 0.0
        try: mp_team = float(c_info.get('MP', 38))
        except: mp_team = 38.0
        if mp_team <= 0: mp_team = 38.0
        try: pts_team = float(c_info.get('Pts', 45))
        except: pts_team = 45.0
        
        gols_90 = gls / n90s
        ast_90 = ast / n90s
        gpk_90 = gpk / n90s
        gpa_90 = gols_90 + ast_90
        crdy_90 = crdy / n90s
        crdr_90 = crdr / n90s
        crd_tot_90 = crdy_90 + crdr_90
        starts_pct = min(1.0, max(0.0, starts / max(1.0, mp)))
        minutagem_real_pct = min(1.0, max(0.0, minutos / (mp_team * 90.0))) * 100.0
        titularidade_rel = min(1.0, max(0.0, starts / mp_team))
        aprov_team_pct = min(100.0, max(0.0, (pts_team / (mp_team * 3.0)) * 100.0))
        media_ga_time = ga_team / mp_team
        
        target_div = 1 if divisao == 'Série A' else 0
        target_apt = 1 if (target_div == 1 and starts_pct >= 0.45 and minutagem_real_pct >= 25.0) else 0
        
        processed.append({
            'Nome': j.get('Player', ''),
            'Time': time,
            'Ano': int(ano) if ano.isdigit() else 2020,
            'Divisao': divisao,
            'Posicao_Grupo': pos_grupo,
            'Age': age,
            'Min': minutos,
            'Gols_90': gols_90,
            'Ast_90': ast_90,
            'GPK_90': gpk_90,
            'GPA_90': gpa_90,
            'Cartoes_Y_90': crdy_90,
            'Cartoes_R_90': crdr_90,
            'Cartoes_Total_90': crd_tot_90,
            'Starts_Pct': starts_pct,
            'Minutagem_Real_Pct': minutagem_real_pct,
            'Titularidade_Relativa': titularidade_rel,
            'Aproveitamento_Equipe_Pct': aprov_team_pct,
            'Media_GA_Time': media_ga_time,
            'target_divisao': target_div,
            'target_aptidao': target_apt
        })
        
    return processed

def fit_logistic_regression(X_train, y_train, scale=False, max_iter=300, lr=0.01):
    # Calculate means and stds if scale=True
    num_samples = len(X_train)
    num_features = len(X_train[0])
    
    means = [0.0] * num_features
    stds = [1.0] * num_features
    
    if scale:
        for j in range(num_features):
            col_vals = [X_train[i][j] for i in range(num_samples)]
            m = sum(col_vals) / num_samples
            var = sum((x - m) ** 2 for x in col_vals) / max(1, num_samples - 1)
            s = math.sqrt(var) if var > 1e-8 else 1.0
            means[j] = m
            stds[j] = s
            
    # Standardize X_train
    X_scaled = []
    for i in range(num_samples):
        row = []
        for j in range(num_features):
            val = (X_train[i][j] - means[j]) / stds[j] if scale else X_train[i][j]
            row.append(val)
        X_scaled.append(row)
        
    # Weights initialization
    weights = [0.0] * num_features
    bias = 0.0
    
    for _ in range(max_iter):
        dw = [0.0] * num_features
        db = 0.0
        for i in range(num_samples):
            z = sum(weights[j] * X_scaled[i][j] for j in range(num_features)) + bias
            z = max(-20.0, min(20.0, z))
            p = 1.0 / (1.0 + math.exp(-z))
            err = p - y_train[i]
            for j in range(num_features):
                dw[j] += err * X_scaled[i][j]
            db += err
        for j in range(num_features):
            weights[j] -= lr * (dw[j] / num_samples)
        bias -= lr * (db / num_samples)
        
    return weights, bias, means, stds

def predict_logistic_regression(X_test, weights, bias, means, stds, scale=False):
    preds = []
    probs = []
    for i in range(len(X_test)):
        z = bias
        for j in range(len(weights)):
            val = (X_test[i][j] - means[j]) / stds[j] if scale else X_test[i][j]
            z += weights[j] * val
        z = max(-20.0, min(20.0, z))
        p = 1.0 / (1.0 + math.exp(-z))
        probs.append(p)
        preds.append(1 if p >= 0.5 else 0)
    return preds, probs

def calc_metrics(y_true, y_pred, y_prob=None):
    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1)
    tn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 0)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0)
    
    acc = (tp + tn) / max(1, len(y_true))
    prec = tp / max(1, tp + fp)
    rec = tp / max(1, tp + fn)
    f1_pos = (2 * prec * rec) / max(1e-8, prec + rec) if (prec + rec) > 0 else 0.0
    
    # Weighted F1
    n0 = sum(1 for yt in y_true if yt == 0)
    n1 = sum(1 for yt in y_true if yt == 1)
    prec0 = tn / max(1, tn + fn)
    rec0 = tn / max(1, tn + fp)
    f1_0 = (2 * prec0 * rec0) / max(1e-8, prec0 + rec0) if (prec0 + rec0) > 0 else 0.0
    f1_w = (n0 * f1_0 + n1 * f1_pos) / max(1, len(y_true))
    
    # ROC-AUC approximation if probs available
    auc = 0.5
    if y_prob:
        pos_scores = [s for yt, s in zip(y_true, y_prob) if yt == 1]
        neg_scores = [s for yt, s in zip(y_true, y_prob) if yt == 0]
        if pos_scores and neg_scores:
            greater = 0
            for ps in pos_scores:
                for ns in neg_scores:
                    if ps > ns: greater += 1
                    elif ps == ns: greater += 0.5
            auc = greater / (len(pos_scores) * len(neg_scores))
            
    return {
        'acc': acc,
        'prec': prec,
        'rec': rec,
        'f1': f1_pos,
        'f1_w': f1_w,
        'auc': auc,
        'cm': [[tn, fp], [fn, tp]]
    }

def main():
    data = load_data()
    train_data = [d for d in data if d['Ano'] <= 2020]
    test_data = [d for d in data if d['Ano'] >= 2021]
    
    print(f"Total Processado -> Treino (<=2020): {len(train_data)} | Teste (>=2021): {len(test_data)}")
    
    # 1. MODELO GENÉRICO (SEM NORMALIZAÇÃO vs COM NORMALIZAÇÃO)
    gen_feats = ['Age', 'Min', 'Gols_90', 'Ast_90', 'Cartoes_Y_90', 'Cartoes_R_90', 'Starts_Pct']
    X_train_gen = [[d[f] for f in gen_feats] for d in train_data]
    y_train_gen = [d['target_divisao'] for d in train_data]
    
    X_test_gen = [[d[f] for f in gen_feats] for d in test_data]
    y_test_gen = [d['target_divisao'] for d in test_data]
    
    # Sem normalização
    w_un, b_un, m_un, s_un = fit_logistic_regression(X_train_gen, y_train_gen, scale=False, max_iter=200)
    pred_un, prob_un = predict_logistic_regression(X_test_gen, w_un, b_un, m_un, s_un, scale=False)
    m_un_res = calc_metrics(y_test_gen, pred_un, prob_un)
    
    # Com normalização
    w_sc, b_sc, m_sc, s_sc = fit_logistic_regression(X_train_gen, y_train_gen, scale=True, max_iter=500, lr=0.05)
    pred_sc, prob_sc = predict_logistic_regression(X_test_gen, w_sc, b_sc, m_sc, s_sc, scale=True)
    m_sc_res = calc_metrics(y_test_gen, pred_sc, prob_sc)
    
    print("\n--- MODELO GENÉRICO (TODAS AS POSIÇÕES) ---")
    print(f"1) Sem Normalização -> Acurácia: {m_un_res['acc']*100:.2f}%, F1-W: {m_un_res['f1_w']:.4f}, Prec: {m_un_res['prec']*100:.2f}%, Rec: {m_un_res['rec']*100:.2f}%, AUC: {m_un_res['auc']:.4f}")
    print("   Matriz de Confusão [TN, FP / FN, TP]:", m_un_res['cm'])
    print(f"2) Com Normalização -> Acurácia: {m_sc_res['acc']*100:.2f}%, F1-W: {m_sc_res['f1_w']:.4f}, Prec: {m_sc_res['prec']*100:.2f}%, Rec: {m_sc_res['rec']*100:.2f}%, AUC: {m_sc_res['auc']:.4f}")
    print("   Matriz de Confusão [TN, FP / FN, TP]:", m_sc_res['cm'])

    # 2. MODELOS POR POSIÇÃO (ESPECIALIZADOS)
    pos_feats = {
        'Atacante': ['Age', 'Gols_90', 'GPK_90', 'Ast_90', 'GPA_90', 'Starts_Pct', 'Minutagem_Real_Pct', 'Aproveitamento_Equipe_Pct'],
        'Goleiro': ['Age', 'Starts_Pct', 'Minutagem_Real_Pct', 'Titularidade_Relativa', 'Media_GA_Time', 'Aproveitamento_Equipe_Pct'],
        'Defensor': ['Age', 'Starts_Pct', 'Minutagem_Real_Pct', 'Cartoes_Y_90', 'Cartoes_R_90', 'Media_GA_Time', 'Aproveitamento_Equipe_Pct'],
        'Meio Campo': ['Age', 'Ast_90', 'GPA_90', 'Gols_90', 'Starts_Pct', 'Minutagem_Real_Pct', 'Cartoes_Total_90', 'Aproveitamento_Equipe_Pct']
    }
    
    pos_results = {}
    for pos, feats in pos_feats.items():
        tr_pos = [d for d in train_data if d['Posicao_Grupo'] == pos]
        te_pos = [d for d in test_data if d['Posicao_Grupo'] == pos]
        
        X_tr = [[d[f] for f in feats] for d in tr_pos]
        y_tr = [d['target_aptidao'] for d in tr_pos]
        
        X_te = [[d[f] for f in feats] for d in te_pos]
        y_te = [d['target_aptidao'] for d in te_pos]
        
        # Raw (sem normalizar)
        w_raw, b_raw, m_raw, s_raw = fit_logistic_regression(X_tr, y_tr, scale=False, max_iter=200)
        p_raw, pr_raw = predict_logistic_regression(X_te, w_raw, b_raw, m_raw, s_raw, scale=False)
        m_pos_raw = calc_metrics(y_te, p_raw, pr_raw)
        
        # Scaled (com normalizar)
        w_norm, b_norm, m_norm, s_norm = fit_logistic_regression(X_tr, y_tr, scale=True, max_iter=500, lr=0.05)
        p_norm, pr_norm = predict_logistic_regression(X_te, w_norm, b_norm, m_norm, s_norm, scale=True)
        m_pos_norm = calc_metrics(y_te, p_norm, pr_norm)
        
        pos_results[pos] = {
            'n_train': len(tr_pos), 'n_test': len(te_pos),
            'raw': m_pos_raw, 'norm': m_pos_norm
        }
        
        print(f"\n--- POSIÇÃO: {pos.upper()} (Treino: {len(tr_pos)} | Teste: {len(te_pos)}) ---")
        print(f"  SEM Normalização -> Acc: {m_pos_raw['acc']*100:.2f}%, F1-W: {m_pos_raw['f1_w']:.4f}, Prec: {m_pos_raw['prec']*100:.2f}%, Rec: {m_pos_raw['rec']*100:.2f}%, AUC: {m_pos_raw['auc']:.4f}")
        print("  CM Raw:", m_pos_raw['cm'])
        print(f"  COM Normalização -> Acc: {m_pos_norm['acc']*100:.2f}%, F1-W: {m_pos_norm['f1_w']:.4f}, Prec: {m_pos_norm['prec']*100:.2f}%, Rec: {m_pos_norm['rec']*100:.2f}%, AUC: {m_pos_norm['auc']:.4f}")
        print("  CM Norm:", m_pos_norm['cm'])

    # Salvar em JSON para inclusão no PDF e na documentação
    export_dict = {
        'generic_raw': m_un_res,
        'generic_scaled': m_sc_res,
        'positional': pos_results
    }
    with open('app/assets/resultados_experimentais_oficiais.json', 'w', encoding='utf-8') as f:
        json.dump(export_dict, f, indent=2)
    print("\nResultados oficiais gravados em app/assets/resultados_experimentais_oficiais.json!")

if __name__ == '__main__':
    main()
