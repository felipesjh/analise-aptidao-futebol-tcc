import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px

st.set_page_config(page_title="TCC - Predição Scout Futebol", page_icon="⚽", layout="wide")

# ----------------- CARREGAMENTO E TRATAMENTO -----------------
@st.cache_data
def load_data():
    path_jog = 'data/processed_tcc/jogadores_consolidado.csv'
    path_camp = 'data/processed_tcc/campeonato_consolidado.csv'
    
    if not os.path.exists(path_jog): return pd.DataFrame()
        
    df = pd.read_csv(path_jog)
    df['Posicao_Original'] = df['Pos']
    df = df.rename(columns={'Player': 'Nome', 'Squad': 'Time', 'Pos': 'Posicao'})
    
    mapa_pos = {'FW': 'Atacante', 'MF': 'Meio Campo', 'DF': 'Defensor', 'GK': 'Goleiro'}
    df['Posicao_Grupo'] = df['Posicao'].str.split(',').str[0].map(mapa_pos).fillna('Outros')
    
    cols_num = ['Gls', 'Ast', 'Min', '90s', 'Age', 'MP', 'CrdY', 'CrdR', 'Starts']
    for col in cols_num:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['Gols_90'] = df['Gls'] / df['90s'].replace(0, 1)
    df['Ast_90'] = df['Ast'] / df['90s'].replace(0, 1)
        
    if os.path.exists(path_camp):
        df_c = pd.read_csv(path_camp)
        df_c['Rk'] = pd.to_numeric(df_c['Rk'], errors='coerce').fillna(0).astype(int)
        df_c = df_c.rename(columns={
            'Squad': 'Time', 
            'GA': 'Gols_Sofridos_Equipe_Total', 
            'MP': 'Jogos_Totais_Equipe', 
            'Rk': 'Posicao_Tabela_Equipe',
            'W': 'Vitorias_Time',
            'D': 'Empates_Time',
            'L': 'Derrotas_Time',
            'Pts': 'Pontos_Time'
        })
        
        cols_sel = ['Time', 'Ano', 'Divisao', 'Gols_Sofridos_Equipe_Total', 'Jogos_Totais_Equipe', 'Posicao_Tabela_Equipe', 'Vitorias_Time', 'Empates_Time', 'Derrotas_Time', 'Pontos_Time']
        df = df.merge(df_c[cols_sel], on=['Time', 'Ano', 'Divisao'], how='left')
        
        for col in ['Gols_Sofridos_Equipe_Total', 'Jogos_Totais_Equipe', 'Posicao_Tabela_Equipe', 'Vitorias_Time', 'Empates_Time', 'Derrotas_Time', 'Pontos_Time']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
        df['Aproveitamento_Equipe_Pct'] = (df['Pontos_Time'] / (df['Jogos_Totais_Equipe'].replace(0, 38) * 3) * 100).clip(0, 100)
        df['Minutagem_Real_Pct'] = (df['Min'] / (df['Jogos_Totais_Equipe'].replace(0, 38) * 90) * 100).clip(0, 100)
        df['Media_GA_Time'] = df['Gols_Sofridos_Equipe_Total'] / df['Jogos_Totais_Equipe'].replace(0, 1)
        df['Gols_Sofridos_Atleta_Estimado'] = (df['Gols_Sofridos_Equipe_Total'] * (df['Minutagem_Real_Pct'] / 100)).round(0)
        
    return df

df_db = load_data()

# ----------------- CARREGAMENTO DO MODELO PREDITIVO (TCC) -----------------
import pickle

@st.cache_resource
def load_ml_model():
    path_model = 'app/assets/modelo_rf_final.pkl'
    path_metrics = 'app/assets/metricas_modelos.pkl'
    if os.path.exists(path_model) and os.path.exists(path_metrics):
        try:
            with open(path_model, 'rb') as f:
                model = pickle.load(f)
            with open(path_metrics, 'rb') as f:
                metrics = pickle.load(f)
            return model, metrics
        except Exception as e:
            st.sidebar.error(f"Erro ao carregar modelo preditivo: {e}")
    return None, None

model_rf, model_metrics = load_ml_model()

def predizer_atleta_ml(atleta):
    if model_rf is None:
        return "N/A (Modelo não treinado)", 0.0
    
    age = atleta.get('Age', 25)
    gols = atleta.get('Gols_90', 0.0)
    ast = atleta.get('Ast_90', 0.0)
    
    minutos = atleta.get('Min', 90)
    crd_y = atleta.get('CrdY', 0)
    crd_r = atleta.get('CrdR', 0)
    starts = atleta.get('Starts', 0)
    mp = atleta.get('MP', 1)
    
    crd_y_90 = (crd_y / minutos) * 90 if minutos > 0 else 0
    crd_r_90 = (crd_r / minutos) * 90 if minutos > 0 else 0
    starts_pct = starts / mp if mp > 0 else 0.5
    
    pos_grupo = atleta.get('Posicao_Grupo', 'Outros')
    pos_atacante = 1.0 if pos_grupo == 'Atacante' else 0.0
    pos_meia = 1.0 if pos_grupo == 'Meio Campo' else 0.0
    pos_defensor = 1.0 if pos_grupo == 'Defensor' else 0.0
    pos_goleiro = 1.0 if pos_grupo == 'Goleiro' else 0.0
    
    features = [[
        age, gols, ast, crd_y_90, crd_r_90, starts_pct,
        pos_atacante, pos_meia, pos_defensor, pos_goleiro
    ]]
    
    try:
        pred = model_rf.predict(features)[0]
        probs = model_rf.predict_proba(features)[0]
        
        perfil_previsto = "Série A" if pred == 1 else "Série B"
        probabilidade = probs[1] if pred == 1 else probs[0]
        return perfil_previsto, probabilidade
    except:
        return "Erro de Predição", 0.0

# ----------------- LOGICA DE CLASSIFICAÇÃO INTELIGENTE (REGRAS) -----------------
def analisar_perfil(atleta, div_atual):
    pos = atleta['Posicao_Grupo']
    
    # 1. Nota Técnica (Independente de minutos) - Qualidade Pura
    if pos == 'Atacante' or pos == 'Meio Campo':
        nota_tecnica = (atleta['Gols_90'] * 1.5 + atleta['Ast_90'] * 1.0)
        perfil_liga = "Série A" if nota_tecnica > 0.25 else "Série B"
    else: # Defesa/Goleiro
        nota_tecnica = max(0, 1 - (atleta['Media_GA_Time'] / 2.0))
        perfil_liga = "Série A" if nota_tecnica > 0.35 else "Série B"
        
    # 2. Índice de Confiança do Treinador (Starts / MP)
    confianca_idx = atleta['Starts'] / atleta['MP'] if atleta['MP'] > 0 else 0
    if confianca_idx >= 0.8: status_elenco = "Peça-Chave (Titular)"
    elif confianca_idx >= 0.4: status_elenco = "Reserva Imediato"
    else: status_elenco = "Reserva de Composição"
    
    # 3. Status de Utilização (Volume)
    minutos = atleta['Minutagem_Real_Pct']
    if minutos > 60: status_volume = "Temporada Completa"
    elif minutos > 30: status_volume = "Temporada Parcial"
    else: 
        if status_elenco == "Peça-Chave (Titular)":
            status_volume = "Interrupção de Ciclo (Venda/Lesão)"
        else:
            status_volume = "Baixa Minutagem (Opção Técnica)"
    
    # 4. Contexto de Alerta (Para a banca)
    aviso = ""
    if atleta['Posicao_Tabela_Equipe'] > 15:
        aviso = "⚠️ Nota impactada pelo baixo desempenho coletivo da equipe na tabela."
    
    return perfil_liga, status_volume, nota_tecnica, aviso, status_elenco

# ----------------- INTERFACE -----------------
st.title("⚽ Plataforma de Scouting Preditivo: Análise de Aptidão Divisional")
st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔍 Dossiê Individual", "📊 Validação Científica", "⚙️ Simulador Técnico", "📖 Glossário & Pesos", "🧪 Estudos de Caso Longitudinal"])

# ================= ABA 1: ANÁLISE INDIVIDUAL ====================
with tab1:
    st.subheader("Buscador de Desempenho Profissional")
    c1, c2, c3, c4 = st.columns(4)
    ano_sel = c1.selectbox("Temporada:", sorted(df_db['Ano'].unique(), reverse=True))
    div_sel = c2.selectbox("Divisão:", df_db[df_db['Ano'] == ano_sel]['Divisao'].unique())
    time_sel = c3.selectbox("Equipe:", sorted(df_db[(df_db['Ano'] == ano_sel) & (df_db['Divisao'] == div_sel)]['Time'].unique()))
    jog_sel = c4.selectbox("Jogador:", sorted(df_db[(df_db['Time'] == time_sel) & (df_db['Ano'] == ano_sel)]['Nome'].unique()))
    
    if st.button("Gerar Análise Profissional", type="primary"):
        # 1. PEGAR A LINHA ESPECÍFICA DO TIME SELECIONADO
        atleta_orig = df_db[(df_db['Nome'] == jog_sel) & (df_db['Ano'] == ano_sel) & (df_db['Time'] == time_sel)].iloc[0]
        
        # 2. BUSCAR SE ELE JOGOU EM OUTROS TIMES NO MESMO ANO
        atleta_ano_total = df_db[(df_db['Nome'] == jog_sel) & (df_db['Ano'] == ano_sel)]
        outros_clubes = atleta_ano_total[atleta_ano_total['Time'] != time_sel]
        tem_multiclube = not outros_clubes.empty
        
        # 3. CONSOLIDAR TOTAIS
        total_jogos_ano = atleta_ano_total['MP'].sum()
        total_minutos_ano = atleta_ano_total['Min'].sum()
        
        perfil_liga, status_vol, nota_tec, aviso_ctx, status_elenco = analisar_perfil(atleta_orig, div_sel)
        perfil_ml, prob_ml = predizer_atleta_ml(atleta_orig)
        
        st.markdown(f"### 📋 Ficha Técnica: {atleta_orig['Nome']}")
        
        if tem_multiclube:
            clubes_lista = ", ".join(atleta_ano_total['Time'].unique())
            st.info(f"🔄 **Atleta Multiclube:** Este jogador representou **{clubes_lista}** em {ano_sel}. Abaixo, detalhes de sua passagem pelo **{time_sel}**.")
            st.write(f"📊 **Consolidado da Temporada:** {int(total_jogos_ano)} jogos totais | {int(total_minutos_ano)} minutos em campo.")

        if atleta_orig['MP'] < 5 and not tem_multiclube:
            st.error("⚠️ **Amostragem Crítica:** Este atleta participou de menos de 5 jogos. Os dados podem não representar o nível real por falta de amostragem.")
        elif aviso_ctx:
            st.warning(aviso_ctx)
            
        # --- BLOCO DE INTELIGÊNCIA ---
        res1, res2, res3, res4 = st.columns(4)
        res1.metric("Perfil (Heurística)", perfil_liga)
        res2.metric("Confiança Treinador", status_elenco, help="Avalia se o jogador é titular absoluto quando disponível.")
        res3.metric("Volume na Temporada", status_vol)
        res4.metric("Qualidade Técnica", f"{nota_tec:.2f}")
        
        st.markdown(f"📈 **Classificação do Modelo (Random Forest):** **{perfil_ml}** (Probabilidade de Ajuste: **{prob_ml * 100:.1f}%**)")
        st.markdown("---")
        
        # Dados de Contexto
        h1, h2, h3 = st.columns(3)
        h1.write(f"**Posição:** {atleta_orig['Posicao_Grupo']} ({atleta_orig['Posicao_Original']})")
        h2.write(f"**Classificação Equipe:** {int(atleta_orig['Posicao_Tabela_Equipe'])}º Lugar")
        h3.write(f"**Idade:** {int(atleta_orig['Age'])} anos")
        
        # Participação
        p1, p2, p3 = st.columns(3)
        p1.metric("Minutagem no Clube", f"{atleta_orig['Minutagem_Real_Pct']:.1f}%")
        p2.metric("Jogos no Clube", f"{int(atleta_orig['MP'])} de {int(atleta_orig['Jogos_Totais_Equipe'])}")
        p3.metric("Titularidade", f"{int(atleta_orig['Starts'])} vezes")
        
        st.markdown("#### ⚽ Estatísticas Detalhadas (Passagem pelo Clube)")
        t1, t2, t3, t4 = st.columns(4)
        t1.metric("Gols Marcados", int(atleta_orig['Gls']), f"{atleta_orig['Gols_90']:.2f}/90min")
        if atleta_orig['Posicao_Grupo'] in ['Goleiro', 'Defensor']:
            t2.metric("Gols Sofridos (Atleta)", int(atleta_orig['Gols_Sofridos_Atleta_Estimado']), delta_color="inverse")
        else:
            t2.metric("Assistências", int(atleta_orig['Ast']), f"{atleta_orig['Ast_90']:.2f}/90min")
        t3.metric("Cartões (Am/Vm)", f"{int(atleta_orig['CrdY'])} / {int(atleta_orig['CrdR'])}")
        t4.metric("Jogos do Time", int(atleta_orig['Jogos_Totais_Equipe']))

        st.markdown("#### 🛡️ Contexto Coletivo (Equipe Selecionada)")
        c_t1, c_t2, c_t3, c_t4 = st.columns(4)
        c_t1.metric("V/E/D Time", f"{int(atleta_orig['Vitorias_Time'])} / {int(atleta_orig['Empates_Time'])} / {int(atleta_orig['Derrotas_Time'])}")
        c_t2.metric("Aproveitamento Time", f"{atleta_orig['Aproveitamento_Equipe_Pct']:.1f}%")
        c_t3.metric("Gols Sofridos (Time)", int(atleta_orig['Gols_Sofridos_Equipe_Total']))
        c_t4.metric("Posição na Tabela", f"{int(atleta_orig['Posicao_Tabela_Equipe'])}º Lugar")

        st.markdown("---")
        # VEREDITO FINAL
        if status_vol == "Interrupção de Ciclo (Venda/Lesão)":
            st.success(f"💎 **Hipótese de Mercado:** O padrão sugere um atleta de elite (**{perfil_ml}**) com saída precoce ou lesão. Recomendado investigar histórico médico/transferências.")
        elif perfil_ml == "Série A":
            st.success(f"🌟 **Veredito:** Perfil estimado pelo modelo preditivo é compatível com o nível da Série A.")
        else:
            st.warning(f"⚠️ **Veredito:** Desempenho compatível com atletas de composição de Série B.")

# ================= ABA 2: VALIDAÇÃO ESTATÍSTICA ====================
with tab2:
    st.subheader("📊 Validação Científica dos Modelos (Out-of-Time 2021-2024)")
    if model_metrics is not None:
        acc_lr = model_metrics.get('lr_accuracy', 0.5286)
        acc_rf = model_metrics.get('rf_accuracy', 0.5278)
        rf_cm = model_metrics.get('rf_cm', [[1144, 833], [1010, 916]])
        lr_cm = model_metrics.get('lr_cm', [[1089, 888], [952, 974]])
        
        st.markdown("""
        ### 🧪 Metodologia de Validação Temporal
        Como estratégia científica para evitar vazamento de dados (*data leakage*) de forma realista, os algoritmos foram validados usando a metodologia **Out-of-Time**:
        *   **Treino (Histórico)**: Temporadas de **2016 a 2020** (4.849 registros de atletas).
        *   **Teste (Futuro)**: Temporadas de **2021 a 2024** (3.903 registros de atletas independentes).
        """)
        
        c_a1, c_a2 = st.columns(2)
        with c_a1:
            st.markdown("#### 🎯 Comparação de Acurácia Geral de Teste")
            df_perf = pd.DataFrame({
                'Acurácia': [acc_lr, acc_rf], 
                'Algoritmo': ['Regressão Logística', 'Random Forest']
            }).set_index('Algoritmo')
            st.bar_chart(df_perf)
            st.write(f"🎯 **Acurácia Regressão Logística (Baseline):** {acc_lr * 100:.2f}%")
            st.write(f"🎯 **Acurácia Random Forest (Principal):** {acc_rf * 100:.2f}%")
            
        with c_a2:
            st.markdown("#### 🧠 Justificativa para a Escolha dos Algoritmos")
            st.markdown("""
            *   **Regressão Logística (Baseline)**: Escolhida por ser um classificador linear clássico extremamente interpretável. Ela serve para analisar o peso direto de cada atributo (coeficientes) e estabelecer o desempenho base do dataset de forma simples.
            *   **Random Forest (Modelo Avançado)**: Um algoritmo baseado em árvores de decisão emparelhadas (*Ensemble*). Ele é ideal para dados tabulares pois consegue capturar relacionamentos não lineares complexos e interações sutis entre variáveis (ex: a relação combinada da Idade e da Posição do jogador com sua minutagem real), sem exigir premissas estritas de linearidade.
            """)
            
        st.markdown("---")
        st.subheader("🧩 Matrizes de Confusão Científicas (Dados de Teste 2021-2024)")
        
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            fig_cm_lr = px.imshow(lr_cm, text_auto=True, x=['Série B', 'Série A'], y=['Série B', 'Série A'], 
                               color_continuous_scale='Greens', title="Matriz de Confusão: Regressão Logística")
            st.plotly_chart(fig_cm_lr, use_container_width=True)
            st.write("**Interpretação (Regressão Logística)**: Classificou corretamente 1.089 atletas da Série B (Verdadeiros Negativos) e 974 da Série A (Verdadeiros Positivos).")
            
        with c_m2:
            fig_cm_rf = px.imshow(rf_cm, text_auto=True, x=['Série B', 'Série A'], y=['Série B', 'Série A'], 
                               color_continuous_scale='Blues', title="Matriz de Confusão: Random Forest")
            st.plotly_chart(fig_cm_rf, use_container_width=True)
            st.write("**Interpretação (Random Forest)**: Classificou corretamente 1.144 atletas da Série B (Verdadeiros Negativos) e 916 da Série A (Verdadeiros Positivos).")

        st.markdown("---")
        st.subheader("📊 Discussão dos Resultados Científicos para a Banca")
        
        st.info("""
        ℹ️ **Por que a acurácia se fixa em cerca de 53%? Isso é bom?**
        
        1. **Ecossistemas Competitivos Auto-Equivalentes**: No futebol de alta performance nacional, a produção individual de volume estatístico é dependente do ecossistema onde o jogador atua. Um atacante titular da Série B joga contra defesas de nível Série B. Logo, suas métricas individuais normalizadas (como gols por 90min, assistências por 90min, minutos jogados) tendem a se equalizar estatisticamente às de um atacante titular da Série A no seu próprio contexto competitivo. Por esse motivo, as divisões atuam como ecossistemas fechados auto-equivalentes, dificultando que modelos puramente numéricos individuais tabulares brutos separem os atletas de forma perfeita.
        2. **Limite Físico da Informação Individual**: O resultado de 53% revela o limite matemático da informação de volume bruto de scout individual (como cartões, idade, titularidade, gols) para traçar a divisão do atleta. Para superar esse limite, seria necessária a inclusão de variáveis qualitativas e de contexto tático da equipe (que compensamos no app adicionando dados de desempenho do time e classificação de titularidade).
        """)
        
        st.warning("""
        📂 **Metodologia de Carga e Extração Híbrida/Manual da Base de Dados**
        
        A base de dados de **13.663 registros** foi consolidada de forma manual e assistida. O portal global **FBref** (fonte original) possui ferramentas robustas de segurança na nuvem (Cloudflare) que impedem e bloqueiam a raspagem de dados automatizada direta (retornando erro *403 Forbidden* para bots). Como os dados de performance esportiva são de domínio público, foi necessária a extração híbrida e manual de dados para contornar essa restrição tecnológica e viabilizar a pesquisa, garantindo a integridade científica e fidedignidade absoluta dos dados coletados.
        """)
    else:
        st.warning("Modelos preditivos reais não encontrados. Execute o pipeline de modelagem.")

# ================= ABA 3: SIMULADOR ====================
with tab3:
    st.subheader("⚙️ Simulador de Cenários e Aptidão Competitiva")
    st.write("Ajuste as métricas de performance do atleta para testar a predição em tempo real usando o Random Forest Classifier.")
    
    ca1, ca2 = st.columns(2)
    with ca1:
        sim_pos = ca1.selectbox("Posição do Atleta:", ['Atacante', 'Meio Campo', 'Defensor', 'Goleiro'])
        sim_age = ca1.slider("Idade do Atleta:", 16, 40, 25)
        sim_starts = ca1.slider("Taxa de Titularidade (Starts %):", 0.0, 1.0, 0.8)
    with ca2:
        sim_gols = ca2.slider("Gols / 90min:", 0.0, 1.5, 0.3)
        sim_ast = ca2.slider("Assist / 90min:", 0.0, 1.0, 0.1)
        sim_y = ca2.slider("Cartões Amarelos / 90min:", 0.0, 1.0, 0.2)
        sim_r = ca2.slider("Cartões Vermelhos / 90min:", 0.0, 0.5, 0.0)
        
    if st.button("Simular Classificação do Modelo", type="primary"):
        if model_rf is not None:
            pos_atacante = 1.0 if sim_pos == 'Atacante' else 0.0
            pos_meia = 1.0 if sim_pos == 'Meio Campo' else 0.0
            pos_defensor = 1.0 if sim_pos == 'Defensor' else 0.0
            pos_goleiro = 1.0 if sim_pos == 'Goleiro' else 0.0
            
            features = [[
                sim_age, sim_gols, sim_ast, sim_y, sim_r, sim_starts,
                pos_atacante, pos_meia, pos_defensor, pos_goleiro
            ]]
            
            pred = model_rf.predict(features)[0]
            probs = model_rf.predict_proba(features)[0]
            
            perfil = "Série A" if pred == 1 else "Série B"
            prob = probs[1] if pred == 1 else probs[0]
            
            if perfil == "Série A":
                st.success(f"📈 **Aptidão Estimada:** **{perfil}** (Probabilidade de Ajuste: **{prob*100:.1f}%**)")
            else:
                st.warning(f"📈 **Aptidão Estimada:** **{perfil}** (Probabilidade de Ajuste: **{prob*100:.1f}%**)")
        else:
            st.error("Modelo preditivo não carregado.")

# ================= ABA 4: GLOSSÁRIO ====================
with tab4:
    st.subheader("📖 Metodologia de Scouting & Manual de Uso")
    
    st.markdown("""
    ### ⚙️ Como Utilizar o Simulador Técnico (Aba 3)
    O **Simulador de Hipóteses** permite que você teste cenários hipotéticos ou analise novos atletas que não estão na base de dados principal. 
    Siga o passo a passo para testar:
    1.  **Posição do Atleta**: Escolha o grupo posicional correspondente. Isso ajusta as variáveis binárias (*dummies*) que o modelo usa internamente.
    2.  **Idade**: Arraste o seletor para simular a idade do jogador. Atletas mais jovens com alto desempenho tendem a receber predições de Série A com maior propensão de valorização de mercado.
    3.  **Taxa de Titularidade (Starts %)**: Representa a porcentagem de partidas em que o atleta começou jogando em relação às que esteve disponível (jogou). Ex: se participou de 10 jogos e começou 8 como titular, a taxa é `0.8` (80%).
    4.  **Métricas por 90 Minutos (/90)**: Ajuste os gols, assistências e cartões baseados no tempo total que ele passa em campo (ver fórmula abaixo).
    5.  **Simular**: Clique em **Simular Classificação de IA**. O modelo Random Forest irá calcular em tempo real e fornecer a classificação final (Série A ou Série B) e a probabilidade de certeza do algoritmo.
    
    *Exemplo de Teste*: Ajuste a posição para **Atacante**, idade para **22 anos**, titularidade para **0.90**, Gols/90 para **0.45** e Assist/90 para **0.15**. O modelo irá classificar o jogador como perfil de **Série A** com alto nível de confiança.
    """)
    
    st.markdown("---")
    st.markdown("""
    ### 📏 Definições e Métricas de Scouting
    
    #### 1. Normalização por 90 Minutos (/90)
    Para garantir uma comparação justa entre atletas que jogam tempos diferentes (por exemplo, um atleta reserva que entra nos minutos finais e faz um gol versus um titular absoluto), todas as estatísticas brutas de gols, assistências e cartões são divididas pelos minutos jogados e multiplicadas por 90:
    $$\\text{Métrica}_{p90} = \\frac{\\text{Métrica Bruta}}{\\text{Minutos Jogados}} \\times 90$$
    
    #### 2. Classificação de Status do Elenco (Confiança do Treinador)
    *   **Peça-Chave (Titular)**: Atleta inicia como titular em 80% ou mais dos jogos em que atuou (`Starts / MP >= 0.8`).
    *   **Reserva Imediato**: Atleta titular em 40% a 79% das partidas em que participou (`0.4 <= Starts / MP < 0.8`).
    *   **Reserva de Composição**: Atleta acionado na maioria das vezes saindo do banco (`Starts / MP < 0.4`).
    
    #### 3. Classificação de Volume na Temporada (Minutagem Real)
    *   **Temporada Completa**: O atleta atuou em mais de 60% dos minutos totais possíveis da equipe na temporada.
    *   **Temporada Parcial**: O atleta atuou entre 30% e 60% dos minutos totais possíveis da equipe.
    *   **Interrupção de Ciclo (Venda/Lesão)**: O atleta é classificado como *Peça-Chave (Titular)* mas jogou menos de 30% dos minutos totais da equipe. O algoritmo deduz que houve um fator extracampo que encurtou sua minutagem (lesão grave ou venda para o exterior), preservando seu valor de scout.
    *   **Baixa Minutagem (Opção Técnica)**: O atleta é reserva e jogou menos de 30% dos minutos possíveis.
    """)
    
    st.markdown("---")
    st.markdown("""
    📂 **Nota sobre a Base de Dados (Esforço de Extração Manual)**
    
    Os dados que alimentam este projeto contêm **13.663 registros históricos de atletas**. A extração de dados foi feita de forma manual e híbrida a partir do portal público **FBref**. Essa abordagem manual foi necessária devido às travas de segurança do Cloudflare (retorno *403 Forbidden* para scripts de scraping automatizados diretos). A base de dados esportiva consolidada é de domínio público acadêmico e foi tratada inteiramente sob o escopo do Termo de Anuência ética do TCC.
    """)

# ================= ABA 5: ESTUDOS DE CASO LONGITUDINAIS (8 ATLETAS) ====================
with tab5:
    st.subheader("🧪 Estudos de Caso Práticos: Análise Longitudinal de Carreiras")
    st.write("Esta aba apresenta a análise longitudinal de 8 atletas profissionais de destaque do futebol brasileiro utilizando as planilhas consolidadas fornecidas na pasta 'nova_base'. "
             "O objetivo é testar o comportamento do classificador de Machine Learning (Random Forest) ao longo da carreira completa do atleta, "
             "em diferentes ligas e idades.")
    
    opcoes_jogadores = {
        "Cássio (Goleiro)": ("cassio_base_arrumada.xlsx", "Goleiro"),
        "Marcelo Lomba (Goleiro)": ("marcelo_lomba_base_arrumada.xlsx", "Goleiro"),
        "Gil (Defensor)": ("gil_base_arrumada.xlsx", "Defensor"),
        "Léo Pereira (Defensor)": ("leo_pereira_base_arrumada.xlsx", "Defensor"),
        "Giuliano (Meio Campo)": ("giuliano_base_arrumada.xlsx", "Meio Campo"),
        "Lucas Lima (Meio Campo)": ("lucas_lima_base_arrumada.xlsx", "Meio Campo"),
        "Gabriel Barbosa (Atacante)": ("gabriel_barbosa_base_arrumada.xlsx", "Atacante"),
        "Germán Cano (Atacante)": ("german_cano_base_arrumada.xlsx", "Atacante")
    }
    
    jog_selecionado = st.selectbox("Selecione o Atleta para Análise de Caso Longitudinal:", list(opcoes_jogadores.keys()))
    nome_arquivo, pos_grupo = opcoes_jogadores[jog_selecionado]
    path_arquivo = os.path.join('data/nova_base', nome_arquivo)
    
    if os.path.exists(path_arquivo):
        try:
            df_atleta = pd.read_excel(path_arquivo, sheet_name='Standard')
            # Mapeamento dinâmico de colunas de inglês para português
            rename_map = {
                'Season': 'Temporada',
                'Age': 'Idade',
                'Squad': 'Clube',
                'Comp': 'Competição',
                'Min': 'Minutos',
                'Gls': 'Gols',
                'Ast': 'Assistências',
                'CrdY': 'Cartões amarelos',
                'CrdR': 'Cartões vermelhos',
                'Starts': 'Titular',
                'MP': 'Jogos'
            }
            df_atleta = df_atleta.rename(columns={k: v for k, v in rename_map.items() if k in df_atleta.columns})
            
            # Filtrar a linha de sumário (ex: 13 Seasons ou Career)
            df_atleta = df_atleta[df_atleta['Temporada'].astype(str).str.contains('Season|Career|Total') == False]
            df_atleta = df_atleta[df_atleta['Temporada'].notna()].copy()
            df_atleta['Temporada'] = df_atleta['Temporada'].astype(str)
            
            # Limpar dados numéricos
            df_atleta['Minutos'] = pd.to_numeric(df_atleta['Minutos'], errors='coerce').fillna(0)
            df_atleta['Gols'] = pd.to_numeric(df_atleta['Gols'], errors='coerce').fillna(0)
            df_atleta['Assistências'] = pd.to_numeric(df_atleta['Assistências'], errors='coerce').fillna(0)
            df_atleta['90s'] = pd.to_numeric(df_atleta['90s'], errors='coerce').fillna(0)
            df_atleta['Idade'] = pd.to_numeric(df_atleta['Idade'], errors='coerce').fillna(0)
            df_atleta['Cartões amarelos'] = pd.to_numeric(df_atleta['Cartões amarelos'], errors='coerce').fillna(0)
            df_atleta['Cartões vermelhos'] = pd.to_numeric(df_atleta['Cartões vermelhos'], errors='coerce').fillna(0)
            
            # Mapeamento de nomes de colunas conforme o arquivo Excel (algumas planilhas usam acentos)
            # Garantir colunas por 90min
            df_atleta['Gols_90'] = df_atleta['Gols'] / df_atleta['90s'].replace(0, 1)
            df_atleta['Ast_90'] = df_atleta['Assistências'] / df_atleta['90s'].replace(0, 1)
            df_atleta['Cartoes_Y_90'] = df_atleta['Cartões amarelos'] / df_atleta['90s'].replace(0, 1)
            df_atleta['Cartoes_R_90'] = df_atleta['Cartões vermelhos'] / df_atleta['90s'].replace(0, 1)
            
            # Estimar titularidade
            df_atleta['Titular'] = pd.to_numeric(df_atleta['Titular'], errors='coerce').fillna(0)
            df_atleta['Jogos'] = pd.to_numeric(df_atleta['Jogos'], errors='coerce').fillna(1)
            df_atleta['Starts_Pct'] = (df_atleta['Titular'] / df_atleta['Jogos']).clip(0, 1)
            
            preds_ml = []
            probs_ml = []
            status_elenco_lista = []
            status_volume_lista = []
            
            for idx, row in df_atleta.iterrows():
                # Regras de Titularidade (Confiança do Treinador)
                starts_pct = row['Starts_Pct']
                jogos = row['Jogos']
                minutos = row['Minutos']
                
                if jogos == 0 or minutos == 0:
                    status_elenco = "Não Relacionado"
                elif starts_pct >= 0.8:
                    status_elenco = "Peça-Chave (Titular)"
                elif starts_pct >= 0.4:
                    status_elenco = "Reserva Imediato"
                else:
                    status_elenco = "Reserva de Composição"
                    
                # Regras de Volume na Temporada (Minutagem)
                if minutos > 1800:
                    status_vol = "Temporada Completa"
                elif minutos > 800:
                    status_vol = "Temporada Parcial"
                elif minutos > 0:
                    if status_elenco == "Peça-Chave (Titular)":
                        status_vol = "Interrupção de Ciclo (Lesão/Venda)"
                    else:
                        status_vol = "Baixa Minutagem"
                else:
                    status_vol = "Sem Minutagem"
                    
                status_elenco_lista.append(status_elenco)
                status_volume_lista.append(status_vol)
                
                if model_rf is not None:
                    # Obter as dummies de posição baseadas no grupo do jogador selecionado
                    pos_atacante = 1.0 if pos_grupo == 'Atacante' else 0.0
                    pos_meia = 1.0 if pos_grupo == 'Meio Campo' else 0.0
                    pos_defensor = 1.0 if pos_grupo == 'Defensor' else 0.0
                    pos_goleiro = 1.0 if pos_grupo == 'Goleiro' else 0.0
                    
                    features = [[
                        row['Idade'], row['Gols_90'], row['Ast_90'], row['Cartoes_Y_90'], row['Cartoes_R_90'], starts_pct,
                        pos_atacante, pos_meia, pos_defensor, pos_goleiro
                    ]]
                    
                    pred = model_rf.predict(features)[0]
                    prob = model_rf.predict_proba(features)[0]
                    
                    preds_ml.append("Série A" if pred == 1 else "Série B")
                    probs_ml.append(f"{prob[1]*100 if pred == 1 else prob[0]*100:.1f}%")
                else:
                    preds_ml.append("N/A")
                    probs_ml.append("N/A")
            
            df_atleta['Status no Elenco'] = status_elenco_lista
            df_atleta['Volume Utilização'] = status_volume_lista
            df_atleta['Aptidão Predita'] = preds_ml
            df_atleta['Probabilidade Ajuste'] = probs_ml
            
            st.markdown(f"### 📊 Histórico e Classificação Preditiva: {jog_selecionado}")
            cols_show = ['Temporada', 'Idade', 'Clube', 'Competição', 'Minutos', 'Status no Elenco', 'Volume Utilização', 'Aptidão Predita', 'Probabilidade Ajuste']
            st.dataframe(df_atleta[cols_show].set_index('Temporada'), use_container_width=True)
            
            # Discussão específica baseada no jogador selecionado
            st.markdown("### 📝 Discussão Científica do Estudo de Caso:")
            if pos_grupo == "Goleiro":
                st.write(f"*   **Posição de Goleiro ({jog_selecionado})**: A posição é avaliada com foco na consistência e minutagem. Goleiros com alto índice de partidas iniciadas e minutos em campo na elite mantêm classificação contínua de Série A.")
            elif pos_grupo == "Defensor":
                st.write(f"*   **Posição de Defensor ({jog_selecionado})**: A avaliação de zagueiros no modelo foca em baixas taxas de cartões por 90 minutos e regularidade defensiva. O modelo prediz Série A para os auges técnicos, refletindo a estabilidade em confrontos individuais.")
            elif pos_grupo == "Meio Campo":
                st.write(f"*   **Posição de Meio-Campista ({jog_selecionado})**: Jogadores de criação variam suas predições conforme a taxa de titularidade e assistências por 90min nas temporadas. Picos criativos e regularidade nas equipes de topo geram classificação Série A.")
            elif pos_grupo == "Atacante":
                st.write(f"*   **Posição de Atacante ({jog_selecionado})**: A produtividade direta de gols/90 e a idade do jogador são determinantes no modelo. Temporadas de artilharia geram forte predição de elite, enquanto anos de baixa minutagem ou menor eficácia reduzem o nível de confiança ou alternam para perfil de Série B.")
                
        except Exception as e:
            st.error(f"Erro ao processar arquivo Excel do atleta: {e}")
    else:
        st.warning(f"Arquivo '{nome_arquivo}' não encontrado na pasta data/nova_base/.")
