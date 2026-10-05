import os
from fpdf import FPDF

def clean_txt(s):
    return s.replace('–', '-').replace('—', '-').replace('“', '"').replace('”', '"').replace('’', "'").replace('¹', '1').replace('²', '2').replace('ª', 'a').replace('º', 'o')

class TurnitinPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(100, 116, 139)
            self.cell(0, 8, clean_txt("MBA Data Science & Analytics (Poli/USP) - Trabalho de Conclusão de Curso"), border=False, align="L")
            self.ln(4)
            self.set_draw_color(203, 213, 225)
            self.line(10, 14, 200, 14)
            self.ln(6)

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(100, 116, 139)
            self.cell(0, 10, clean_txt(f"Página {self.page_no()} | Autor: Felipe Santos de Jesus | POLI-USP"), border=False, align="C")

def build_pdf():
    pdf = TurnitinPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    epw = pdf.epw
    
    # ---------------- TÍTULO E AUTORIA ----------------
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(epw, 7, clean_txt("Sistema preditivo de scouting esportivo: avaliação de aptidão divisional de jogadores de futebol no Campeonato Brasileiro usando aprendizado de máquina"), align="C")
    pdf.ln(4)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(epw, 5, clean_txt("Felipe Santos de Jesus1*; Profa. Flávia Priscila Dantas2"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(epw, 4, clean_txt("1 Escola Politécnica da Universidade de São Paulo (POLI-USP). Aluno do Programa de MBA em Data Science & Analytics para Operações."), align="L")
    pdf.multi_cell(epw, 4, clean_txt("2 Escola Politécnica da Universidade de São Paulo (POLI-USP). Orientadora do Programa de MBA em Data Science & Analytics para Operações."), align="L")
    pdf.cell(epw, 4, clean_txt("*autor correspondente: felipesjh@gmail.com"), align="L", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # ---------------- RESUMO E PALAVRAS-CHAVE ----------------
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(epw, 6, clean_txt("Resumo"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9.5)
    p_resumo = (
        "O processo de recrutamento no futebol profissional contemporâneo envolve riscos financeiros elevados e tradicionalmente baseou-se em análises subjetivas de olheiros. "
        "Este trabalho desenvolveu um sistema preditivo fundamentado em Aprendizado de Máquina para avaliar a aptidão divisional de jogadores para as Séries A e B do Campeonato Brasileiro, "
        "atuando como ferramenta de mitigação de risco financeiro. Consolidou-se um banco de dados com 13.663 registros históricos de atletas (temporadas de 2010 a 2024), extraídos do portal FBref. "
        "Após a aplicação de filtro de minutagem mínima (>= 300 minutos, retendo 8.752 registros qualificados), engenharia de atributos para a normalização de métricas por 90 minutos (/90) e padronização Z-Score via StandardScaler, "
        "estruturou-se a validação dos modelos sob o paradigma temporal Out-of-Time (treinamento com dados de 2010-2020 e teste com dados de 2021-2024). Avaliaram-se os algoritmos de Regressão Logística, Random Forest e Gradient Boosting posicional. "
        "O modelo Gradient Boosting Posicional alcançou F1-Score de 0,8600 para Atacantes de Área (Acurácia 85,90%) e 0,8350 para Goleiros (Acurácia 83,80%, ROC-AUC 0,9130). "
        "Demonstrou-se empiricamente que a ausência de normalização provoca o colapso catastrófico de gradiente na Regressão Logística (0,00% de Precisão e Recall). "
        "Justificou-se o escopo tático pelas limitações de variáveis macro para Defensores e Meias. Validou-se qualitativamente a utilidade da solução por estudos de caso longitudinais de oito atletas e pela implantação em um Web-App interativo em Streamlit."
    )
    pdf.multi_cell(epw, 4.8, clean_txt(p_resumo), align="J")
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.cell(epw, 5, clean_txt("Palavras-chave: Inteligência Artificial; Mineração de Dados; Validação Temporal; Estatísticas Esportivas; Scouting de Futebol."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # ---------------- ABSTRACT E KEYWORDS ----------------
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(epw, 6, clean_txt("Abstract"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9.5)
    p_abstract = (
        "The player recruitment process in contemporary professional football involves high financial risks and has traditionally relied on subjective scout evaluations. "
        "This work developed a machine learning-based predictive system to assess player divisional suitability for Series A and B of the Brazilian National Championship as a tool for financial risk mitigation. "
        "A database of 13,663 historical player-season records (2010-2024 seasons) was compiled from the FBref portal. Following play-time filtering (>= 300 minutes, retaining 8,752 qualified records), "
        "feature engineering per 90 minutes (/90), and Z-Score standardization via StandardScaler, model validation was structured under an Out-of-Time temporal framework (training on 2010-2020 and testing on 2021-2024). "
        "Logistic Regression, Random Forest, and Position-Specialized Gradient Boosting algorithms were evaluated. The Positional Gradient Boosting model achieved a weighted F1-Score of 0.8600 for Forwards (85.90% Accuracy) and 0.8350 for Goalkeepers (83.80% Accuracy, ROC-AUC 0.9130). "
        "It was empirically proven that unscaled Logistic Regression suffers catastrophic gradient collapse (0.00% Precision and Recall). The tactical scope was justified due to macro-feature limitations for Defenders and Midfielders. "
        "The practical utility of the solution was qualitatively verified through longitudinal career case studies of eight players and deployed via an interactive Streamlit web application."
    )
    pdf.multi_cell(epw, 4.8, clean_txt(p_abstract), align="J")
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.cell(epw, 5, clean_txt("Keywords: Artificial Intelligence; Data Mining; Temporal Validation; Sports Statistics; Football Scouting."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # ---------------- INTRODUÇÃO ----------------
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(epw, 6, clean_txt("Introdução"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9.5)
    p_intro = (
        "O mercado internacional do futebol movimenta anualmente dezenas de bilhões de dólares em transações de direitos federativos, salários e direitos comerciais de transmissão de mídia. "
        "No cenário brasileiro contemporâneo, a promulgação da Lei n 14.193/2021 viabilizou a constituição da Sociedade Anônima do Futebol (SAF), provocando uma transição sem precedentes nos clubes nacionais. "
        "Sob essa nova perspectiva corporativa, a governança financeira, a eficiência na alocação de recursos e o retorno sobre o investimento (ROI) tornaram-se métricas de sobrevivência institucional.\n\n"
        "Diante dessas condições de risco, a Ciência de Dados aplicada ao scouting esportivo atua como uma ferramenta analítica de mitigação de risco corporativo de extrema relevância (SAYAN; HANÇER, 2022). "
        "Este trabalho adota a validação temporal Out-of-Time (Treino 2010-2020, Teste cego 2021-2024), justifica a escolha de modelos tabulares interpretáveis (GRINSZTAJN et al., 2022) e delimita o escopo às Séries A e B (2010-2024). "
        "O objetivo geral consiste em desenvolver, avaliar e implantar um sistema preditivo para estimar a aptidão divisional de jogadores de futebol, servindo de suporte quantitativo ao recrutamento profissional."
    )
    pdf.multi_cell(epw, 4.8, clean_txt(p_intro), align="J")
    pdf.ln(6)

    # ---------------- MATERIAL E MÉTODOS ----------------
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(epw, 6, clean_txt("Material e Métodos ou Método"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9.5)
    p_metodo = (
        "A pesquisa classifica-se como Aplicada, Quantitativa, Exploratorio-Descritiva, Documental e de Implementacao de Algoritmo. "
        "A base consolidada (13.663 registros) passou por filtro de corte minimo de 300 minutos (retendo 8.752 registros) e padronizacao Z-Score via StandardScaler. "
        "Para garantir rigor estatistico contra vazamento de dados (data leakage), a validacao foi conduzida estritamente no paradigma temporal Out-of-Time (Treino 2010-2020, Teste cego 2021-2024).\n\n"
        "1. Buscador Preditivo SAD e Taxonomia Tripartida:\n"
        "O modelo Gradient Boosting Posicional estima a probabilidade P(Serie A) de cada atleta. A classificacao final adota taxonomia tripartida: "
        "(a) Titular de Elite (Serie A) para P >= 75%; (b) Reserva Qualificado (Serie A) para 50% <= P < 75%; e (c) Inapto (Nem Titular nem Reserva de Serie A) para P < 50%.\n\n"
        "2. Simulador Tecnico ('What-If') e Formula de Similaridade (Scouting Match):\n"
        "Para identificar atletas reais com estatisticas semelhantes ao perfil simulado nos sliders, o sistema calcula a Distancia Euclidiana Normalizada Ponderada (Dj):\n"
        "Dj = sum(wi * |Xi,atleta - Xi,simulado| / sigma_i)\n\n"
        "Os pesos das variaveis (wi) refletem a prioridade tatica posicional:\n"
        "- Atacantes / Meio-Campistas: w_gols = 3,0 (produtividade), w_ast = 1,5 (criacao), w_starts = 1,0 (titularidade), w_min = 1,0 (volume), w_idade = 0,5.\n"
        "- Goleiros: w_gols_sofridos = 3,0 (solidez defensiva), w_starts = 1,0, w_min = 1,0, w_idade = 0,5.\n"
        "- Defensores: w_cartoes_amarelos = 2,0 (disciplina/risco), w_gols_sofridos = 2,0, w_starts = 1,0, w_min = 1,0, w_idade = 0,5.\n\n"
        "A similaridade percentual e obtida por: Similaridade (%) = max(50%, 100% - Dj * 15%)."
    )
    pdf.multi_cell(epw, 4.8, clean_txt(p_metodo), align="J")
    pdf.ln(4)

    # Tabela ABNT FPDF
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(242, 242, 242)
    pdf.cell(48, 5.5, clean_txt("Etapa de Processamento"), border=1, fill=True, align="C")
    pdf.cell(78, 5.5, clean_txt("Descrição Operacional"), border=1, fill=True, align="C")
    pdf.cell(32, 5.5, clean_txt("Volume (N)"), border=1, fill=True, align="C")
    pdf.cell(32, 5.5, clean_txt("Percentual (%)"), border=1, fill=True, align="C", new_x="LMARGIN", new_y="NEXT")
    
    t2_rows = [
        ("Registros Originais Brutos", "Atletas-Temporada consolidados (2010-2024)", "13.663", "100,0%"),
        ("Filtro de Descarte (Min < 300)", "Registros de amostragem insignificante", "4.911", "35,9% (Removidos)"),
        ("Base Final Qualificada", "Base tratada com significância estatística", "8.752", "64,1% (Retidos)"),
        ("Treinamento Out-of-Time", "Dados históricos (2010 a 2020)", "4.849", "35,5% do total"),
        ("Teste Independente Cego", "Dados futuros Out-of-Time (2021 a 2024)", "3.903", "28,6% do total")
    ]
    pdf.set_font("Helvetica", "", 8)
    for r in t2_rows:
        pdf.cell(48, 5, clean_txt(r[0]), border=1)
        pdf.cell(78, 5, clean_txt(r[1]), border=1)
        pdf.cell(32, 5, clean_txt(r[2]), border=1, align="C")
        pdf.cell(32, 5, clean_txt(r[3]), border=1, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # ---------------- RESULTADOS E DISCUSSÃO ----------------
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(epw, 6, clean_txt("Resultados e Discussão"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9.5)
    pdf.multi_cell(epw, 4.8, clean_txt("A Tabela 4 resume o desempenho comparativo dos modelos no conjunto de teste cego Out-of-Time (2021-2024):"), align="J")
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(242, 242, 242)
    pdf.cell(50, 5.5, clean_txt("Modelo / Posição"), border=1, fill=True, align="C")
    pdf.cell(45, 5.5, clean_txt("Pipeline"), border=1, fill=True, align="C")
    pdf.cell(22, 5.5, clean_txt("Acurácia"), border=1, fill=True, align="C")
    pdf.cell(22, 5.5, clean_txt("Precisão"), border=1, fill=True, align="C")
    pdf.cell(22, 5.5, clean_txt("Recall"), border=1, fill=True, align="C")
    pdf.cell(29, 5.5, clean_txt("F1-Weighted / AUC"), border=1, fill=True, align="C", new_x="LMARGIN", new_y="NEXT")
    
    t4_rows = [
        ("LogReg (Sem Scaler - Genérico)", "Dados Brutos", "50,65%", "0,00%", "0,00%", "0,3406 / N/A"),
        ("LogReg (Sem Scaler - Goleiro)", "Dados Brutos", "81,90%", "0,00%", "0,00%", "0,7376 / N/A"),
        ("LogReg (Sem Scaler - Atacante)", "Dados Brutos", "78,19%", "56,00%", "20,59%", "0,7408 / N/A"),
        ("Genérico (Com Scaler)", "LogReg + StandardScaler", "53,34%", "53,50%", "41,69%", "0,5271 / 0.5355"),
        ("Genérico (Com Scaler)", "RandForest + StandardScaler", "74,80%", "72,10%", "71,50%", "0,7480 / 0.8120"),
        ("SAD Atacante (GradBoost)", "GradBoost + StandardScaler", "85,90%", "81,20%", "78,40%", "0,8600 / 0.8710"),
        ("SAD Goleiro (GradBoost)", "GradBoost + StandardScaler", "83,80%", "79,50%", "74,10%", "0,8350 / 0.9130")
    ]
    pdf.set_font("Helvetica", "", 8)
    for r in t4_rows:
        pdf.cell(50, 5, clean_txt(r[0]), border=1)
        pdf.cell(45, 5, clean_txt(r[1]), border=1)
        pdf.cell(22, 5, clean_txt(r[2]), border=1, align="C")
        pdf.cell(22, 5, clean_txt(r[3]), border=1, align="C")
        pdf.cell(22, 5, clean_txt(r[4]), border=1, align="C")
        pdf.cell(29, 5, clean_txt(r[5]), border=1, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # ---------------- CONCLUSÃO ----------------
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(epw, 6, clean_txt("Conclusão ou Considerações Finais"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9.5)
    pdf.multi_cell(epw, 4.8, clean_txt("O sistema preditivo desenvolvido cumpriu os objetivos propostos ao mapear a aptidão divisional para as Séries A e B do futebol brasileiro, entregando os resultados em um Web-App interativo em Streamlit (app/app.py). A normalização via StandardScaler é requisito indispensável para evitar o colapso de gradiente. O filtro de 300 minutos eliminou o ruído de pequenas amostras e a especialização posicional elevou o F1-Score para 0,8600 em Atacantes e 0,8350 em Goleiros."), align="J")
    pdf.ln(6)

    # ---------------- REFERÊNCIAS ----------------
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(epw, 6, clean_txt("Referências"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8.5)
    refs = [
        "CARLING, C. et al. The Role of Motion Analysis in Elite Soccer. Sports Medicine, v. 38, n. 10, p. 839-862, 2008.",
        "GRINSZTAJN, L. et al. Why Do Tree-Based Models Still Outperform Deep Learning on Typical Tabular Data? NeurIPS 35, 2022.",
        "HUGHES, M.; FRANKS, I. M. Essentials of Performance Analysis in Sport. 3. ed. London: Routledge, 2019.",
        "MEMMERT, D.; RAABE, D. Data Analytics in Football: Positional Data Collection, Modelling and Analysis. London: Routledge, 2018.",
        "SAYAN, V. H.; HANÇER, E. A Survey on Football Player Performance Estimation Using Machine Learning. MAKU Techno-Science, 2022.",
        "TANG, Q. et al. The Role of Machine Learning in Talent Identification for Team Sports. JSSM, v. 25, p. 58-83, 2026.",
        "VILELA, T. et al. Towards a Pervasive Intelligent System on Football Scouting. Springer, AISC, v. 747, p. 341-351, 2018."
    ]
    for r in refs:
        pdf.multi_cell(epw, 4, clean_txt(r), align="L")
        pdf.ln(1)
        
    pdf.ln(4)

    # ---------------- APÊNDICES E ANEXOS ----------------
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(epw, 6, clean_txt("Apêndice(s) e Anexo(s)"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(epw, 5, clean_txt("Apêndice A. Repositório de Código-Fonte e Execução da Aplicação"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8.5)
    pdf.multi_cell(epw, 4, clean_txt("Código-fonte público disponível no GitHub: https://github.com/felipesjh/analise-aptidao-futebol-tcc.git"), align="L")
    pdf.ln(2)
    
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(epw, 5, clean_txt("Anexo A. Relatórios e Certificados do Turnitin (Espaço Reservado)"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8.5)
    pdf.multi_cell(epw, 4, clean_txt("(Espaço reservado para inserção da folha de aprovação do Turnitin e índice de similaridade gerado pela Secretaria Acadêmica da Poli/USP)."), align="L")

    out_file_v2 = "[Turnitin - Trabalho Final v2]  - Felipe  Santos De Jesus.pdf"
    out_file_v3 = "[Turnitin - Trabalho Final v3]  - Felipe  Santos De Jesus.pdf"
    pdf.output(out_file_v2)
    pdf.output(out_file_v3)
    print(f"PDF Versão 2 e Versão 3 gerados com sucesso via FPDF2 em: {out_file_v3}")

if __name__ == '__main__':
    build_pdf()
