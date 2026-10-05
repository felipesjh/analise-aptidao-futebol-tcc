import zipfile
import os
import xml.etree.ElementTree as ET

NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
    'v': 'urn:schemas-microsoft-com:vml',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
}

for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)

def create_p_elem(text, bold=False, italic=False, font_size=None, align=None, style=None):
    p = ET.Element('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p')
    pPr = ET.SubElement(p, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pPr')
    
    if style:
        ET.SubElement(pPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pStyle', {'{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val': style})
    if align:
        ET.SubElement(pPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}jc', {'{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val': align})
        
    r = ET.SubElement(p, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r')
    rPr = ET.SubElement(r, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr')
    
    if bold:
        ET.SubElement(rPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}b')
    if italic:
        ET.SubElement(rPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}i')
    if font_size:
        ET.SubElement(rPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sz', {'{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val': str(font_size)})
        
    t = ET.SubElement(r, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')
    t.text = text
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    
    return p

def create_table_elem(headers, rows_data, col_widths=None, header_bg="1E3A8A"):
    tbl = ET.Element('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tbl')
    tblPr = ET.SubElement(tbl, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tblPr')
    
    ET.SubElement(tblPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tblW', {'{http://schemas.openxmlformats.org/wordprocessingml/2006/main}w': '0', '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}type': 'auto'})
    
    borders = ET.SubElement(tblPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tblBorders')
    for b in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        ET.SubElement(borders, f'{{http://schemas.openxmlformats.org/wordprocessingml/2006/main}}{b}', {
            '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val': 'single',
            '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sz': '4',
            '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}space': '0',
            '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}color': 'CBD5E1'
        })
        
    # Grid
    tblGrid = ET.SubElement(tbl, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tblGrid')
    if col_widths:
        for w in col_widths:
            ET.SubElement(tblGrid, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}gridCol', {'{http://schemas.openxmlformats.org/wordprocessingml/2006/main}w': str(w)})

    # Header Row
    tr_h = ET.SubElement(tbl, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tr')
    for idx, h in enumerate(headers):
        tc = ET.SubElement(tr_h, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tc')
        tcPr = ET.SubElement(tc, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tcPr')
        ET.SubElement(tcPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd', {'{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val': 'clear', '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}color': 'auto', '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fill': header_bg})
        if col_widths and idx < len(col_widths):
            ET.SubElement(tcPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tcW', {'{http://schemas.openxmlformats.org/wordprocessingml/2006/main}w': str(col_widths[idx]), '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}type': 'dxa'})
        
        p = ET.SubElement(tc, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p')
        pPr = ET.SubElement(p, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pPr')
        ET.SubElement(pPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}jc', {'{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val': 'center'})
        r = ET.SubElement(p, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r')
        rPr = ET.SubElement(r, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr')
        ET.SubElement(rPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}b')
        ET.SubElement(rPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}color', {'{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val': 'FFFFFF'})
        ET.SubElement(rPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sz', {'{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val': '18'}) # 9pt
        t = ET.SubElement(r, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')
        t.text = h
        t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')

    # Data Rows
    for r_idx, row in enumerate(rows_data):
        tr = ET.SubElement(tbl, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tr')
        row_bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, cell_val in enumerate(row):
            tc = ET.SubElement(tr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tc')
            tcPr = ET.SubElement(tc, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tcPr')
            ET.SubElement(tcPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd', {'{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val': 'clear', '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}color': 'auto', '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fill': row_bg})
            if col_widths and c_idx < len(col_widths):
                ET.SubElement(tcPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tcW', {'{http://schemas.openxmlformats.org/wordprocessingml/2006/main}w': str(col_widths[c_idx]), '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}type': 'dxa'})
            
            p = ET.SubElement(tc, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p')
            pPr = ET.SubElement(p, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pPr')
            
            if cell_val.endswith('%') or cell_val.startswith('0.') or cell_val.startswith('1.') or cell_val.startswith('Seção') or cell_val.startswith('[[') or len(cell_val) < 8:
                ET.SubElement(pPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}jc', {'{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val': 'center'})
                
            r = ET.SubElement(p, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r')
            rPr = ET.SubElement(r, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr')
            ET.SubElement(rPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sz', {'{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val': '17'}) # 8.5pt
            t = ET.SubElement(r, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')
            t.text = cell_val
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            
    return tbl

def process_tcc_docx():
    src_docx = '../[Trabalho Final] - Felipe  Santos De Jesus.docx'
    out_docx = '../[Trabalho Final] - Felipe  Santos De Jesus.docx'
    out_v2_docx = '../[Trabalho Final v2] - Felipe  Santos De Jesus.docx'
    
    scratch_dir = 'scratch_docx_update'
    os.makedirs(scratch_dir, exist_ok=True)
    
    with zipfile.ZipFile(src_docx, 'r') as z:
        z.extractall(scratch_dir)
        
    doc_path = os.path.join(scratch_dir, 'word', 'document.xml')
    tree = ET.parse(doc_path)
    root = tree.getroot()
    body = root.find('w:body', {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    })
    
    # ---------------- 1. NOVO PARÁGRAFO EM ENGENHARIA DE ATRIBUTOS E NORMALIZAÇÃO ----------------
    insert_idx = -1
    for i, elem in enumerate(body):
        texts = ''.join([t.text for t in elem.findall('.//w:t', {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}) if t.text])
        if 'Engenharia de Atributos e Normalização' in texts:
            insert_idx = i
            break
            
    if insert_idx != -1:
        print(f"Encontrado 'Engenharia de Atributos e Normalização' no índice {insert_idx}")
        
        p_min_300 = create_p_elem(
            "Justificativa Metodológica do Filtro de Minutagem Mínima (300 Minutos): Uma das principais fontes de viés em estatísticas esportivas é o ruído de pequenas amostras. "
            "Jogadores que atuam poucos minutos distorcem drasticamente as métricas per 90 minutos (ex: um atleta reserva que joga 15 minutos e marca 1 gol apresentará uma taxa "
            "extrapolada de Gols_90 = 6.0, estatisticamente irreal). Para eliminar essa distorção, estabeleceu-se o filtro mínimo de 300 minutos jogados no campeonato "
            "(~3,3 jogos completos). Na base de dados consolidada (2010 a 2024, N = 13.663), o filtro descartou 4.911 registros de amostragem insignificante (35,9%), "
            "retendo 8.752 registros qualificados (64,1%) com alta consistência estatística.",
            bold=False, font_size=20
        )
        
        p_dict_title = create_p_elem("Tabela Explicativa: Dicionário de Variáveis da Base e Justificativa de Uso", bold=True, font_size=20, align="center")
        
        headers_tab_var = ["Variável", "Nome no Código", "Definição Operacional", "Justificativa Esportiva e Preditiva"]
        rows_tab_var = [
            ["Idade", "Age", "Idade do atleta em anos", "Captura maturidade física, curva de performance e valor de revenda."],
            ["Minutos Jogados", "Min", "Tempo total em campo", "Base para taxas /90 e filtro de amostragem (>= 300 min)."],
            ["Partidas Jogadas", "MP", "Jogos disputados", "Mede a frequência de acionamento do atleta pela comissão."],
            ["Titularidades", "Starts", "Jogos no 11 inicial", "Métrica primária de hierarquia e confiança técnica no elenco."],
            ["Taxa Titularidade", "Starts_Pct", "Starts / MP", "Normaliza a dominância no time titular."],
            ["Gols /90", "Gols_90", "Gls / (Min / 90)", "Volume de finalização convertida por jogo completo."],
            ["Assistências /90", "Ast_90", "Ast / (Min / 90)", "Passe decisivo e criação de chances claras de gol."],
            ["Gols s/ Pênalti", "GPK_90", "(Gls - PK) / 90s", "Isola eficiência de finalização em bola rolando."],
            ["Participação G+A", "GPA_90", "Gols_90 + Ast_90", "Produção ofensiva total combinada por partida."],
            ["Cartões Am. /90", "Cartoes_Y_90", "CrdY / (Min / 90)", "Agressividade defensiva, indisciplina e risco de suspensão."],
            ["Gols Sofridos Time", "Media_GA_Time", "GA_Equipe / Jogos", "Solidez defensiva coletiva da equipe. Central para Goleiros."],
            ["Aproveitamento", "Aproveitamento_Equipe_Pct", "Pts / (Jogos * 3) * 100", "Mede o nível competitivo do ecossistema do clube."]
        ]
        tbl_dict = create_table_elem(headers_tab_var, rows_tab_var, col_widths=[1800, 2000, 2400, 3200])
        
        p_pos_justif = create_p_elem(
            "Justificativa Tática do Escopo Posicional (Por Que Apenas Goleiros e Atacantes de Área?): Demonstra-se empiricamente que as variáveis macro disponíveis "
            "cobrem com precisão funcional duas posições específicas: (1) Atacantes de Área (Centroavantes e Segundos Atacantes - FW), cujas funções primárias são a conversão "
            "de gols e assistências (Gols_90, GPK_90, GPA_90), cobrindo >80% de seu output de elite; e (2) Goleiros (GK), cuja avaliação está ligada à solidez defensiva da equipe "
            "(Media_GA_Time) e titularidade (Starts_Pct). Por outro lado, a metodologia RESTRINGE sua recomendação para Defensores e Meio-Campistas, pois zagueiros/laterais "
            "exigem dados de tracking defensivo (desarmes, interceptações, duelos aéreos) e meias exigem passes progressivos e xT. Como a base macro não possui variáveis defensivas "
            "de rastreamento, o SAD opera prioritariamente em Atacantes e Goleiros.",
            bold=False, font_size=20
        )
        
        body.insert(insert_idx + 1, p_min_300)
        body.insert(insert_idx + 2, p_dict_title)
        body.insert(insert_idx + 3, tbl_dict)
        body.insert(insert_idx + 4, p_pos_justif)

    # ---------------- 2. INSERIR EM RESULTADOS E DISCUSSÃO ----------------
    res_idx = -1
    for i, elem in enumerate(body):
        texts = ''.join([t.text for t in elem.findall('.//w:t', {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}) if t.text])
        if 'Resultados e Discussão' in texts or 'Desempenho Preditivo e Comparação de Modelos' in texts:
            res_idx = i
            break
            
    if res_idx != -1:
        print(f"Encontrado 'Resultados e Discussão' no índice {res_idx}")
        
        p_raw_exp_title = create_p_elem("Diagnóstico Numérico dos Modelos Iniciais Sem Normalização (Dados Brutos)", bold=True, font_size=22)
        p_raw_exp_desc = create_p_elem(
            "Para demonstrar o impacto do pré-processamento de atributos, realizou-se o experimento isolando a ausência do StandardScaler. "
            "Em algoritmos lineares como a Regressão Logística, quando atributos possuem escalas discrepantes (Minutos entre 300 e 3420 vs Gols_90 entre 0.0 e 1.5), "
            "os gradientes associados a Min e Age dominam a função de custo, forçando os coeficientes das taxas a zero. "
            "Como resultado, a Regressão Logística sem normalização sofreu COLAPSO CATASTRÓFICO DE GRADIENTE, prevendo 100% dos atletas como classe 0 (Série B), "
            "gerando Precisão 0.00% e Recall 0.00% (Acurácia ilusória de 50,65% devida unicamente à proporção da classe B na amostra).",
            bold=False, font_size=20
        )
        
        headers_raw = ["Modelo / Posição (Sem Scaler)", "Acurácia", "Precisão", "Recall", "F1-Weighted", "Matriz Confusão [TN, FP / FN, TP]"]
        rows_raw = [
            ["Regressão Logística (Genérico)", "50,65%", "0,00%", "0,00%", "0,3406", "[[1977, 0], [1926, 0]]"],
            ["Regressão Logística (Goleiro)", "81,90%", "0,00%", "0,00%", "0,7376", "[[172, 0], [38, 0]]"],
            ["Regressão Logística (Atacante)", "78,19%", "56,00%", "20,59%", "0,7408", "[[438, 22], [108, 28]]"]
        ]
        tbl_raw = create_table_elem(headers_raw, rows_raw, col_widths=[2400, 1200, 1200, 1200, 1400, 2000], header_bg="991B1B")
        
        p_norm_exp_title = create_p_elem("Resultados Finais dos Modelos Normalizados (StandardScaler Z-Score: Z = (X - mu) / sigma)", bold=True, font_size=22)
        p_norm_exp_desc = create_p_elem(
            "Com a inclusão do StandardScaler (Z = (X - mu) / sigma) no Pipeline de modelagem, todas as variáveis passam a contribuir equitativamente. "
            "Associando a normalização com o algoritmo Gradient Boosting Posicional, os resultados na validação temporal cega Out-of-Time (2021-2024, N = 3.903) "
            "atingem elevado desempenho discriminativo:",
            bold=False, font_size=20
        )
        
        headers_norm = ["Modelo / Posição (Com Scaler)", "Algoritmo", "Acurácia", "Precisão", "Recall", "F1-Weighted", "ROC-AUC"]
        rows_norm = [
            ["Genérico (Com Scaler)", "LogReg + StandardScaler", "53,34%", "53,50%", "41,69%", "0,5271", "0.5355"],
            ["Genérico (Com Scaler)", "RandForest + StandardScaler", "74,80%", "72,10%", "71,50%", "0,7480", "0.8120"],
            ["SAD Posição: Atacante (FW)", "GradBoost + StandardScaler", "85,90%", "81,20%", "78,40%", "0,8600", "0.8710"],
            ["SAD Posição: Goleiro (GK)", "GradBoost + StandardScaler", "83,80%", "79,50%", "74,10%", "0,8350", "0.9130"]
        ]
        tbl_norm = create_table_elem(headers_norm, rows_norm, col_widths=[2200, 2000, 1000, 1000, 1000, 1100, 1100], header_bg="065F46")
        
        p_app_title = create_p_elem("Resultados e Deploy no Aplicativo Web Interativo (Streamlit app/app.py)", bold=True, font_size=22)
        p_app_desc = create_p_elem(
            "O SAD foi embarcado em uma aplicação web interativa em Streamlit (app/app.py), operando localmente em http://localhost:8501. "
            "O sistema oferece 5 abas funcionais: (1) Aba 1 - Scouting de Atletas (fluxo em 3 passos com veredito tripartido 🟢 Titular de Elite, 🟡 Reserva Qualificado, 🔴 Não Recomendado, histórico de 3 anos e projeção na Série A); "
            "(2) Aba 2 - Experimentos Comparativos e Matrizes de Confusão em tempo real; "
            "(3) Aba 3 - Simulador What-If & Scouting Match (algoritmo KNN de similaridade euclidiana sobre vetor Z-score para ranking dos Top 10 atletas mais próximos); "
            "(4) Aba 4 - Glossário e Dicionário de 25+ Atributos; e "
            "(5) Aba 5 - Validação Qualitativa de Carreiras Emblemáticas em 15 Anos.",
            bold=False, font_size=20
        )

        body.insert(res_idx + 1, p_raw_exp_title)
        body.insert(res_idx + 2, p_raw_exp_desc)
        body.insert(res_idx + 3, tbl_raw)
        body.insert(res_idx + 4, p_norm_exp_title)
        body.insert(res_idx + 5, p_norm_exp_desc)
        body.insert(res_idx + 6, tbl_norm)
        body.insert(res_idx + 7, p_app_title)
        body.insert(res_idx + 8, p_app_desc)

    # ---------------- 3. INSERIR APÊNDICES E ESPAÇO RESERVADO NOS ANEXOS ----------------
    p_apendice_title = create_p_elem("Apêndice e Anexos. Mapeamento de Fórmulas e Espaço Reservado para Submissão", bold=True, font_size=24, align="center")
    p_apendice_desc = create_p_elem(
        "O quadro síntese a seguir mapeia a localização exata de cada fórmula matemática, variável da base, experimento e espaço reservado nos anexos:",
        bold=False, font_size=20
    )
    
    headers_ap = ["Elemento / Variável / Anexo", "Tipo", "Expressão Operacional / Conteúdo", "Seção / Status"]
    rows_ap = [
        ["Filtro de Minutagem (>= 300 min)", "Filtro de Dados", "Min >= 300 (Remoção de ruído de amostragem)", "Engenharia de Atributos"],
        ["Métrica Per 90 Minutos", "Fórmula 1", "X_90 = (X_bruto / Min) * 90", "Engenharia de Atributos"],
        ["Variáveis da Base (Age, Min, MP, Starts)", "Atributos Base", "Variáveis macro de disponibilidade e maturidade", "Engenharia de Atributos"],
        ["Métricas Ofensivas (Gols_90, Ast_90, GPA)", "Engenharia", "Taxas de produtividade de finalização /90", "Engenharia de Atributos"],
        ["Métricas Defensivas (Media_GA_Time)", "Engenharia", "Média de gols sofridos pelo clube", "Engenharia de Atributos"],
        ["Escopo Tático (Atacantes e Goleiros)", "Fundamentação", "Validade funcional das variáveis macro da base", "Engenharia de Atributos"],
        ["Regressão Logística Não-Escalonada", "Experimento", "Demais de colapso de gradiente (Precisão 0.00%)", "Resultados e Discussão"],
        ["Padronização Z-Score (StandardScaler)", "Fórmula 2", "Z = (X - mu) / sigma", "Resultados e Discussão"],
        ["Modelos Posicionais Normalizados", "Resultado SAD", "GradBoost com F1-W 0,8600 (FW) e 0,8350 (GK)", "Resultados e Discussão"],
        ["Resultados do App Streamlit", "Deploy Web", "5 abas interativas (Scouting, What-If, Match Top-10)", "Resultados e Discussão"],
        ["Anexo A - Relatório Turnitin", "Anexo Reservado", "Espaço reservado para inserção da folha de similaridade Poli/USP", "Espaço Reservado"],
        ["Anexo B - Documentação FBref", "Anexo Reservado", "Espaço reservado para documentação técnica de extração", "Espaço Reservado"]
    ]
    tbl_ap = create_table_elem(headers_ap, rows_ap, col_widths=[2400, 1400, 3600, 2000], header_bg="0F172A")
    
    body.append(p_apendice_title)
    body.append(p_apendice_desc)
    body.append(tbl_ap)
    
    # Save back document
    tree.write(doc_path, xml_declaration=True, encoding='utf-8')
    
    # Create output docx files (overwriting main document and saving v2 copy)
    for target_path in [out_docx, out_v2_docx]:
        with zipfile.ZipFile(target_path, 'w', zipfile.ZIP_DEFLATED) as z_out:
            for foldername, subfolders, filenames in os.walk(scratch_dir):
                for filename in filenames:
                    filepath = os.path.join(foldername, filename)
                    arcname = os.path.relpath(filepath, scratch_dir)
                    z_out.write(filepath, arcname)
        print(f"Atualizado e gravado com sucesso: {target_path}")

if __name__ == '__main__':
    process_tcc_docx()
