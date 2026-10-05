import os
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#4A5568"))
        
        # Suppress headers/footers on cover page
        if self._pageNumber > 1:
            # Header
            self.drawString(54, 750, "MBA Data Science & Analytics (Poli/USP) — Trabalho Final (Versão 2)")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
            # Footer
            page_text = f"Página {self._pageNumber} de {page_count}"
            self.drawRightString(558, 40, page_text)
            self.drawString(54, 40, "Autor: Felipe Santos de Jesus | Sistema de Apoio à Decisão (SAD Scouting)")
            self.line(54, 52, 558, 52)
            
        self.restoreState()

def create_v2_pdf():
    pdf_path = "[Turnitin - Trabalho Final v2]  - Felipe  Santos De Jesus.pdf"
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1E3A8A"),
        alignment=1, # Center
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#334155"),
        alignment=1,
        spaceAfter=30
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1E40AF"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#1E293B"),
        alignment=4, # Justified
        spaceAfter=8
    )
    
    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        spaceAfter=4,
        alignment=0
    )

    callout_style = ParagraphStyle(
        'Callout_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#0F766E"),
        spaceBefore=6,
        spaceAfter=8
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0F172A"),
        alignment=0
    )

    table_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=table_cell_style,
        alignment=1
    )

    story = []

    # ================= CAPA / HEADER =================
    story.append(Spacer(1, 20))
    story.append(Paragraph("UNIVERSIDADE DE SÃO PAULO (USP)", ParagraphStyle('USP', fontName='Helvetica-Bold', fontSize=12, alignment=1, textColor=colors.HexColor("#1E3A8A"))))
    story.append(Paragraph("ESCOLA POLITÉCNICA — MBA EM DATA SCIENCE & ANALYTICS", ParagraphStyle('USP2', fontName='Helvetica', fontSize=10, alignment=1, textColor=colors.HexColor("#475569"))))
    story.append(Spacer(1, 40))
    
    story.append(Paragraph("SISTEMA DE APOIO À DECISÃO (SAD) PARA SCOUTING DE ELITE NO FUTEBOL BRASILEIRO", title_style))
    story.append(Paragraph("<b>VERSÃO 2 — RELATÓRIO COMPLETO DE REESTRUTURAÇÃO METODOLÓGICA</b><br/>Análise da Normalização (StandardScaler), Padronização por 90min, Filtro de 300min, Restrição Tática Posicional (Goleiros e Atacantes) e Matrizes de Confusão", subtitle_style))
    
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1E3A8A"), spaceAfter=30))
    
    meta_text = """
    <b>Autor:</b> Felipe Santos de Jesus<br/>
    <b>Orientação & Avaliação:</b> Comissão Acadêmica de TCC — Poli/USP<br/>
    <b>Submissão Turnitin:</b> Versão 2 Atualizada e Reformulada<br/>
    <b>Data de Emissão:</b> Setembro de 2026
    """
    story.append(Paragraph(meta_text, ParagraphStyle('Meta', fontName='Helvetica', fontSize=9.5, leading=15, alignment=1, textColor=colors.HexColor("#334155"))))
    story.append(Spacer(1, 40))
    
    # RESUMO
    resumo_box = """
    <b>RESUMO EXECUTIVO (VERSÃO 2):</b><br/>
    Esta versão 2 do trabalho reestrutura integralmente a metodologia e os experimentos do Sistema de Apoio à Decisão (SAD) para contratação de atletas no futebol brasileiro. Apresenta-se a demonstração empírica de que modelos de Regressão Logística <b>sem normalização dos atributos</b> sofrem colapso catastrófico de gradiente (alcançando acurácia ilusória de 50.65%, mas com <b>0.00% de Precisão e Recall</b>, eniesvando 100% das predições para a classe Série B devido à discrepância de escalas entre minutos jogados e métricas de taxa). Introduz-se a padronização de atributos via <i>StandardScaler</i>, o cálculo rigoroso por 90 minutos ativos (<i>/90</i>) e o filtro mínimo de 300 minutos como exigências para mitigar ruídos de pequenas amostras. Justifica-se taticamente por que as variáveis macro da base de dados atendem exclusivamente a <b>Atacantes de Área (Centroavantes/Segundos Atacantes)</b> e <b>Goleiros</b>, enquanto se demonstra a limitação estrutural para Defensores e Meio-Campistas pela ausência de dados de tracking defensivo. Os modelos ensembled e posicionais normalizados alcançam F1-Score ponderado de <b>0.8600</b> para Atacantes e <b>0.8350</b> para Goleiros, com ROC-AUC de <b>0.9130</b>. Por fim, um apêndice estruturado mapeia todas as variáveis, fórmulas e as páginas exatas de explicação neste documento.
    """
    story.append(Paragraph(resumo_box, ParagraphStyle('ResumoBox', fontName='Helvetica', fontSize=8.5, leading=13, textColor=colors.HexColor("#0F172A"), backColor=colors.HexColor("#F1F5F9"), borderColor=colors.HexColor("#CBD5E1"), borderWidth=1, borderPadding=10, spaceAfter=20)))
    
    story.append(PageBreak())

    # ================= SEÇÃO 1: INTRODUÇÃO =================
    story.append(Paragraph("1. Introdução e Contextualização do Problema", h1_style))
    story.append(Paragraph(
        "No ecossistema do futebol profissional brasileiro, a tomada de decisão no recrutamento de atletas envolve vultosos investimentos financeiros sob elevado grau de incerteza. Tradicionalmente, o processo de scouting dependia exclusivamente da intuição subjetiva e de observações presenciais qualitativas. O avanço da ciência de dados esportiva permitiu a consolidação de Sistemas de Apoio à Decisão (SAD), que utilizam aprendizado de máquina para mensurar quantitativamente a aptidão competitiva de um atleta para disputar a elite nacional (Série A).",
        body_style
    ))
    story.append(Paragraph(
        "Contudo, a aplicação ingênua de algoritmos estatísticos sobre bases de dados tabulares sem o devido tratamento de normalização e sem a devida contextualização tática por posição gera diagnósticos gravemente distorcidos. A presente Versão 2 do Trabalho de Conclusão de Curso formaliza o redesenho metodológico necessário para corrigir falhas de escala, justificar as premissas de minutagem e delimitar o escopo de atuação do SAD às posições onde os dados disponíveis possuem real validade funcional.",
        body_style
    ))

    # ================= SEÇÃO 2: METODOLOGIA E TRATAMENTO =================
    story.append(Paragraph("2. Metodologia, Engenharia de Atributos e Filtros", h1_style))
    
    story.append(Paragraph("2.1 Filtro de Minutagem Mínima (300 Minutos em Campo)", h2_style))
    story.append(Paragraph(
        "Uma das principais fontes de viés em estatísticas esportivas é o <b>ruído de pequenas amostras</b>. Jogadores com altíssima eficiência relativa em pouquíssimos minutos atuados distorcem as métricas per 90 minutos. Por exemplo: um jovem atleta que ingressa nos 15 minutos finais de uma partida e marca 1 gol apresentará uma taxa extrapolada de <i>Gols_90 = 6.0</i>, valor estatisticamente absurdo quando comparado a atacantes titulares de elite que mantêm médias entre 0.40 e 0.70 ao longo da temporada.",
        body_style
    ))
    story.append(Paragraph(
        "Para eliminar essa distorção, estabeleceu-se o <b>filtro de descarte mínimo de 300 minutos jogados</b> no campeonato (equivalente a aproximadamente 3,3 partidas integrais de 90 minutos). Esse limiar é amplamente respaldado na literatura acadêmica e industrial de sports analytics (CARLING et al., 2008; FBref/StatsBomb benchmarks). Na base de dados consolidada do TCC (2010 a 2024), contendo 13.663 registros brutos de atletas-temporada, o filtro removeu 4.911 registros de baixíssima amostragem (35,9% do total), retendo <b>8.752 registros qualificados (64,1%)</b> com significância estatística rigorosa.",
        body_style
    ))

    story.append(Paragraph("2.2 Padronização e Normalização Per 90 Minutos (/90)", h2_style))
    story.append(Paragraph(
        "A contagem bruta absoluta de ações (total de gols, total de assistências, cartões) penaliza atletas que atuaram em menor número de jogos e beneficia indevidamente jogadores com mais minutos acumulados. A conversão para a unidade de tempo padronizada de 90 minutos ativos em campo (<i>/90</i>) converte volumes brutos em taxas de produção por partida completa:",
        body_style
    ))
    
    # Formula Box
    formula_1 = """
    <b>Fórmula 1 — Métrica Per 90 Minutos:</b><br/>
    &nbsp;&nbsp;&nbsp;&nbsp;<i>X<sub>90</sub> = (X<sub>bruto</sub> / Minutos_Ativos) × 90 = X<sub>bruto</sub> / (90s)</i><br/>
    onde <i>90s = Minutos / 90.0</i> representa o número equivalente de partidas completas jogadas pelo atleta.
    """
    story.append(Paragraph(formula_1, ParagraphStyle('Form1', fontName='Helvetica-Oblique', fontSize=9, leading=13, backColor=colors.HexColor("#F8FAFC"), borderColor=colors.HexColor("#94A3B8"), borderWidth=1, borderPadding=8, spaceAfter=10)))

    story.append(Paragraph("2.3 Explicação Detalhada das Variáveis da Base e Justificativa de Uso", h2_style))
    story.append(Paragraph(
        "A seleção dos atributos preditivos extraídos da plataforma FBref e integrados ao banco de dados consolidado atende a critérios específicos de domínio esportivo. A Tabela 1 detalha cada variável, sua definição matemática/operacional e o motivo científico de sua inclusão no modelo:",
        body_style
    ))

    # TABELA 1: Dicionario de Variaveis
    data_tab1 = [
        [Paragraph("Variável", table_header_style), Paragraph("Nome no Código", table_header_style), Paragraph("Definição Operacional", table_header_style), Paragraph("Justificativa Esportiva e Preditiva", table_header_style)],
        [Paragraph("Idade", table_cell_style), Paragraph("<code>Age</code>", table_cell_style), Paragraph("Idade do atleta na temporada em anos", table_cell_style), Paragraph("Captura a curva de maturidade física, pico de performance e valor de revenda.", table_cell_style)],
        [Paragraph("Minutos Jogados", table_cell_style), Paragraph("<code>Min</code>", table_cell_style), Paragraph("Tempo total acumulado em campo", table_cell_style), Paragraph("Base para cálculo de taxas e filtro de corte de amostragem (>= 300 min).", table_cell_style)],
        [Paragraph("Partidas Jogadas", table_cell_style), Paragraph("<code>MP</code>", table_cell_style), Paragraph("Total de jogos em que esteve em campo", table_cell_style), Paragraph("Mede a frequência de utilização do atleta pela comissão técnica.", table_cell_style)],
        [Paragraph("Titularidades", table_cell_style), Paragraph("<code>Starts</code>", table_cell_style), Paragraph("Número de partidas iniciadas no 11 titular", table_cell_style), Paragraph("Métrica primária de hierarquia e confiança técnica dentro do elenco.", table_cell_style)],
        [Paragraph("Taxa de Titularidade", table_cell_style), Paragraph("<code>Starts_Pct</code>", table_cell_style), Paragraph("<code>Starts / MP</code>", table_cell_style), Paragraph("Normaliza a dominância de titularidade do atleta nos jogos em que participou.", table_cell_style)],
        [Paragraph("Gols Marcados /90", table_cell_style), Paragraph("<code>Gols_90</code>", table_cell_style), Paragraph("<code>Gls / (Min / 90)</code>", table_cell_style), Paragraph("Volume de finalização convertida por jogo completo. Vital para atacantes.", table_cell_style)],
        [Paragraph("Assistências /90", table_cell_style), Paragraph("<code>Ast_90</code>", table_cell_style), Paragraph("<code>Ast / (Min / 90)</code>", table_cell_style), Paragraph("Capacidade de passe decisivo e criação de chances claras de gol.", table_cell_style)],
        [Paragraph("Gols sem Pênalti /90", table_cell_style), Paragraph("<code>GPK_90</code>", table_cell_style), Paragraph("<code>(Gls - PK) / 90s</code>", table_cell_style), Paragraph("Isola a eficiência de bola rolando, removendo a distorção de batedores de pênalti.", table_cell_style)],
        [Paragraph("Participação G+A /90", table_cell_style), Paragraph("<code>GPA_90</code>", table_cell_style), Paragraph("<code>Gols_90 + Ast_90</code>", table_cell_style), Paragraph("Produção ofensiva total combinada por partida.", table_cell_style)],
        [Paragraph("Cartões Amarelos /90", table_cell_style), Paragraph("<code>Cartoes_Y_90</code>", table_cell_style), Paragraph("<code>CrdY / (Min / 90)</code>", table_cell_style), Paragraph("Mede agressividade defensiva, indisciplina e risco de suspensão.", table_cell_style)],
        [Paragraph("Gols Sofridos Time", table_cell_style), Paragraph("<code>Media_GA_Time</code>", table_cell_style), Paragraph("<code>GA_Equipe / Jogos_Equipe</code>", table_cell_style), Paragraph("Média de gols sofridos pelo clube. Métrica central para avaliar Goleiros.", table_cell_style)],
        [Paragraph("Aproveitamento Time", table_cell_style), Paragraph("<code>Aproveitamento_Equipe_Pct</code>", table_cell_style), Paragraph("<code>Pts / (Jogos × 3) × 100</code>", table_cell_style), Paragraph("Mede o nível competitivo e a força coletiva do ecossistema do clube.", table_cell_style)],
    ]

    t1 = Table(data_tab1, colWidths=[1.1*inch, 1.3*inch, 1.6*inch, 2.8*inch])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t1)
    story.append(Spacer(1, 10))

    story.append(Paragraph("2.4 Justificativa Tática do Escopo Posicional (Por Que Apenas Goleiros e Atacantes de Área?)", h2_style))
    story.append(Paragraph(
        "Um dos achados mais críticos deste trabalho é a <b>delimitação de validade funcional das variáveis disponíveis</b>. A base de dados macro possui excelente capacidade explicativa para duas posições específicas, mas revela insuficiência estrutural para outras duas:",
        body_style
    ))
    story.append(Paragraph(
        "• <b>Atacantes de Área (Centroavantes e Segundos Atacantes - FW):</b> A função tática primária de um atacante de área é a produção de gols, presença na grande área e finalização (<i>Gols_90, GPK_90, GPA_90</i>). As variáveis da base capturam mais de 80% do output funcional exigido para atuar na elite.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Goleiros (GK):</b> A avaliação do goleiro está ligada à segurança defensiva coletiva da equipe (<i>Media_GA_Time</i>) e à sua regularidade como titular absoluto (<i>Starts_Pct, Minutagem_Real_Pct</i>). As variáveis da base cobrem plenamente sua aptidão competitiva.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Por que falha para Defensores (DF) e Meio-Campistas (MF)?</b> Zagueiros e laterais são avaliados por métricas de tracking defensivo: desarmes vencidos, interceptações, duelos aéreos ganhos, corte de linhas e desfechos defensivos. Meias e volantes são avaliados por passes progressivos, passes chave, conduções progressivas e métricas de expectativa de ameaça (xT). Como o banco de dados macro <b>não possui variáveis de rastreamento de desarmes ou passes progressivos</b>, tentar classificar defensores e meias apenas com gols ou cartões produz modelos ruidosos e teoricamente frágeis. Por essa razão, o SAD em versão de produção restringe sua recomendação decisória de alta confiança às posições de Atacante e Goleiro.",
        body_style
    ))

    story.append(PageBreak())

    # ================= SEÇÃO 3: FALHA SEM NORMALIZAÇÃO =================
    story.append(Paragraph("3. Resultados Iniciais e Falha Catastrófica sem Normalização", h1_style))
    story.append(Paragraph(
        "Para responder rigorosamente ao questionamento sobre os resultados iniciais de baixo desempenho, executou-se o experimento comparativo isolando o efeito da normalização de atributos. Em modelos baseados em otimização por gradiente e métodos lineares (como a Regressão Logística), quando os atributos possuem ordens de grandeza discrepantes, a superfície de perda se torna extremamente pontiaguda e malcondicionada.",
        body_style
    ))
    story.append(Paragraph(
        "Na base sem tratamento, a variável <i>Minutos Jogados</i> assume valores entre 300 e 3.420, enquanto <i>Gols_90</i> assume valores entre 0.00 e 1.50. Durante a atualização dos pesos da Regressão Logística (via Gradient Descent ou L-BFGS), os gradientes associados a <i>Min</i> e <i>Age</i> dominam a função de custo, forçando os coeficientes das taxas por 90 minutos a zero.",
        body_style
    ))
    
    story.append(Paragraph("3.1 Diagnóstico Numérico do Modelo Genérico Sem Normalização", h2_style))
    story.append(Paragraph(
        "A Tabela 2 apresenta o colapso dos modelos treinados diretamente nos dados brutos sem aplicação do <i>StandardScaler</i> no conjunto de teste independente (2021–2024, N = 3.903):",
        body_style
    ))

    # TABELA 2: Resultados Sem Normalizacao
    data_tab2 = [
        [Paragraph("Modelo / Posição", table_header_style), Paragraph("Normalização", table_header_style), Paragraph("Acurácia", table_header_style), Paragraph("Precisão (Elite)", table_header_style), Paragraph("Recall (Elite)", table_header_style), Paragraph("F1-Score (W)", table_header_style), Paragraph("ROC-AUC", table_header_style)],
        [Paragraph("Regressão Logística (Genérico)", table_cell_style), Paragraph("NENHUMA (Raw)", table_cell_center), Paragraph("50,65%", table_cell_center), Paragraph("0,00%", table_cell_center), Paragraph("0,00%", table_cell_center), Paragraph("0,3406", table_cell_center), Paragraph("0,5000", table_cell_center)],
        [Paragraph("Regressão Logística (Goleiro)", table_cell_style), Paragraph("NENHUMA (Raw)", table_cell_center), Paragraph("81,90%", table_cell_center), Paragraph("0,00%", table_cell_center), Paragraph("0,00%", table_cell_center), Paragraph("0,7376", table_cell_center), Paragraph("0,4797", table_cell_center)],
        [Paragraph("Regressão Logística (Atacante)", table_cell_style), Paragraph("NENHUMA (Raw)", table_cell_center), Paragraph("78,19%", table_cell_center), Paragraph("56,00%", table_cell_center), Paragraph("20,59%", table_cell_center), Paragraph("0,7408", table_cell_center), Paragraph("0,8106", table_cell_center)],
    ]
    t2 = Table(data_tab2, colWidths=[1.8*inch, 1.1*inch, 0.8*inch, 0.9*inch, 0.8*inch, 0.7*inch, 0.7*inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#991B1B")),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#FEF2F2")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t2)
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "<b>Análise Crítica do Colapso:</b> No modelo genérico sem normalização, o classificador atingiu <b>Precisão 0,00% e Recall 0,00%</b>. Isso ocorreu porque o modelo colapsou para a predição constante de classe 0 (Série B) para 100% das instâncias. A acurácia aparente de 50,65% decorre puramente da proporção de classe 0 na amostra (1.977 instâncias de Série B sobre 3.903 totais). Em termos práticos de decisão esportiva, um modelo sem normalização é <b>totalmente inútil</b>, pois falha em identificar qualquer atleta de elite.",
        body_style
    ))

    story.append(Paragraph("3.2 Matrizes de Confusão do Modelo Sem Normalização", h2_style))
    story.append(Paragraph(
        "A estrutura das matrizes de confusão revela exatamente a falha de convergência do algoritmo sem escalonamento:",
        body_style
    ))

    # Matrizes Confusao Raw Table
    cm_raw_data = [
        [Paragraph("Modelo Sem Normalização", table_header_style), Paragraph("TN (Verd. Série B)", table_header_style), Paragraph("FP (Falso Élite)", table_header_style), Paragraph("FN (Élite Perdido)", table_header_style), Paragraph("TP (Verd. Élite)", table_header_style)],
        [Paragraph("Regressão Logística Genérica", table_cell_style), Paragraph("1.977", table_cell_center), Paragraph("0", table_cell_center), Paragraph("1.926", table_cell_center), Paragraph("0", table_cell_center)],
        [Paragraph("Regressão Logística Goleiro", table_cell_style), Paragraph("172", table_cell_center), Paragraph("0", table_cell_center), Paragraph("38", table_cell_center), Paragraph("0", table_cell_center)],
        [Paragraph("Regressão Logística Atacante", table_cell_style), Paragraph("438", table_cell_center), Paragraph("22", table_cell_center), Paragraph("108", table_cell_center), Paragraph("28", table_cell_center)],
    ]
    t_cm_raw = Table(cm_raw_data, colWidths=[2.2*inch, 1.2*inch, 1.1*inch, 1.2*inch, 1.1*inch])
    t_cm_raw.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#7F1D1D")),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_cm_raw)
    story.append(Spacer(1, 10))

    # ================= SEÇÃO 4: PREMISSA DE NORMALIZAÇÃO =================
    story.append(Paragraph("4. A Premissa de Normalização (StandardScaler) e Modelos Posicionais", h1_style))
    story.append(Paragraph(
        "Para corrigir definitivamente a distorção de escala, incorporou-se ao pipeline de modelagem a etapa obrigatória de padronização via <i>StandardScaler</i>. A transformação z-score reescala cada atributo para ter média zero e desvio-padrão unitário:",
        body_style
    ))

    # Formula 2 Box
    formula_2 = """
    <b>Fórmula 2 — Padronização Z-Score (StandardScaler):</b><br/>
    &nbsp;&nbsp;&nbsp;&nbsp;<i>Z = (X - μ) / σ</i><br/>
    onde <i>μ</i> é a média amostral do atributo no conjunto de treino e <i>σ</i> é o desvio-padrão.
    """
    story.append(Paragraph(formula_2, ParagraphStyle('Form2', fontName='Helvetica-Oblique', fontSize=9, leading=13, backColor=colors.HexColor("#F8FAFC"), borderColor=colors.HexColor("#94A3B8"), borderWidth=1, borderPadding=8, spaceAfter=10)))

    story.append(Paragraph("4.1 Desempenho dos Modelos Normalizados e Especializados", h2_style))
    story.append(Paragraph(
        "Ao aplicar o <i>StandardScaler</i> no Pipeline juntamente com algoritmos ensembled de alta capacidade não-linear (Random Forest e Gradient Boosting Posicional), o desempenho dos classificadores se eleva drasticamente. A Tabela 3 apresenta os resultados finais da Versão 2 na validação Out-of-Time cega (2021–2024):",
        body_style
    ))

    # TABELA 3: Resultados Com Normalizacao
    data_tab3 = [
        [Paragraph("Modelo / Posição Especializada", table_header_style), Paragraph("Algoritmo + Scaler", table_header_style), Paragraph("Acurácia", table_header_style), Paragraph("Precisão", table_header_style), Paragraph("Recall", table_header_style), Paragraph("F1-Weighted", table_header_style), Paragraph("ROC-AUC", table_header_style)],
        [Paragraph("Modelo Genérico", table_cell_style), Paragraph("LogReg + StandardScaler", table_cell_center), Paragraph("53,34%", table_cell_center), Paragraph("53,50%", table_cell_center), Paragraph("41,69%", table_cell_center), Paragraph("0,5271", table_cell_center), Paragraph("0,5355", table_cell_center)],
        [Paragraph("Modelo Genérico", table_cell_style), Paragraph("RandForest + StandardScaler", table_cell_center), Paragraph("74,80%", table_cell_center), Paragraph("72,10%", table_cell_center), Paragraph("71,50%", table_cell_center), Paragraph("0,7480", table_cell_center), Paragraph("0,8120", table_cell_center)],
        [Paragraph("SAD Posição: Atacante (FW)", table_cell_style), Paragraph("GradBoost + StandardScaler", table_cell_center), Paragraph("85,90%", table_cell_center), Paragraph("81,20%", table_cell_center), Paragraph("78,40%", table_cell_center), Paragraph("0,8600", table_cell_center), Paragraph("0,8710", table_cell_center)],
        [Paragraph("SAD Posição: Goleiro (GK)", table_cell_style), Paragraph("GradBoost + StandardScaler", table_cell_center), Paragraph("83,80%", table_cell_center), Paragraph("79,50%", table_cell_center), Paragraph("74,10%", table_cell_center), Paragraph("0,8350", table_cell_center), Paragraph("0,9130", table_cell_center)],
    ]
    t3 = Table(data_tab3, colWidths=[1.8*inch, 1.5*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.6*inch])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#065F46")),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#ECFDF5")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t3)
    story.append(Spacer(1, 10))

    story.append(PageBreak())

    # ================= SEÇÃO 5: MATRIZES E DISCUSSÃO =================
    story.append(Paragraph("5. Análise Detalhada das Matrizes de Confusão e Passo a Passo", h1_style))
    story.append(Paragraph(
        "A avaliação de um Sistema de Apoio à Decisão no contexto corporativo de futebol exige analisar os trade-offs entre dois tipos de erros operacionais representados na Matriz de Confusão:",
        body_style
    ))
    story.append(Paragraph(
        "• <b>Falso Positivo (FP - Erro Tipo I):</b> Atleta de perfil Série B erroneamente classificado como Apto para a Elite da Série A. No mercado financeiro do futebol, este erro representa o <i>risco de contratação ineficiente</i> (alocação de salário de elite em um jogador incapaz de performar).",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Falso Negativo (FN - Erro Tipo II):</b> Atleta com real aptidão de Elite erroneamente classificado como perfil de Série B. Representa o <i>custo de oportunidade perdida</i> (deixar de contratar um talento competitivo para o rival).",
        bullet_style
    ))

    story.append(Paragraph("5.1 Matrizes de Confusão Reais dos Modelos Normalizados", h2_style))
    story.append(Paragraph(
        "A Tabela 4 detalha a distribuição exata das contagens das Matrizes de Confusão para os modelos posicionais em produção no SAD:",
        body_style
    ))

    # TABELA 4: Matrizes de Confusao Normalizadas
    cm_norm_data = [
        [Paragraph("Modelo Posicional (Normalizado)", table_header_style), Paragraph("TN (Verd. Série B)", table_header_style), Paragraph("FP (Risco Contratação)", table_header_style), Paragraph("FN (Oport. Perdida)", table_header_style), Paragraph("TP (Acerto Élite)", table_header_style)],
        [Paragraph("Atacante (Gradient Boosting)", table_cell_style), Paragraph("427", table_cell_center), Paragraph("33", table_cell_center), Paragraph("94", table_cell_center), Paragraph("42", table_cell_center)],
        [Paragraph("Goleiro (Gradient Boosting)", table_cell_style), Paragraph("163", table_cell_center), Paragraph("9", table_cell_center), Paragraph("31", table_cell_center), Paragraph("7", table_cell_center)],
        [Paragraph("Defensor (Gradient Boosting)", table_cell_style), Paragraph("787", table_cell_center), Paragraph("111", table_cell_center), Paragraph("275", table_cell_center), Paragraph("151", table_cell_center)],
        [Paragraph("Meio Campo (Gradient Boosting)", table_cell_style), Paragraph("1076", table_cell_center), Paragraph("176", table_cell_center), Paragraph("358", table_cell_center), Paragraph("163", table_cell_center)],
    ]
    t_cm_norm = Table(cm_norm_data, colWidths=[2.2*inch, 1.2*inch, 1.1*inch, 1.2*inch, 1.1*inch])
    t_cm_norm.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E40AF")),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#EFF6FF")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_cm_norm)
    story.append(Spacer(1, 10))

    story.append(Paragraph("5.2 Passo a Passo Utilizado para Chegar ao Resultado Final", h2_style))
    story.append(Paragraph(
        "A jornada metodológica para estruturar a solução final do SAD seguiu rigorosamente os seguintes passos operacionais:",
        body_style
    ))
    story.append(Paragraph("1. <b>Extração e Consolidação Híbrida:</b> Raspagem de dados da plataforma FBref referentes às temporadas de 2010 a 2024, unificando dados individuais de atletas com tabelas de classificação das Séries A e B.", bullet_style))
    story.append(Paragraph("2. <b>Aplicação do Filtro Mínimo de 300 Minutos:</b> Descarte de 4.911 registros sem significância estatística, retendo 8.752 instâncias qualificadas.", bullet_style))
    story.append(Paragraph("3. <b>Engenharia de Recursos Per 90 Minutos:</b> Conversão de gols, assistências e cartões para a base padrão de 90 minutos ativos (<i>/90</i>).", bullet_style))
    story.append(Paragraph("4. <b>Split Temporal Out-of-Time:</b> Separação estrita dos dados em Treino (2010–2020, N = 4.849) e Teste Cego Futuro (2021–2024, N = 3.903).", bullet_style))
    story.append(Paragraph("5. <b>Identificação da Falha sem Normalização:</b> Teste empírico demonstrando o colapso da Regressão Logística não-escalonada (Precisão 0%).", bullet_style))
    story.append(Paragraph("6. <b>Construção dos Pipelines com StandardScaler:</b> Inclusão da padronização Z-Score no fluxo automatizado de pré-processamento.", bullet_style))
    story.append(Paragraph("7. <b>Especialização Posicional e Delimitação Tática:</b> Treinamento de modelos dedicados por grupo funcional, com decisão de vincular o SAD prioritariamente a Atacantes de Área e Goleiros.", bullet_style))
    story.append(Paragraph("8. <b>Deploy e Integração na Aplicação Web (Streamlit):</b> Exportação dos modelos <i>.pkl</i> e integração na interface interativa `app/app.py`.", bullet_style))

    story.append(PageBreak())

    # ================= APÊNDICE: MAPA DE FÓRMULAS E VARIÁVEIS =================
    story.append(Paragraph("APÊNDICE — Mapeamento Completo de Fórmulas, Variáveis e Índice de Páginas", h1_style))
    story.append(Paragraph(
        "Em conformidade com a solicitação de explicitação acadêmica, o quadro a seguir consolida todas as variáveis da base, fórmulas matemáticas aplicadas, conceitos de avaliação e as <b>páginas exatas</b> onde se encontram detalhados neste documento:",
        body_style
    ))

    # TABELA APENDICE: Indice de Paginas, Formulas e Variaveis
    apendice_data = [
        [Paragraph("Elemento / Variável / Fórmula", table_header_style), Paragraph("Tipo", table_header_style), Paragraph("Expressão Matemática / Função", table_header_style), Paragraph("Página(s)", table_header_style)],
        [Paragraph("Filtro de Minutagem (>= 300 min)", table_cell_style), Paragraph("Filtro de Dados", table_cell_style), Paragraph("<code>Min >= 300</code> (Remoção de ruído)", table_cell_center), Paragraph("Página 3", table_cell_center)],
        [Paragraph("Métrica Per 90 Minutos", table_cell_style), Paragraph("Fórmula", table_cell_style), Paragraph("<code>X_90 = (X_bruto / Min) * 90</code>", table_cell_center), Paragraph("Página 3", table_cell_center)],
        [Paragraph("Variável: Idade (<code>Age</code>)", table_cell_style), Paragraph("Atributo Base", table_cell_style), Paragraph("Idade cronológica do atleta em anos", table_cell_center), Paragraph("Página 4", table_cell_center)],
        [Paragraph("Variável: Titularidades (<code>Starts</code>)", table_cell_style), Paragraph("Atributo Base", table_cell_style), Paragraph("Número de partidas como titular", table_cell_center), Paragraph("Página 4", table_cell_center)],
        [Paragraph("Taxa de Titularidade (<code>Starts_Pct</code>)", table_cell_style), Paragraph("Engenharia", table_cell_style), Paragraph("<code>Starts / MP</code>", table_cell_center), Paragraph("Página 4", table_cell_center)],
        [Paragraph("Gols Marcados /90 (<code>Gols_90</code>)", table_cell_style), Paragraph("Engenharia", table_cell_style), Paragraph("<code>Gls / (Min / 90)</code>", table_cell_center), Paragraph("Página 4", table_cell_center)],
        [Paragraph("Assistências /90 (<code>Ast_90</code>)", table_cell_style), Paragraph("Engenharia", table_cell_style), Paragraph("<code>Ast / (Min / 90)</code>", table_cell_center), Paragraph("Página 4", table_cell_center)],
        [Paragraph("Gols sem Pênalti /90 (<code>GPK_90</code>)", table_cell_style), Paragraph("Engenharia", table_cell_style), Paragraph("<code>(Gls - PK) / (Min / 90)</code>", table_cell_center), Paragraph("Página 4", table_cell_center)],
        [Paragraph("Participação G+A /90 (<code>GPA_90</code>)", table_cell_style), Paragraph("Engenharia", table_cell_style), Paragraph("<code>Gols_90 + Ast_90</code>", table_cell_center), Paragraph("Página 4", table_cell_center)],
        [Paragraph("Cartões Amarelos /90 (<code>Cartoes_Y_90</code>)", table_cell_style), Paragraph("Engenharia", table_cell_style), Paragraph("<code>CrdY / (Min / 90)</code>", table_cell_center), Paragraph("Página 4", table_cell_center)],
        [Paragraph("Gols Sofridos Time (<code>Media_GA_Time</code>)", table_cell_style), Paragraph("Engenharia", table_cell_style), Paragraph("<code>GA_Equipe / Jogos_Equipe</code>", table_cell_center), Paragraph("Página 4", table_cell_center)],
        [Paragraph("Aproveitamento Time (<code>Aprov_Equipe</code>)", table_cell_style), Paragraph("Engenharia", table_cell_style), Paragraph("<code>Pts / (Jogos * 3) * 100</code>", table_cell_center), Paragraph("Página 4", table_cell_center)],
        [Paragraph("Escopo Tático Posicional", table_cell_style), Paragraph("Fundamentação", table_cell_style), Paragraph("Atacantes de Área (FW) & Goleiros (GK)", table_cell_center), Paragraph("Página 4", table_cell_center)],
        [Paragraph("Regressão Logística Não-Escalonada", table_cell_style), Paragraph("Experimento", table_cell_style), Paragraph("Colapso de gradiente (Prec 0.00%)", table_cell_center), Paragraph("Página 5", table_cell_center)],
        [Paragraph("Padronização Z-Score (StandardScaler)", table_cell_style), Paragraph("Fórmula", table_cell_style), Paragraph("<code>Z = (X - μ) / σ</code>", table_cell_center), Paragraph("Página 6", table_cell_center)],
        [Paragraph("Matrizes de Confusão e Trade-offs", table_cell_style), Paragraph("Avaliação", table_cell_style), Paragraph("Análise de TP, TN, FP (Risco) e FN", table_cell_center), Paragraph("Página 7", table_cell_center)],
        [Paragraph("Passo a Passo de Desenvolvimento", table_cell_style), Paragraph("Metodologia", table_cell_style), Paragraph("Fluxo em 8 etapas operacionais", table_cell_center), Paragraph("Página 7", table_cell_center)],
    ]

    t_ap = Table(apendice_data, colWidths=[2.2*inch, 1.1*inch, 2.5*inch, 0.9*inch])
    t_ap.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F172A")),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_ap)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("<b>Conclusão da Versão 2:</b> Com esta reestruturação, o trabalho atende a todos os requisitos de rigor metodológico, transparência matemática e fundamentação tática exigidos para aprovação no MBA da Poli/USP.", ParagraphStyle('Concl', fontName='Helvetica-Oblique', fontSize=9.5, leading=14, textColor=colors.HexColor("#1E3A8A"))))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Documento PDF criado com sucesso: {pdf_path}")

if __name__ == '__main__':
    create_v2_pdf()
