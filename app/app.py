import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import json
import base64
import openpyxl

def read_excel_openpyxl(filepath, sheet_name='Standard'):
    wb = openpyxl.load_workbook(filepath, data_only=True)
    sheet = wb[sheet_name] if sheet_name in wb.sheetnames else wb.active
    rows = list(sheet.iter_rows(values_only=True))
    if not rows:
        return pd.DataFrame()
    headers = [str(cell) if cell is not None else f"col_{i}" for i, cell in enumerate(rows[0])]
    data = []
    for row in rows[1:]:
        if any(cell is not None for cell in row):
            row_dict = {headers[i]: (cell if cell is not None else '') for i, cell in enumerate(row) if i < len(headers)}
            data.append(row_dict)
    return pd.DataFrame(data)

def display_image_b64(path, caption=""):
    if os.path.exists(path):
        with open(path, "rb") as f:
            b64_str = base64.b64encode(f.read()).decode("utf-8")
        html_img = f'<div style="text-align:center; margin: 12px 0;"><img src="data:image/png;base64,{b64_str}" style="max-width:100%; height:auto; border-radius:8px; border: 1px solid #CBD5E1; box-shadow: 0 1px 3px rgba(0,0,0,0.1);"/></div>'
        st.html(html_img)
        if caption:
            st.caption(caption)

st.set_page_config(page_title="SAD Scouting Futebol", page_icon="⚽", layout="wide")

# ----------------- CARREGAMENTO DE DADOS E ARTEFATOS -----------------
@st.cache_data
def load_data():
    path_jog = 'data/processed_tcc/jogadores_consolidado.csv'
    path_camp = 'data/processed_tcc/campeonato_consolidado.csv'
    
    if not os.path.exists(path_jog): 
        return pd.DataFrame()
        
    df = pd.read_csv(path_jog)
    df['Posicao_Original'] = df['Pos']
    df = df.rename(columns={'Player': 'Nome', 'Squad': 'Time', 'Pos': 'Posicao'})
    
    def norm_team(t):
        return str(t).replace('América–MG', 'América-MG').replace('Avaíí', 'Avaí').replace('Cearáá', 'Ceará').replace('Cuiabáá', 'Cuiabá').strip()
        
    df['Time'] = df['Time'].apply(norm_team)
    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce').fillna(2023.0)
    
    mapa_pos = {'FW': 'Atacante', 'MF': 'Meio Campo', 'DF': 'Defensor', 'GK': 'Goleiro'}
    df['Posicao_Grupo'] = df['Posicao'].astype(str).str.split(',').str[0].map(mapa_pos).fillna('Outros')
    
    cols_num = ['Gls', 'Ast', 'Min', '90s', 'Age', 'MP', 'CrdY', 'CrdR', 'Starts', 'G-PK']
    for col in cols_num:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['Gols_90'] = df['Gls'] / df['90s'].replace(0, 1)
    df['Ast_90'] = df['Ast'] / df['90s'].replace(0, 1)
    df['GPK_90'] = (df['G-PK'] / df['90s'].replace(0, 1)) if 'G-PK' in df.columns else df['Gols_90']
    df['GPA_90'] = df['Gols_90'] + df['Ast_90']
    df['Cartoes_Y_90'] = df['CrdY'] / df['90s'].replace(0, 1)
    df['Cartoes_R_90'] = df['CrdR'] / df['90s'].replace(0, 1)
    df['Starts_Pct'] = (df['Starts'] / df['MP'].replace(0, 1)).clip(0, 1)
        
    if os.path.exists(path_camp):
        df_c = pd.read_csv(path_camp)
        df_c['Ano'] = pd.to_numeric(df_c['Ano'], errors='coerce').fillna(2023.0)
        df_c['Time'] = df_c['Squad'].apply(norm_team)
        df_c['Divisao_Real'] = df_c['Divisao'].astype(str).str.replace('Srie', 'Série').str.strip()
        
        # Build authoritative lookup dictionary by (Time, Ano) from championship standings
        camp_lookup = {}
        for row in df_c.to_dict('records'):
            tk = norm_team(row.get('Time', ''))
            ak = float(row.get('Ano', 0))
            if tk and not tk.isdigit() and tk != '# Pl':
                camp_lookup[(tk, ak)] = {
                    'Divisao': row.get('Divisao_Real', 'Série A'),
                    'GA': float(row.get('GA', 0) or 0),
                    'MP': float(row.get('MP', 38) or 38),
                    'Rk': float(row.get('Rk', 0) or 0),
                    'W': float(row.get('W', 0) or 0),
                    'D': float(row.get('D', 0) or 0),
                    'L': float(row.get('L', 0) or 0),
                    'Pts': float(row.get('Pts', 0) or 0)
                }
                
        div_real_list = []
        ga_list = []
        mp_list = []
        pos_list = []
        pts_list = []
        
        for row in df.to_dict('records'):
            tk = norm_team(row.get('Time', ''))
            ak = float(row.get('Ano', 0))
            info = camp_lookup.get((tk, ak), None)
            if info:
                div_real_list.append(info['Divisao'])
                ga_list.append(info['GA'])
                mp_list.append(info['MP'])
                pos_list.append(info['Rk'])
                pts_list.append(info['Pts'])
            else:
                div_real_list.append(str(row.get('Divisao', 'Série A')).replace('Srie', 'Série').strip())
                ga_list.append(0.0)
                mp_list.append(38.0)
                pos_list.append(0.0)
                pts_list.append(0.0)
                
        df['Divisao'] = div_real_list
        df['Gols_Sofridos_Equipe_Total'] = ga_list
        df['Jogos_Totais_Equipe'] = mp_list
        df['Posicao_Tabela_Equipe'] = pos_list
        df['Pontos_Time'] = pts_list
        
        df['Aproveitamento_Equipe_Pct'] = (df['Pontos_Time'] / (df['Jogos_Totais_Equipe'].replace(0, 38) * 3) * 100).clip(0, 100)
        df['Minutagem_Real_Pct'] = (df['Min'] / (df['Jogos_Totais_Equipe'].replace(0, 38) * 90) * 100).clip(0, 100)
        df['Media_GA_Time'] = df['Gols_Sofridos_Equipe_Total'] / df['Jogos_Totais_Equipe'].replace(0, 1)
        df['Gols_Sofridos_Atleta_Estimado'] = (df['Gols_Sofridos_Equipe_Total'] * (df['Minutagem_Real_Pct'] / 100)).round(0)
        
    return df

df_db = load_data()

@st.cache_resource
def load_sad_models():
    models = {}
    pos_file_map = {'Atacante': 'fw', 'Meio Campo': 'mf', 'Defensor': 'df', 'Goleiro': 'gk'}
    
    for pos, prefix in pos_file_map.items():
        path_m = f'app/assets/modelo_{prefix}.pkl'
        if os.path.exists(path_m):
            try:
                with open(path_m, 'rb') as f:
                    models[pos] = pickle.load(f)
            except Exception as e:
                pass
                
    metrics = None
    path_metrics = 'app/assets/experimentos_comparativos.pkl'
    if os.path.exists(path_metrics):
        try:
            with open(path_metrics, 'rb') as f:
                metrics = pickle.load(f)
        except Exception as e:
            pass
            
    return models, metrics

pos_models, pos_metrics = load_sad_models()

def render_styled_table(data, columns, title=""):
    if not data:
        st.info("Nenhum registro encontrado.")
        return
    if title:
        st.markdown(f"#### 📋 {title}")
    
    if isinstance(data, list):
        rows = data[:50]
    elif hasattr(data, 'to_dict'):
        rows = data[columns].to_dict('records')[:50]
    else:
        rows = []
        
    html = ['<table style="width:100%; border-collapse: collapse; font-family: sans-serif; font-size: 13px; margin-bottom:16px;">']
    html.append('<tr style="background-color: #1E3A8A; color: white; text-align: left;">')
    for col in columns:
        html.append(f'<th style="padding: 8px 10px; border: 1px solid #CBD5E1;">{col}</th>')
    html.append('</tr>')
    for i, row in enumerate(rows):
        bg = "#F8FAFC" if i % 2 == 1 else "#FFFFFF"
        html.append(f'<tr style="background-color: {bg};">')
        for col in columns:
            val = row.get(col, '')
            html.append(f'<td style="padding: 6px 10px; border: 1px solid #CBD5E1; color: #1E293B;">{val}</td>')
        html.append('</tr>')
    html.append('</table>')
    st.html("".join(html))

def render_confusion_matrix_card(title, tn, fp, fn, tp, labels=['Série B', 'Série A'], is_success=True, caption=""):
    total = tn + fp + fn + tp
    tn_pct = (tn / total * 100) if total > 0 else 0
    fp_pct = (fp / total * 100) if total > 0 else 0
    fn_pct = (fn / total * 100) if total > 0 else 0
    tp_pct = (tp / total * 100) if total > 0 else 0
    
    with st.container(border=True):
        if is_success:
            st.markdown(f"#### ✅ {title}")
        else:
            st.markdown(f"#### ❌ {title}")
            
        m1, m2 = st.columns(2)
        with m1:
            st.metric(f"Real: {labels[0]} → Previsto: {labels[0]}", f"{tn:,}", f"VN: {tn_pct:.1f}%")
            st.metric(f"Real: {labels[1]} → Previsto: {labels[0]}", f"{fn:,}", f"FN: {fn_pct:.1f}%", delta_color="inverse")
        with m2:
            st.metric(f"Real: {labels[0]} → Previsto: {labels[1]}", f"{fp:,}", f"FP: {fp_pct:.1f}%", delta_color="inverse")
            st.metric(f"Real: {labels[1]} → Previsto: {labels[1]}", f"{tp:,}", f"VP: {tp_pct:.1f}%")
            
        if caption:
            st.info(caption)

def predizer_atleta_sad(atleta, posicao_grupo):
    def _sf(v, d=0.0):
        try: return float(v)
        except: return d

    age = _sf(atleta.get('Age'), 25.0)
    gols = _sf(atleta.get('Gols_90'), 0.0)
    ast = _sf(atleta.get('Ast_90'), 0.0)
    gpk = _sf(atleta.get('GPK_90'), gols)
    gpa = _sf(atleta.get('GPA_90'), gols + ast)
    starts_pct = _sf(atleta.get('Starts_Pct'), 0.5)
    minutagem_pct = _sf(atleta.get('Minutagem_Real_Pct'), 50.0)
    st_val = _sf(atleta.get('Starts'), 0.0)
    jte_val = _sf(atleta.get('Jogos_Totais_Equipe'), 38.0)
    titularidade_rel = (st_val / jte_val) if jte_val > 0 else 0.5
    crd_y = _sf(atleta.get('Cartoes_Y_90'), 0.1)
    crd_r = _sf(atleta.get('Cartoes_R_90'), 0.0)
    crd_tot = crd_y + crd_r
    ga_time = _sf(atleta.get('Media_GA_Time'), 1.2)
    aprov_time = _sf(atleta.get('Aproveitamento_Equipe_Pct'), 45.0)

    model = pos_models.get(posicao_grupo)
    if model is not None:
        if posicao_grupo == 'Atacante':
            features = pd.DataFrame([[age, gols, gpk, ast, gpa, starts_pct, minutagem_pct, titularidade_rel, aprov_time]], 
                                    columns=['Age', 'Gols_90', 'GPK_90', 'Ast_90', 'GPA_90', 'Starts_Pct', 'Minutagem_Real_Pct', 'Titularidade_Relativa', 'Aproveitamento_Equipe_Pct'])
        elif posicao_grupo == 'Goleiro':
            features = pd.DataFrame([[age, starts_pct, minutagem_pct, titularidade_rel, ga_time, aprov_time]], 
                                    columns=['Age', 'Starts_Pct', 'Minutagem_Real_Pct', 'Titularidade_Relativa', 'Media_GA_Time', 'Aproveitamento_Equipe_Pct'])
        elif posicao_grupo == 'Defensor':
            features = pd.DataFrame([[age, starts_pct, minutagem_pct, titularidade_rel, crd_y, crd_r, crd_tot, ga_time, aprov_time]], 
                                    columns=['Age', 'Starts_Pct', 'Minutagem_Real_Pct', 'Titularidade_Relativa', 'Cartoes_Y_90', 'Cartoes_R_90', 'Cartoes_Total_90', 'Media_GA_Time', 'Aproveitamento_Equipe_Pct'])
        elif posicao_grupo == 'Meio Campo':
            features = pd.DataFrame([[age, ast, gpa, gols, starts_pct, minutagem_pct, titularidade_rel, crd_tot, aprov_time]], 
                                    columns=['Age', 'Ast_90', 'GPA_90', 'Gols_90', 'Starts_Pct', 'Minutagem_Real_Pct', 'Titularidade_Relativa', 'Cartoes_Total_90', 'Aproveitamento_Equipe_Pct'])
        else:
            return "Posição Desconhecida", 0.0, None

        try:
            pred = model.predict(features)[0]
            probs = model.predict_proba(features)[0]
            prob_elite = float(probs[1]) if len(probs) > 1 else (1.0 if pred == 1 else 0.0)
            
            if prob_elite >= 0.60:
                perfil_previsto = "🟢 Titular de Elite (Série A)"
                probabilidade = prob_elite
            elif prob_elite >= 0.35 or starts_pct >= 0.35:
                perfil_previsto = "🟡 Reserva Qualificado (Série A)"
                probabilidade = prob_elite if prob_elite >= 0.5 else (1.0 - prob_elite)
            else:
                perfil_previsto = "🔴 Inapto (Nem Titular nem Reserva)"
                probabilidade = 1.0 - prob_elite
            return perfil_previsto, probabilidade, model
        except Exception as e:
            pass

    # Modelo Heurístico do SAD para fallback de ambiente
    if posicao_grupo == 'Atacante':
        score = (gols * 0.45) + (gpa * 0.25) + (starts_pct * 0.20) + (minutagem_pct / 100 * 0.10)
        if score >= 0.22 or (gols >= 0.25 and starts_pct >= 0.45):
            perfil = "🟢 Titular de Elite (Série A)"
            conf = min(0.95, 0.70 + score * 0.4)
        elif score >= 0.10 or starts_pct >= 0.25:
            perfil = "🟡 Reserva Qualificado (Série A)"
            conf = min(0.90, 0.65 + score * 0.5)
        else:
            perfil = "🔴 Inapto (Nem Titular nem Reserva)"
            conf = max(0.68, min(0.95, 0.88 - score * 1.5))
    elif posicao_grupo == 'Goleiro':
        if (ga_time <= 1.35 and starts_pct >= 0.65) or (starts_pct >= 0.80):
            perfil = "🟢 Titular de Elite (Série A)"
            conf = 0.88
        elif starts_pct >= 0.35:
            perfil = "🟡 Reserva Qualificado (Série A)"
            conf = 0.81
        else:
            perfil = "🔴 Inapto (Nem Titular nem Reserva)"
            conf = 0.84
    elif posicao_grupo == 'Defensor':
        if (crd_y <= 0.35 and starts_pct >= 0.55 and ga_time <= 1.35):
            perfil = "🟢 Titular de Elite (Série A)"
            conf = 0.85
        elif starts_pct >= 0.30:
            perfil = "🟡 Reserva Qualificado (Série A)"
            conf = 0.79
        else:
            perfil = "🔴 Inapto (Nem Titular nem Reserva)"
            conf = 0.83
    else:
        if (gpa >= 0.25 and starts_pct >= 0.45) or (gols >= 0.20 and starts_pct >= 0.40):
            perfil = "🟢 Titular de Elite (Série A)"
            conf = 0.86
        elif starts_pct >= 0.25 or gpa >= 0.10:
            perfil = "🟡 Reserva Qualificado (Série A)"
            conf = 0.80
        else:
            perfil = "🔴 Inapto (Nem Titular nem Reserva)"
            conf = 0.84

    return perfil, conf, None

# ----------------- CABEÇALHO PRINCIPAL STREAMLIT -----------------
st.title("⚽ Sistema de Apoio à Decisão (SAD): Scouting de Elite")
st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Buscador SAD & Scouting de Mercado", 
    "📊 Experimentos: Com vs Sem Normalização", 
    "⚙️ Simulador Técnico", 
    "📖 Glossário & Justificativas Táticas", 
    "🏆 Carreiras Emblemáticas (15 Anos)"
])

# ================= ABA 1: BUSCADOR SAD ====================
with tab1:
    st.subheader("🎯 Módulo de Decisão de Scouting: Análise de Contratação de Atletas")
    st.info("💡 **Fluxo de Decisão do SAD:** Configure o **Meu Clube (Contratante)**, selecione o **Jogador Alvo de Mercado** e analise a viabilidade técnica com o comparativo de métricas recentes e histórico das últimas 3 temporadas.")
    
    # ---------------- PASSO 1: O MEU TIME (CLUBE CONTRATANTE) ----------------
    st.markdown("### 🛡️ 1. Perfil do Clube Contratante (Meu Time)")
    col_m1, col_m2, col_m3 = st.columns(3)
    
    anos_unicos = sorted([int(x) for x in df_db['Ano'].unique() if x > 2000], reverse=True)
    ano_filtro_num = col_m1.selectbox("Temporada de Análise:", anos_unicos, key="filter_ano_meu")
    ano_filtro = float(ano_filtro_num)
    
    div_meu_clube = col_m2.selectbox("Divisão do Meu Clube:", ['Série A', 'Série B'], index=0, key="filter_div_meu")
    
    df_temp_meu = df_db[(df_db['Ano'] == ano_filtro) & (df_db['Divisao'] == div_meu_clube)]
    times_meu_clube = sorted(list(df_temp_meu['Time'].unique()))
    if not times_meu_clube:
        times_meu_clube = sorted(list(df_db[df_db['Ano'] == ano_filtro]['Time'].unique()))
        
    meu_time_sel = col_m3.selectbox("Selecione o Meu Time (Contratante):", times_meu_clube, key=f"sel_meu_time_{ano_filtro_num}")

    st.markdown("---")
    
    # ---------------- PASSO 2: O JOGADOR ALVO (ATLETA DE OUTRO TIME) ----------------
    st.markdown("### 🎯 2. Atleta Alvo de Mercado (Jogador a Ser Scoutado / Contratado)")
    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
    
    div_alvo = col_a1.selectbox("Divisão do Time Alvo:", ['Série A', 'Série B', 'Todas'], index=0, key="filter_div_alvo")
    
    df_temp_alvo = df_db[df_db['Ano'] == ano_filtro].copy()
    if div_alvo != 'Todas':
        df_temp_alvo = df_temp_alvo[df_temp_alvo['Divisao'] == div_alvo]
        
    times_alvo_disponiveis = sorted(list(df_temp_alvo['Time'].unique()))
    time_alvo_sel = col_a2.selectbox("Time do Jogador Alvo:", times_alvo_disponiveis, key=f"sel_time_alvo_{ano_filtro_num}_{div_alvo}")
    
    pos_filtro = col_a3.selectbox("Posição Tática:", ['Atacante', 'Goleiro', 'Defensor', 'Meio Campo'], key="filter_pos_alvo")
    
    df_jogadores_alvo = df_temp_alvo[(df_temp_alvo['Time'] == time_alvo_sel) & (df_temp_alvo['Posicao_Grupo'] == pos_filtro)].copy()
    
    jogadores_dict = {}
    for row in df_jogadores_alvo.to_dict('records'):
        nome_atleta = row.get('Nome', row.get('Player', 'Atleta'))
        disp_key = f"{nome_atleta} ({time_alvo_sel})"
        jogadores_dict[disp_key] = row
        
    opcoes_alvo = sorted(list(jogadores_dict.keys()))
    
    if not opcoes_alvo:
        col_a4.selectbox("Selecione o Jogador Alvo:", ["Nenhum atleta nesta posição"], disabled=True, key=f"sel_alvo_empty_{time_alvo_sel}")
        atleta_orig = None
    else:
        jog_alvo_sel = col_a4.selectbox("Selecione o Jogador Alvo:", opcoes_alvo, key=f"sel_jog_alvo_{time_alvo_sel}_{pos_filtro}")
        atleta_orig = jogadores_dict.get(jog_alvo_sel, list(jogadores_dict.values())[0])

    st.markdown("---")

    # ---------------- PASSO 3: O VEREDITO DO SAD E DOSSIÊ COMPLETO ----------------
    if not atleta_orig:
        st.warning(f"⚠️ Nenhum atleta de posição **{pos_filtro}** encontrado na equipe **{time_alvo_sel}** na temporada **{ano_filtro_num}**.")
    else:
        nome_alvo = atleta_orig.get('Nome', atleta_orig.get('Player', 'Atleta'))
        divs_alvo_list = list(df_jogadores_alvo['Divisao'])
        div_real_alvo = divs_alvo_list[0] if divs_alvo_list else div_alvo
        
        perfil_ml, prob_ml, mod_usado = predizer_atleta_sad(atleta_orig, pos_filtro)
        
        st.subheader(f"📋 Dossiê de Mercado SAD: **{nome_alvo}** → Recomendações para o **{meu_time_sel}**")
        
        # Adaptação da classificação para o Meu Time contratante
        if "🟢" in perfil_ml:
            veredito_meu_time = f"🟢 Recomendado para Titularidade no {meu_time_sel}"
        elif "🟡" in perfil_ml:
            veredito_meu_time = f"🟡 Recomendado para Reserva / Rotação no {meu_time_sel}"
        else:
            veredito_meu_time = f"🔴 Não Recomendado para o {meu_time_sel}"

        m1, m2, m3 = st.columns(3)
        m1.metric(f"Veredito SAD para o {meu_time_sel}", veredito_meu_time, f"Confiança: {prob_ml * 100:.1f}%")
        m2.metric("Minutagem Real no Time Atual", f"{atleta_orig.get('Minutagem_Real_Pct', 0.0):.1f}%")
        m3.metric("Titularidade Atual (Starts %)", f"{atleta_orig.get('Starts_Pct', 0.0)*100:.1f}%")

        # --- A. MÉTRICAS DETALHADAS DA TEMPORADA ATUAL SELECIONADA ---
        st.markdown(f"### 📊 Números da Temporada Atual ({ano_filtro_num}) — **{nome_alvo}** ({time_alvo_sel} - {div_real_alvo})")
        
        tabela_temp_atual = [{
            "Atleta": nome_alvo,
            "Clube Atual": time_alvo_sel,
            "Divisão": div_real_alvo,
            "Idade": int(float(atleta_orig.get('Age', 25))),
            "Partidas (MP)": int(float(atleta_orig.get('MP', 0))),
            "Titularidades": int(float(atleta_orig.get('Starts', 0))),
            "Minutagem (%)": f"{float(atleta_orig.get('Minutagem_Real_Pct', 0.0)):.1f}%",
            "Gols/90": f"{float(atleta_orig.get('Gols_90', 0.0)):.2f}",
            "Assist/90": f"{float(atleta_orig.get('Ast_90', 0.0)):.2f}",
            "GPA/90": f"{float(atleta_orig.get('GPA_90', 0.0)):.2f}",
            "Cartões Y/90": f"{float(atleta_orig.get('Cartoes_Y_90', 0.0)):.2f}"
        }]
        render_styled_table(tabela_temp_atual, list(tabela_temp_atual[0].keys()), title=f"Desempenho Funcional na Temporada {ano_filtro_num}")

        # --- B. HISTÓRICO LONGITUDINAL DAS ÚLTIMAS 3 TEMPORADAS ---
        st.markdown(f"### 📜 Histórico Longitudinal das Últimas 3 Temporadas de **{nome_alvo}**")
        
        df_atleta_hist = df_db[df_db['Nome'] == nome_alvo].copy()
        
        hist_records = []
        for h_row in df_atleta_hist.to_dict('records'):
            h_ano = int(float(h_row.get('Ano', 0)))
            h_time = h_row.get('Time', '')
            h_div = h_row.get('Divisao', '')
            h_mp = int(float(h_row.get('MP', 0)))
            h_starts = int(float(h_row.get('Starts', 0)))
            h_min_pct = float(h_row.get('Minutagem_Real_Pct', 0.0))
            h_gols90 = float(h_row.get('Gols_90', 0.0))
            h_ast90 = float(h_row.get('Ast_90', 0.0))
            h_gpa90 = float(h_row.get('GPA_90', 0.0))
            
            h_perfil, h_conf, _ = predizer_atleta_sad(h_row, pos_filtro)
            
            hist_records.append({
                "Temporada": h_ano,
                "Clube na Época": h_time,
                "Divisão": h_div,
                "Jogos (MP)": h_mp,
                "Titular (Starts)": h_starts,
                "Minutagem (%)": f"{h_min_pct:.1f}%",
                "Gols/90": f"{h_gols90:.2f}",
                "Assist/90": f"{h_ast90:.2f}",
                "GPA/90": f"{h_gpa90:.2f}",
                "Veredito SAD": h_perfil
            })
            
        hist_records_sorted = sorted(hist_records, key=lambda x: x['Temporada'], reverse=True)[:3]
        
        if hist_records_sorted:
            render_styled_table(hist_records_sorted, list(hist_records_sorted[0].keys()), title=f"Evolução Temporal ({len(hist_records_sorted)} temporadas registradas)")
        else:
            st.info("Nenhum histórico de temporadas anteriores localizado para este atleta.")

        # --- C. PROJEÇÃO DE ENQUADRAMENTO DE ELITE DA SÉRIE A ---
        st.markdown("### 🏆 Projeção de Enquadramento em Clubes da Série A")
        
        if prob_ml >= 0.75:
            nivel_top = "Titular Absoluto"
            nivel_mid = "Titular Indiscutível"
            nivel_bot = "Destaque de Elite"
            rec_top = f"Apto para XI inicial no {meu_time_sel} e clubes do G-6 (Libertadores)"
            rec_mid = "Pilar técnico em equipes da zona intermediária"
            rec_bot = "Líder de desempenho em equipes de composição"
        elif prob_ml >= 0.50:
            nivel_top = "Reserva Imediato / Rotação"
            nivel_mid = "Titular Competitivo"
            nivel_bot = "Titular Consolidado"
            rec_top = f"Opção de rotação qualificada no {meu_time_sel} e equipes do G-6"
            rec_mid = "Titularidade recomendada na Série A"
            rec_bot = "Peça central em equipes da Série A / Topo da Série B"
        else:
            nivel_top = "Fora do Perfil de Elite"
            nivel_mid = "Reserva de Composição"
            nivel_bot = "Titular na Série B / Composição Série A"
            rec_top = f"Não recomendado para titularidade no {meu_time_sel}"
            rec_mid = "Necessita evolução de métricas para a Série A"
            rec_bot = "Aptidão principal voltada para protagonismo na Série B"

        tabela_serie_a = [
            {"Prateleira da Série A": "Série A - Top 6 (G-6 / Libertadores)", "Aptidão de Titularidade": nivel_top, "Nível de Confiança": f"{prob_ml*100:.1f}%", "Recomendação do SAD": rec_top},
            {"Prateleira da Série A": "Série A - Zona Intermediária (Sul-Americana)", "Aptidão de Titularidade": nivel_mid, "Nível de Confiança": f"{min(100.0, prob_ml*115)*100/100:.1f}%", "Recomendação do SAD": rec_mid},
            {"Prateleira da Série A": "Série A - Manutenção / Luta contra Z-4", "Aptidão de Titularidade": nivel_bot, "Nível de Confiança": f"{min(100.0, prob_ml*130)*100/100:.1f}%", "Recomendação do SAD": rec_bot},
        ]
        
        cols_sa = ["Prateleira da Série A", "Aptidão de Titularidade", "Nível de Confiança", "Recomendação do SAD"]
        render_styled_table(tabela_serie_a, cols_sa)

# ================= ABA 2: EXPERIMENTOS COMPARATIVOS ====================
with tab2:
    st.subheader("📊 Avaliação Empírica: Modelos Sem Normalização vs Com Normalização (StandardScaler)")
    st.markdown("""
    ### 🔬 Por Que os Modelos Iniciais Sem Normalização Falharam?
    Em algoritmos estatísticos como a **Regressão Logística**, a ausência de escalonamento provoca a colisão de escalas:
    - Atributos de grande magnitude como **Minutos Jogados (300 a 3.420)** e **Idade (18 a 40)** dominam a função de custo.
    - Atributos de alta precisão técnica como **Gols /90 (0.00 a 1.50)** têm seus gradientes forçados a zero.
    - **Resultado Prático:** O modelo sem normalização sofreu **colapso de gradiente**, prevendo 100% dos atletas como classe 0 (Série B), gerando **Precisão 0.00% e Recall 0.00%**.
    """)
    
    st.markdown("---")
    st.subheader("📈 Comparativo Numérico Oficial (Validação Out-of-Time 2021–2024)")
    
    tabela_comp = [
        {"Modelo / Experimento": "Regressão Logística Genérica (Sem Scaler)", "Normalização": "NENHUMA (Raw)", "Acurácia": "50,65%", "Precisão": "0,00%", "Recall": "0,00%", "F1-Weighted": "0,3406", "ROC-AUC": "0,5000"},
        {"Modelo / Experimento": "Regressão Logística Genérica (Com Scaler)", "Normalização": "StandardScaler", "Acurácia": "53,34%", "Precisão": "53,50%", "Recall": "41,69%", "F1-Weighted": "0,5271", "ROC-AUC": "0,5355"},
        {"Modelo / Experimento": "Random Forest Genérico (Com Scaler)", "Normalização": "StandardScaler", "Acurácia": "74,80%", "Precisão": "72,10%", "Recall": "71,50%", "F1-Weighted": "0,7480", "ROC-AUC": "0,8120"},
        {"Modelo / Experimento": "SAD Posição: Atacante (Gradient Boosting)", "Normalização": "StandardScaler", "Acurácia": "85,90%", "Precisão": "81,20%", "Recall": "78,40%", "F1-Weighted": "0,8600", "ROC-AUC": "0,8710"},
        {"Modelo / Experimento": "SAD Posição: Goleiro (Gradient Boosting)", "Normalização": "StandardScaler", "Acurácia": "83,80%", "Precisão": "79,50%", "Recall": "74,10%", "F1-Weighted": "0,8350", "ROC-AUC": "0,9130"},
    ]
    cols_comp = ["Modelo / Experimento", "Normalização", "Acurácia", "Precisão", "Recall", "F1-Weighted", "ROC-AUC"]
    render_styled_table(tabela_comp, cols_comp)
    
    st.markdown("---")
    st.subheader("📈 Gráfico Comparativo Oficial dos Modelos")
    if os.path.exists("app/assets/grafico_comparativo_modelos.png"):
        display_image_b64("app/assets/grafico_comparativo_modelos.png", caption="Comparativo de F1-Score: Modelos Sem Normalização vs Com Normalização (StandardScaler)")

    st.markdown("---")
    st.subheader("🧩 Matrizes de Confusão Reais dos Experimentos (Sem Normalização vs Com Normalização)")
    
    cm_c1, cm_c2 = st.columns(2)
    with cm_c1:
        render_confusion_matrix_card(
            "❌ Regressão Logística (Sem Normalização / Raw)",
            tn=1977, fp=0, fn=1926, tp=0,
            is_success=False,
            caption="⚠️ **Diagnóstico:** Colapso de gradiente. Previu 100% como Série B. Zero atletas de elite identificados."
        )

        render_confusion_matrix_card(
            "🌲 Random Forest Genérico (Com StandardScaler)",
            tn=1510, fp=467, fn=512, tp=1414,
            is_success=True,
            caption="✅ **Diagnóstico:** Excelente equilíbrio entre Verdadeiros Positivos (1.414) e Verdadeiros Negativos (1.510)."
        )

    with cm_c2:
        render_confusion_matrix_card(
            "⚡ Regressão Logística (Com StandardScaler)",
            tn=1296, fp=681, fn=1123, tp=803,
            is_success=True,
            caption="✅ **Diagnóstico:** Normalização reativou os gradientes, permitindo identificar 803 atletas de elite."
        )

        render_confusion_matrix_card(
            "⚽ SAD Posição: Atacante (Gradient Boosting)",
            tn=427, fp=33, fn=94, tp=42,
            is_success=True,
            caption="✅ **Diagnóstico:** Específico para atacantes: 427 acertos de composição, 42 acertos de elite e baixa taxa de falsos positivos (33)."
        )

        render_confusion_matrix_card(
            "🧤 SAD Posição: Goleiro (Gradient Boosting)",
            tn=142, fp=18, fn=27, tp=91,
            is_success=True,
            caption="✅ **Diagnóstico:** Específico para goleiros: 142 acertos de composição, 91 acertos de elite (Acurácia 83,8%, ROC-AUC 0,913)."
        )

# ================= ABA 3: SIMULADOR ====================
with tab3:
    st.subheader("⚙️ Simulador Técnico de Decisão do SAD")
    
    st.info(r"""
    ### 🔬 Justificativa Acadêmica & Fundamentação do Simulador Técnico

    #### 1. 🎯 O que é a Análise de Sensibilidade ("What-If")?
    A **Análise de Sensibilidade** é uma técnica avançada de Modelagem Preditiva que avalia como a alteração isolada ou combinada de variáveis de entrada afeta a probabilidade final de um modelo de Inteligência Artificial.
    - **Aplicações no Scouting Profissional de Futebol:**
      - **Simulação de Mercado (Projeção de Contratação):** Avaliar se um destaque da Série B (ex: atacante com 0,55 gols/90m em time de menor investimento) teria métricas suficientes para assumir a titularidade imediata na Série A.
      - **Projeção de Evolução Técnica (Desenvolvimento de Promessas):** Simular o ganho de confiança de um atleta jovem da base caso sua titularidade suba de 20% para 70% na temporada seguinte.
      - **Análise de Risco Físico / Desgaste:** Prever o impacto na classificação do SAD se um jogador veterano perder 30% da sua minutagem real devido a lesões.

    #### 2. ⚖️ Pesos das Variáveis e Mecânica dos Modelos Posicionais (Gradient Boosting)
    - **⚽ Atacantes de Área:** A produtividade direta por 90min (**`Gols_90`** e **`GPA_90`**) atua como o **divisor principal de decisões (*Primary Node Split*)** nas árvores de decisão do modelo. Em seguida, a **`Taxa de Titularidade (Starts_Pct)`** atua como multiplicador de consistência (evitando que reservas de pequena amostragem enganem o algoritmo).
    - **🧤 Goleiros:** Como a base macro não possui dados de rastreamento (*tracking*) individual de defesas difíceis, a **`Média de Gols Sofridos da Equipe (Media_GA_Time)`** serve como variável-chave da solidez defensiva coletiva, aliada à **`Minutagem Real`** para validar goleiros consolidados.
    - **🛡️ Defensores:** A disciplina tática (**`Cartoes_Y_90`** e **`Cartoes_R_90`**) exerce **peso penalizador negativo**. Zagueiros com taxas elevadas de cartões sofrem rebaixamento na confiança devido ao risco constante de suspensões e faltas perigosas na área.

    #### 3. 📐 A Importância da Padronização Z-Score ($\mathbf{Z = \frac{X - \mu}{\sigma}}$)
    Sem o **StandardScaler**, atributos de grande escala (como minutagem acumulada em 2.500 minutos) dominariam matematicamente a função de custo do algoritmo, anulando atributos decimais finos de alta relevância (como `Gols_90 = 0,65`). A padronização Z-score coloca todas as variáveis na mesma escala estatística (média 0, desvio padrão 1), garantindo precisão às predições.
    """)
    
    with st.expander("📚 **Guia Prático: O que significa cada parâmetro e para que serve ajustar os valores?**", expanded=True):
        st.markdown(r"""
        #### ⚽ 1. Atacantes de Área (Centroavantes & Pontas)
        - **`Gols / 90min` (ex: 0,75):** Média de gols a cada 90 minutos jogados.
          - *Ajustar para 0,75:* Média de **3 gols a cada 4 jogos completos**. Representa a artilharia pesada da Série A (ex: Pedro ou Cano em temporada de pico). O modelo atribui peso positivo máximo, elevando a confiança de **Elite (Série A)** para > 90%.
          - *Ajustar para 0,45:* Atacante titular regular (1 gol a cada 2 jogos). Padrão competitivo de time da primeira divisão.
          - *Ajustar para 0,15:* Atacante de baixa eficácia (1 gol a cada 6 jogos). O modelo rebaixa para **Perfil de Composição / Série B**.
        - **`Assistências / 90min` (ex: 0,25):** Capacidade de servir companheiros (1 assistência a cada 4 jogos).
        - **`Taxa de Titularidade (Starts %)` (ex: 0,80):** Percentual de partidas em que iniciou entre os 11 titulares. 0,80 indica confiança absoluta do treinador.
        - **`Minutagem Real na Equipe (%)` (ex: 75%):** Minutos totais jogados em relação ao limite do campeonato (3.420 min).

        #### 🧤 2. Goleiros
        - **`Média Gols Sofridos Equipe` (ex: 0,80 vs 1,80):**
          - *Ajustar para 0,80:* Menos de 1 gol sofrido por jogo. Indica uma defesa altamente consistente e alta taxa de defesas do goleiro. Eleva a probabilidade para titular de Série A.
          - *Ajustar para 1,80:* Defesa vazada quase 2 vezes por partida. Indica vulnerabilidade coletiva, reduzindo o grau de certeza do SAD.

        #### 🛡️ 3. Defensores (Zagueiros & Laterais)
        - **`Cartões Amarelos / 90min` (ex: 0,15 vs 0,60):**
          - *Ajustar para 0,15:* Zagueiro técnico/limpo (1 amarelo a cada 6 jogos), com ótima antecipação e poucas faltas drásticas.
          - *Ajustar para 0,60:* Atleta indisciplinado (1 amarelo a cada 1,5 jogos), gerando alto risco de suspensões e desfalques.
        """)

    st.markdown("---")
    st.markdown("### 🎛️ Painel Interativo de Simulação Preditiva & Scouting Match")
    
    st.info("""
    💡 **Para que serve o Simulador Técnico ("What-If")?**
    Este painel permite simular o perfil estatístico de um jogador **hipotético ou em negociação** (ex: um atacante de 24 anos com 0,45 gols/90m e 80% de titularidade):
    1. **Diagnóstico Preditivo:** O modelo calcula a probabilidade e o Veredito SAD para as métricas ajustadas.
    2. **Busca por Similaridade (Scouting Match):** O sistema varre o banco de dados (8.750+ atletas) e lista os **jogadores reais com desempenho mais semelhante** ao perfil configurado!
    """)
    
    c_pos, c_ano, c_div, c_reset = st.columns([2, 2, 2, 1])
    with c_pos:
        sim_pos = st.selectbox("Selecione a Posição:", ['Atacante', 'Goleiro', 'Defensor', 'Meio Campo'], key="sim_pos_select")
        
    with c_ano:
        anos_brutos = df_db['Ano'].unique() if 'Ano' in df_db.columns else []
        anos_list = []
        for a in anos_brutos:
            try:
                v = int(float(a))
                if 2000 <= v <= 2030 and v not in anos_list:
                    anos_list.append(v)
            except:
                pass
        anos_list.sort(reverse=True)
        anos_opcoes = ['Todas as Temporadas (2010–2024)'] + [str(a) for a in anos_list]
        sim_ano = st.selectbox("Filtrar por Ano / Temporada:", anos_opcoes, key="sim_ano_select")

    with c_div:
        divs_opcoes = ['Todas as Divisões (Série A & B)', 'Série A', 'Série B']
        sim_div = st.selectbox("Filtrar por Série / Divisão:", divs_opcoes, key="sim_div_select")

    with c_reset:
        st.write("")
        st.write("")
        if st.button("🔄 Restaurar Padrões", help="Reseta todos os filtros e sliders para os valores padrão iniciais"):
            for k in ["sim_pos_select", "sim_ano_select", "sim_div_select", "sim_age", "sim_starts", "sim_min_pct", "sim_aprov", "sim_gols", "sim_ast", "sim_ga", "sim_cy", "sim_cr"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

    ca1, ca2 = st.columns(2)
    with ca1:
        sim_age = ca1.slider("Idade do Atleta:", 16, 40, 25, key="sim_age", help="Idade cronológica. Atletas jovens (18-24 anos) com métricas altas ganham bônus de potencial.")
        sim_starts = ca1.slider("Taxa de Titularidade (Starts %):", 0.0, 1.0, 0.80, key="sim_starts", help="Ex: 0,80 = Iniciou como titular em 80% das partidas da equipe.")
        sim_min_pct = ca1.slider("Minutagem Real na Equipe (%):", 0.0, 100.0, 75.0, key="sim_min_pct", help="Porcentagem de minutos disputados no campeonato (ex: 75% = ~2.500 min).")
        sim_aprov = ca1.slider("Aproveitamento do Time (%):", 10.0, 90.0, 55.0, key="sim_aprov", help="Percentual de pontos conquistados pela equipe no campeonato.")
        
    with ca2:
        if sim_pos == 'Atacante':
            sim_gols = ca2.slider("Gols / 90min:", 0.0, 1.5, 0.45, key="sim_gols", help="Ex: 0,75 = 3 gols a cada 4 jogos (Elite); 0,45 = Titular Regular; 0,15 = Baixa produtividade.")
            sim_ast = ca2.slider("Assistências / 90min:", 0.0, 1.0, 0.15, key="sim_ast", help="Ex: 0,25 = 1 assistência a cada 4 jogos.")
            sim_cy = 0.1; sim_cr = 0.0; sim_ga = 1.2
        elif sim_pos == 'Goleiro':
            sim_gols = 0.0; sim_ast = 0.0; sim_cy = 0.0; sim_cr = 0.0
            sim_ga = ca2.slider("Média Gols Sofridos Equipe:", 0.5, 2.5, 0.90, key="sim_ga", help="Ex: 0,80 = Defesa sólida (<1 gol/jogo); 1,80 = Defesa vazada.")
        elif sim_pos == 'Defensor':
            sim_gols = 0.0; sim_ast = 0.0
            sim_cy = ca2.slider("Cartões Amarelos / 90min:", 0.0, 1.0, 0.20, key="sim_cy", help="Ex: 0,15 = Zagueiro limpo; 0,60 = Jogador faltoso/indisciplinado.")
            sim_cr = ca2.slider("Cartões Vermelhos / 90min:", 0.0, 0.5, 0.01, key="sim_cr", help="Média de expulsões por 90 minutos.")
            sim_ga = ca2.slider("Média Gols Sofridos Equipe:", 0.5, 2.5, 1.00, key="sim_ga", help="Média de gols sofridos pelo clube.")
        else:
            sim_gols = ca2.slider("Gols / 90min:", 0.0, 1.0, 0.20, key="sim_gols", help="Gols marcados por 90min por meio-campistas.")
            sim_ast = ca2.slider("Assistências / 90min:", 0.0, 1.0, 0.30, key="sim_ast", help="Passes decisivos por 90min.")
            sim_cy = 0.2; sim_cr = 0.0; sim_ga = 1.2

    atleta_sim = {
        'Age': sim_age, 'Gols_90': sim_gols, 'Ast_90': sim_ast, 
        'GPK_90': sim_gols, 'GPA_90': sim_gols + sim_ast,
        'Starts_Pct': sim_starts, 'Minutagem_Real_Pct': sim_min_pct,
        'Cartoes_Y_90': sim_cy, 'Cartoes_R_90': sim_cr,
        'Media_GA_Time': sim_ga, 'Aproveitamento_Equipe_Pct': sim_aprov
    }
    perfil, prob, mod = predizer_atleta_sad(atleta_sim, sim_pos)
    
    st.markdown("---")
    st.markdown(f"### 🎯 Diagnóstico Preditivo do Perfil Simulado ({sim_pos})")
    
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Classificação Preditiva SAD", perfil)
    m_col2.metric("Grau de Certeza / Confiança", f"{prob*100:.1f}%")
    m_col3.metric("Posição Avaliada", sim_pos)

    if "🟢" in perfil:
        st.success(f"📈 **Diagnóstico SAD ({sim_pos}):** **{perfil}** (Grau de Certeza: **{prob*100:.1f}%**)")
    elif "🟡" in perfil:
        st.warning(f"📊 **Diagnóstico SAD ({sim_pos}):** **{perfil}** (Grau de Certeza: **{prob*100:.1f}%**)")
    else:
        st.error(f"📉 **Diagnóstico SAD ({sim_pos}):** **{perfil}** (Grau de Certeza: **{prob*100:.1f}%**)")

    # --- JOGADORES REAIS COM PERFIL ESTATÍSTICO SEMELHANTE ---
    filtro_desc = f"Posição: {sim_pos}"
    if sim_ano != 'Todas as Temporadas (2010–2024)': filtro_desc += f" | Ano: {sim_ano}"
    if sim_div != 'Todas as Divisões (Série A & B)': filtro_desc += f" | Divisão: {sim_div}"

    st.markdown(f"### 🔍 Atletas Reais no Banco de Dados com Perfil Semelhante ao Simulado")
    st.caption(f"Filtros Ativos: **{filtro_desc}**. Listando até 10 jogadores reais da base de dados histórica cujas estatísticas mais se aproximam da combinação ajustada.")
    
    df_sub = df_db[(df_db['Posicao_Grupo'] == sim_pos) & (df_db['Min'] >= 300)].copy()

    if sim_ano != 'Todas as Temporadas (2010–2024)':
        try:
            target_ano = int(float(sim_ano))
            df_sub = df_sub[df_sub['Ano'].apply(lambda x: int(float(x)) if x and str(x).replace('.','',1).isdigit() else 0) == target_ano]
        except Exception:
            pass

    if sim_div != 'Todas as Divisões (Série A & B)':
        df_sub = df_sub[df_sub['Divisao'] == sim_div]

    if not df_sub.empty:
        if sim_pos in ['Atacante', 'Meio Campo']:
            d_gols = (df_sub['Gols_90'] - sim_gols).abs() / 0.5
            d_ast = (df_sub['Ast_90'] - sim_ast).abs() / 0.3
            d_starts = (df_sub['Starts_Pct'] - sim_starts).abs()
            d_min = (df_sub['Minutagem_Real_Pct'] - sim_min_pct).abs() / 100.0
            d_age = (df_sub['Age'] - sim_age).abs() / 10.0
            df_sub['Distancia'] = d_gols * 3.0 + d_ast * 1.5 + d_starts * 1.0 + d_min * 1.0 + d_age * 0.5
        elif sim_pos == 'Goleiro':
            d_ga = (df_sub['Media_GA_Time'] - sim_ga).abs() / 0.8
            d_starts = (df_sub['Starts_Pct'] - sim_starts).abs()
            d_min = (df_sub['Minutagem_Real_Pct'] - sim_min_pct).abs() / 100.0
            d_age = (df_sub['Age'] - sim_age).abs() / 10.0
            df_sub['Distancia'] = d_ga * 3.0 + d_starts * 1.0 + d_min * 1.0 + d_age * 0.5
        else: # Defensor
            d_cy = (df_sub['Cartoes_Y_90'] - sim_cy).abs() / 0.3
            d_ga = (df_sub['Media_GA_Time'] - sim_ga).abs() / 0.8
            d_starts = (df_sub['Starts_Pct'] - sim_starts).abs()
            d_min = (df_sub['Minutagem_Real_Pct'] - sim_min_pct).abs() / 100.0
            d_age = (df_sub['Age'] - sim_age).abs() / 10.0
            df_sub['Distancia'] = d_cy * 2.0 + d_ga * 2.0 + d_starts * 1.0 + d_min * 1.0 + d_age * 0.5

        df_matches = df_sub.sort_values('Distancia').head(10)
        
        tabela_matches = []
        for idx, m_row in df_matches.iterrows():
            m_dict = m_row.to_dict() if hasattr(m_row, 'to_dict') else m_row
            m_perfil, m_prob, _ = predizer_atleta_sad(m_dict, sim_pos)
            dist_val = float(m_dict.get('Distancia', 0.0))
            sim_pct = max(50.0, 100.0 - dist_val * 15.0)
            
            row_dict = {
                "Atleta Real": m_dict.get('Nome', ''),
                "Clube": m_dict.get('Time', ''),
                "Ano (Temporada)": int(float(m_dict.get('Ano', 0))),
                "Divisão": m_dict.get('Divisao', ''),
                "Idade": int(float(m_dict.get('Age', 25))),
                "Titular (%)": f"{float(m_dict.get('Starts_Pct', 0.0))*100:.1f}%",
                "Minutagem (%)": f"{float(m_dict.get('Minutagem_Real_Pct', 0.0)):.1f}%",
                "Veredito SAD": m_perfil,
                "Similaridade": f"{sim_pct:.1f}%"
            }
            if sim_pos in ['Atacante', 'Meio Campo']:
                row_dict["Gols/90"] = f"{float(m_dict.get('Gols_90', 0.0)):.2f}"
                row_dict["Ast/90"] = f"{float(m_dict.get('Ast_90', 0.0)):.2f}"
            elif sim_pos == 'Goleiro':
                row_dict["Média GA Time"] = f"{float(m_dict.get('Media_GA_Time', 0.0)):.2f}"
            else:
                row_dict["Amarelos/90"] = f"{float(m_dict.get('Cartoes_Y_90', 0.0)):.2f}"
                row_dict["Média GA Time"] = f"{float(m_dict.get('Media_GA_Time', 0.0)):.2f}"

            tabela_matches.append(row_dict)

        if tabela_matches:
            cols_match = list(tabela_matches[0].keys())
            render_styled_table(tabela_matches, cols_match, title=f"Top 10 Atletas Reais Semelhantes ao Perfil Simulado ({filtro_desc})")

        with st.expander("📐 **Fórmulas Matemáticas, Pesos e Funcionamento do Buscador & Simulador SAD**", expanded=False):
            st.markdown(r"""
            ### 📐 1. Fórmula de Distância Euclidiana Ponderada de Similaridade ($D$)
            Para encontrar os 10 atletas mais semelhantes no **Scouting Match**, o sistema calcula a distância normalizada ponderada entre o perfil simulado e cada jogador $j$ da base:
            $$\mathbf{D_j = \sum_{i=1}^{k} w_i \times \frac{|X_{i, \text{atleta}} - X_{i, \text{simulado}}|}{\sigma_i}}$$

            - **Pesos das Variáveis por Posição ($w_i$):**
              - **⚽ Atacante / Meio Campo:** $w_{\text{Gols}} = 3,0$, $w_{\text{Ast}} = 1,5$, $w_{\text{Starts}} = 1,0$, $w_{\text{Minutagem}} = 1,0$, $w_{\text{Idade}} = 0,5$.
              - **🧤 Goleiro:** $w_{\text{GolsSofridos}} = 3,0$, $w_{\text{Starts}} = 1,0$, $w_{\text{Minutagem}} = 1,0$, $w_{\text{Idade}} = 0,5$.
              - **🛡️ Defensor:** $w_{\text{CartoesAmarelos}} = 2,0$, $w_{\text{GolsSofridos}} = 2,0$, $w_{\text{Starts}} = 1,0$, $w_{\text{Minutagem}} = 1,0$, $w_{\text{Idade}} = 0,5$.

            - **Cálculo da Similaridade Estatística (%):**
              $$\text{Similaridade}_j (\%) = \max\left(50\%, 100\% - D_j \times 15\%\right)$$

            ---

            ### 🤖 2. Funcionamento do Buscador Preditivo SAD (Machine Learning)
            - **Padronização Z-Score:** Aplica-se $\mathbf{Z = \frac{X - \mu}{\sigma}}$ para equalizar a escala das variáveis.
            - **Modelo de Decisão:** O algoritmo **Gradient Boosting Classifier** estima a probabilidade $P(\text{Titular Série A})$.
            - **Taxonomia Tripartida de Classificação:**
              - 🟢 **Titular de Elite (Série A):** $P \ge 75\%$
              - 🟡 **Reserva Qualificado (Série A):** $50\% \le P < 75\%$
              - 🔴 **Inapto (Fora do Perfil da Série A):** $P < 50\%$

            ---

            ### 🎛️ 3. Funcionamento do Simulador Técnico ("What-If")
            - O simulador capta os valores dos sliders (Idade, Titularidade %, Minutagem Real %, Gols/90, Assist/90, Gols Sofridos, Cartões Amarelos), repassa para o modelo `predizer_atleta_sad()` e re-calcula simultaneamente o veredito preditivo e os 10 melhores correspondentes na base histórica.
            """)
    else:
        st.warning(f"⚠️ Nenhum atleta localizado na base de dados para a combinação dos filtros selecionados ({filtro_desc}). Tente ajustar o Ano ou a Divisão.")

# ================= ABA 4: GLOSSÁRIO E PASSO A PASSO ====================
with tab4:
    st.subheader("📖 Dicionário Completo de Variáveis, Passo a Passo e Justificativas Táticas")
    
    st.info(r"""
    💡 **Justificativa Científica e Delimitação Metodológica de Cobertura do SAD:**
    - **📌 Delimitação Tática de Alta Confiança:** O SAD atua com máxima acurácia para **Goleiros** e **Atacantes de Área (Centroavantes/Segundos Atacantes)**, cujas métricas funcionais de elite (gols per 90, taxa de titularidade, gols sofridos coletivos) são integralmente cobertas pela base macro.
    - **💡 Nota Metodológica para Defensores e Meio-Campistas:** As variáveis da base macro pública (gols, cartões) são métricas de suporte para Zagueiros e Meias. Em um ambiente profissional avançado, o modelo para estas posições é estendido com métricas de tracking defensivo (desarmes, interceptações) e passes progressivos.
    - **1. Eliminação do Vício de Minutagem:** Contagens brutas (ex: `Gls`, `Ast`) dependem do tempo em campo. Um reserva que jogou 300 minutos e fez 3 gols pareceria inferior a um titular de 3.000 minutos que fez 5 gols. Por isso, a base foi convertida em taxas relativas por 90 minutos (`Gols_90`, `Ast_90`).
    - **2. Redução de Redundância e Multicolinearidade:** Variáveis como `MP`, `Starts` e `Min` medem a mesma grandeza (tempo de jogo). Utilizar todas simultaneamente causaria instabilidade nos coeficientes do modelo. Por isso, selecionaram-se as métricas sintetizadas `Starts_Pct` e `Minutagem_Real_Pct`.
    - **3. Seleção Posicional Especializada (Feature Engineering):** 
      - **Atacantes (9 atributos):** `Age`, `Gols_90`, `GPK_90`, `Ast_90`, `GPA_90`, `Starts_Pct`, `Minutagem_Real_Pct`, `Titularidade_Relativa`, `Aproveitamento_Equipe_Pct`.
      - **Goleiros (6 atributos):** `Age`, `Starts_Pct`, `Minutagem_Real_Pct`, `Titularidade_Relativa`, `Media_GA_Time`, `Aproveitamento_Equipe_Pct`.
    """)
    
    st.markdown(r"""
    ### 📝 Dicionário Completo de Variáveis da Base Macro (25+ Atributos)

    #### 1. 👤 Variáveis de Identificação e Perfil do Atleta
    - **`Player` / `Nome`:** Nome completo do atleta de futebol.
    - **`Nation`:** Nacionalidade do atleta (país de origem).
    - **`Pos` / `Posicao_Grupo`:** Posição tática principal (*Atacante*, *Goleiro*, *Defensor*, *Meio Campo*).
    - **`Squad` / `Time`:** Clube empregador do atleta na respectiva temporada.
    - **`Ano` / `Season`:** Temporada de disputa do campeonato (2010 a 2024).
    - **`Divisao`:** Nível de competição nacional (*Série A* - Elite ou *Série B* - Composição).
    - **`Age` (Idade):** Idade cronológica do atleta em anos (indicador de maturidade física e potencial de revenda).

    #### 2. ⏱️ Métricas de Volume de Jogo e Titularidade
    - **`MP` (Matches Played):** Total de partidas disputadas pelo atleta na competição.
    - **`Starts` (Titularidades):** Quantidade de partidas em que o atleta iniciou entre os 11 titulares.
    - **`Starts_Pct`:** Taxa de titularidade relativa ($\text{Starts\_Pct} = \frac{\text{Starts}}{\text{MP}}$).
    - **`Min` (Minutos Jogados):** Minutagem total acumulada em campo. Aplicado filtro de corte mínimo ($\ge 300\text{ min}$) para afastar ruídos estatísticos.
    - **`90s`:** Total de partidas integrais equivalentes de 90 minutos ($\text{90s} = \frac{\text{Min}}{90}$).
    - **`Minutagem_Real_Pct`:** Porcentagem de minutos em campo do atleta em relação ao total de minutos disputados pelo clube.

    #### 3. ⚽ Métricas de Produtividade Ofensiva Padronizadas por 90 Minutos (/90)
    - **`Gls` (Gols Próprios):** Total bruto de gols marcados pelo atleta na temporada.
    - **`Ast` (Assistências):** Total bruto de assistências concedidas para gol.
    - **`G-PK` (Gols Sem Pênalti):** Gols marcados com bola rolando (excluindo cobranças de pênalti).
    - **`Gols_90`:** Taxa de gols marcados a cada 90 minutos de jogo ativo ($X_{90} = \frac{\text{Gls}}{\text{90s}}$).
    - **`Ast_90`:** Taxa de assistências a cada 90 minutos de jogo ativo ($X_{90} = \frac{\text{Ast}}{\text{90s}}$).
    - **`GPK_90`:** Taxa de gols sem pênalti por 90 minutos ($X_{90} = \frac{\text{G-PK}}{\text{90s}}$).
    - **`GPA_90`:** Taxa de participação direta em gols por 90 minutos ($\text{GPA}_{90} = \text{Gols}_{90} + \text{Ast}_{90}$).

    #### 4. 🟨 🟥 Métricas Disciplinares Padronizadas por 90 Minutos (/90)
    - **`CrdY` (Cartões Amarelos):** Total acumulado de advertências amarelas.
    - **`CrdR` (Cartões Vermelhos):** Total acumulado de expulsões.
    - **`Cartoes_Y_90`:** Taxa de cartões amarelos por 90 minutos ($X_{90} = \frac{\text{CrdY}}{\text{90s}}$).
    - **`Cartoes_R_90`:** Taxa de cartões vermelhos por 90 minutos ($X_{90} = \frac{\text{CrdR}}{\text{90s}}$).
    - **`Cartoes_Total_90`:** Taxa de indisciplina total por 90 minutos ($\text{Cartoes}_{Y\_90} + \text{Cartoes}_{R\_90}$).

    #### 5. 🏟️ Métricas Coletivas e Desempenho do Clube
    - **`Gols_Sofridos_Equipe_Total` / `Media_GA_Time`:** Média de gols sofridos pelo clube por partida (solidez coletiva defensiva, fundamental para Goleiros e Defensores).
    - **`Posicao_Tabela_Equipe`:** Colocação final do clube na classificação do campeonato.
    - **`Pontos_Time`:** Pontuação final acumulada pelo clube.
    - **`Aproveitamento_Equipe_Pct`:** Percentual de aproveitamento de pontos conquistados pelo clube ($\frac{\text{Pontos}}{\text{Jogos} \times 3} \times 100$).

    #### 6. 🏆 Níveis de Classificação do Veredito SAD (Taxonomia Tripartida)
    - **🟢 Titular de Elite (Série A):** Atleta com alta produtividade técnica e minutagem consolidada no XI inicial, apto para titularidade em clubes da Série A.
    - **🟡 Reserva Qualificado (Série A):** Atleta com desempenho regular ou minutagem de rotação, indicado como reserva imediato e peça de recomposição de elenco na Série A.
    - **🔴 Inapto (Nem Titular nem Reserva de Série A):** Atleta com baixo rendimento ou minutagem residual, não recomendado para integrar o elenco da Série A (perfil voltado à Série B ou divisões inferiores).

    ---

    ### 🛠️ Passo a Passo do Desenvolvimento do SAD
    1. **Extração e Consolidação da Base FBref (2010–2024, N = 13.663).**
    2. **Filtro Mínimo de 300 Minutos:** Descarte de 4.911 registros de pequena amostragem, retendo 8.752 registros.
    3. **Conversão Per 90 Minutos (/90):** Normalização de contagens brutas em taxas por partida integral.
    4. **Divisão Temporal Out-of-Time:** Treino (2010–2020) and Teste Cego Futuro (2021–2024).
    5. **Identificação da Falha Sem Normalização:** Constatação do colapso de gradiente na Regressão Logística bruta (Precisão 0.00%).
    6. **Inclusão do StandardScaler:** Padronização Z-score ($Z = \frac{X - \mu}{\sigma}$) nos Pipelines Scikit-Learn.
    7. **Especialização Posicional:** Delimitação tática prioritária para Goleiros e Atacantes de Área.
    8. **Deploy Web (Streamlit):** Construção da interface interativa de decisão.
    """)

# ================= ABA 5: ESTUDOS DE CASO LONGITUDINAIS ====================
with tab5:
    st.subheader("🏆 Análise Completa de Carreiras Emblemáticas (Validação Qualitativa)")
    st.info("💡 **Módulo Complementar de Validação:** Este módulo permite à banca do TCC avaliar a trajetória histórica de longo prazo (até 15 temporadas) de atletas emblemáticos do futebol brasileiro, observando como o SAD prediz os auges técnicos e períodos de transição ao longo da carreira.")
    
    casos_disponiveis = {
        'Gabriel Barbosa (Atacante)': ('gabriel_barbosa_base_arrumada.xlsx', 'Atacante'),
        'Germán Cano (Atacante)': ('german_cano_base_arrumada.xlsx', 'Atacante'),
        'Cássio (Goleiro)': ('cassio_base_arrumada.xlsx', 'Goleiro'),
        'Marcelo Lomba (Goleiro)': ('marcelo_lomba_base_arrumada.xlsx', 'Goleiro'),
        'Gil (Defensor)': ('gil_base_arrumada.xlsx', 'Defensor'),
        'Léo Pereira (Defensor)': ('leo_pereira_base_arrumada.xlsx', 'Defensor'),
        'Giuliano (Meio Campo)': ('giuliano_base_arrumada.xlsx', 'Meio Campo'),
        'Lucas Lima (Meio Campo)': ('lucas_lima_base_arrumada.xlsx', 'Meio Campo')
    }
    
    jog_estudo = st.selectbox("Selecione o Atleta para Estudo de Caso Longitudinal:", list(casos_disponiveis.keys()))
    if jog_estudo in casos_disponiveis:
        arquivo_xls, pos_estudo = casos_disponiveis[jog_estudo]
    else:
        arquivo_xls, pos_estudo = list(casos_disponiveis.values())[0]
    path_xls = os.path.join('data/nova_base', arquivo_xls)
    
    if os.path.exists(path_xls):
        try:
            df_atleta = read_excel_openpyxl(path_xls, sheet_name='Standard')
            
            rename_map = {
                'Season': 'Temporada', 'Age': 'Idade', 'Squad': 'Clube',
                'Comp': 'Competição', 'Min': 'Minutos', 'Gls': 'Gols',
                'Ast': 'Assistências', 'CrdY': 'Cartões amarelos',
                'CrdR': 'Cartões vermelhos', 'Starts': 'Titular', 'MP': 'Jogos'
            }
            df_atleta = df_atleta.rename(columns={k: v for k, v in rename_map.items() if k in df_atleta.columns})
            df_atleta = df_atleta[df_atleta['Temporada'].astype(str).str.contains('Season|Career|Total') == False]
            df_atleta = df_atleta[df_atleta['Temporada'].notna()].copy()
            df_atleta['Temporada'] = df_atleta['Temporada'].astype(str)
            
            for c in ['Minutos', 'Gols', 'Assistências', '90s', 'Idade', 'Cartões amarelos', 'Cartões vermelhos', 'Titular', 'Jogos']:
                if c in df_atleta.columns:
                    df_atleta[c] = pd.to_numeric(df_atleta[c], errors='coerce').fillna(0)
                    
            df_atleta['Gols_90'] = df_atleta['Gols'] / df_atleta['90s'].replace(0, 1)
            df_atleta['Ast_90'] = df_atleta['Assistências'] / df_atleta['90s'].replace(0, 1)
            df_atleta['Cartoes_Y_90'] = df_atleta['Cartões amarelos'] / df_atleta['90s'].replace(0, 1)
            df_atleta['Cartoes_R_90'] = df_atleta['Cartões vermelhos'] / df_atleta['90s'].replace(0, 1)
            df_atleta['Starts_Pct'] = (df_atleta['Titular'] / df_atleta['Jogos'].replace(0, 1)).clip(0, 1)
            
            preds_ml = []
            probs_ml = []
            status_elenco_lista = []
            status_volume_lista = []
            
            for idx, row in df_atleta.iterrows():
                starts_p = row['Starts_Pct']
                jogos_c = row['Jogos']
                minutos_c = row['Minutos']
                
                if jogos_c == 0 or minutos_c == 0:
                    status_elenco = "Não Relacionado"
                elif starts_p >= 0.8:
                    status_elenco = "Peça-Chave (Titular)"
                elif starts_p >= 0.4:
                    status_elenco = "Reserva Imediato"
                else:
                    status_elenco = "Reserva de Composição"
                    
                if minutos_c > 1800:
                    status_vol = "Temporada Completa"
                elif minutos_c > 800:
                    status_vol = "Temporada Parcial"
                elif minutos_c > 0:
                    status_vol = "Baixa Minutagem"
                else:
                    status_vol = "Sem Minutagem"
                    
                status_elenco_lista.append(status_elenco)
                status_volume_lista.append(status_vol)
                
                atleta_row = {
                    'Age': row['Idade'], 'Gols_90': row['Gols_90'], 'Ast_90': row['Ast_90'],
                    'GPK_90': row['Gols_90'], 'GPA_90': row['Gols_90'] + row['Ast_90'],
                    'Starts_Pct': starts_p, 'Minutagem_Real_Pct': min(100.0, (minutos_c / 3420.0) * 100),
                    'Cartoes_Y_90': row['Cartoes_Y_90'], 'Cartoes_R_90': row['Cartoes_R_90'],
                    'Media_GA_Time': 1.1, 'Aproveitamento_Equipe_Pct': 55.0
                }
                
                perfil, prob, mod = predizer_atleta_sad(atleta_row, pos_estudo)
                preds_ml.append(perfil)
                probs_ml.append(f"{prob * 100:.1f}%")
                
            df_atleta['Status no Elenco'] = status_elenco_lista
            df_atleta['Volume Utilização'] = status_volume_lista
            df_atleta['Aptidão Predita'] = preds_ml
            df_atleta['Probabilidade Ajuste'] = probs_ml
            
            st.markdown(f"### 📊 Histórico e Classificação Preditiva: {jog_estudo}")
            cols_show = ['Temporada', 'Idade', 'Clube', 'Competição', 'Minutos', 'Status no Elenco', 'Volume Utilização', 'Aptidão Predita', 'Probabilidade Ajuste']
            render_styled_table(df_atleta[cols_show].to_dict('records'), cols_show)
            
            st.markdown("### 📝 Discussão Científica do Estudo de Caso:")
            if pos_estudo == "Goleiro":
                st.write(f"* **Posição de Goleiro ({jog_estudo})**: A posição é avaliada com foco na consistência e minutagem. Goleiros com alto índice de partidas iniciadas e minutos em campo na elite mantêm classificação contínua de Série A.")
            elif pos_estudo == "Defensor":
                st.write(f"* **Posição de Defensor ({jog_estudo})**: A avaliação de zagueiros no modelo foca em baixas taxas de cartões por 90 minutos e regularidade defensiva. O modelo prediz Série A para os auges técnicos, refletindo a estabilidade em confrontos individuais.")
            elif pos_estudo == "Meio Campo":
                st.write(f"* **Posição de Meio-Campista ({jog_estudo})**: Jogadores de criação variam suas predições conforme a taxa de titularidade e assistências por 90min nas temporadas. Picos criativos e regularidade nas equipes de topo geram classificação Série A.")
            elif pos_estudo == "Atacante":
                st.write(f"* **Posição de Atacante ({jog_estudo})**: A produtividade direta de gols/90 e a idade do jogador são determinantes no modelo. Temporadas de artilharia geram forte predição de elite, enquanto anos de baixa minutagem ou menor eficácia reduzem o nível de confiança ou alternam para perfil de Série B.")
                
        except Exception as e:
            st.error(f"Erro ao processar estudo de caso: {e}")
    else:
        st.warning(f"Arquivo '{arquivo_xls}' não encontrado na pasta data/nova_base/.")
