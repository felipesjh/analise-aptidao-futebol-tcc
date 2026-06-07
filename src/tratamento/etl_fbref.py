"""
ETL Robusto para dados copiados manualmente do FBRef.
Aceita arquivos .csv, .txt (separado por tab) ou qualquer formato colado do navegador.
Uso: python src/tratamento/etl_fbref.py
"""
import pandas as pd
import numpy as np
import os
import glob
import re
import io


def detectar_separador(caminho: str) -> str:
    """Detecta se o arquivo usa vírgula, tab ou ponto-e-vírgula."""
    with open(caminho, 'r', encoding='utf-8', errors='replace') as f:
        amostra = f.read(2000)
    tabs = amostra.count('\t')
    virgulas = amostra.count(',')
    pv = amostra.count(';')
    if tabs > virgulas and tabs > pv:
        return '\t'
    if pv > virgulas:
        return ';'
    return ','


def extrair_meta_do_nome(nome_arquivo: str):
    """
    Extrai Ano e Divisão a partir do nome do arquivo.
    Padrão esperado: SerieA_2023.txt / SerieB_2019.csv
    """
    base = os.path.basename(nome_arquivo).upper()
    
    # Extrair ano (4 dígitos)
    match_ano = re.search(r'(20\d{2})', base)
    ano = int(match_ano.group(1)) if match_ano else None
    
    # Extrair divisão
    if 'SERIEA' in base.replace('_','').replace('-','') or 'SERIE_A' in base or 'SERIE-A' in base:
        divisao = 'Série A'
    elif 'SERIEB' in base.replace('_','').replace('-','') or 'SERIE_B' in base or 'SERIE-B' in base:
        divisao = 'Série B'
    else:
        divisao = 'Desconhecido'
    
    return ano, divisao


def ler_arquivo_fbref(caminho: str, ano: int, divisao: str) -> pd.DataFrame:
    """
    Lê um arquivo copiado do FBRef, lidando com:
    - Cabeçalho duplo (FBRef tem multi-index)
    - Linhas 'Player' repetidas (bug clássico do FBRef)
    - Separadores variados (tab, vírgula)
    - Colunas com nomes duplicados
    """
    sep = detectar_separador(caminho)
    
    try:
        # Tentar leitura direta
        df = pd.read_csv(caminho, sep=sep, encoding='utf-8', errors='replace', header=0)
    except Exception:
        with open(caminho, 'r', encoding='utf-8', errors='replace') as f:
            conteudo = f.read()
        df = pd.read_csv(io.StringIO(conteudo), sep=sep, header=0)

    # Remover linhas duplicadas de cabeçalho que o FBRef insere no meio da tabela
    if 'Player' in df.columns:
        df = df[df['Player'] != 'Player']
        df = df[df['Player'].notna()]
        df = df[df['Player'].str.strip() != '']

    # Padronizar nome da coluna de minutos (FBRef usa "Min" ou "90s" ou "Min_Playing")
    colunas_min = [c for c in df.columns if c.lower() in ('min', 'min_playing', 'minutos', 'minutes')]
    if colunas_min:
        df = df.rename(columns={colunas_min[0]: 'Min'})

    # Adicionar metadados
    df['Ano'] = ano
    df['Divisao_Alvo'] = divisao

    print(f"  Lido: {os.path.basename(caminho)} -> {len(df)} linhas, {len(df.columns)} colunas")
    return df


def limpar_e_normalizar(df: pd.DataFrame, min_minutos: int = 300) -> pd.DataFrame:
    """
    Pipeline de limpeza completo:
    1. Converter tipos
    2. Padronizar posições
    3. Cortar outliers de baixo minuto
    4. Calcular métricas /90
    5. Aplicar Coeficiente de Liga
    """
    print("\n[ETL] Iniciando limpeza...")

    # Converter Min para numérico
    if 'Min' in df.columns:
        df['Min'] = df['Min'].astype(str).str.replace(',', '').str.strip()
        df['Min'] = pd.to_numeric(df['Min'], errors='coerce').fillna(0)
    else:
        print("  [AVISO] Coluna 'Min' não encontrada! Verifique o arquivo copiado.")
        return df

    # Padronizar Idade (FBRef usa "24-123" -> pegar só o número inteiro)
    if 'Age' in df.columns:
        df['Age'] = df['Age'].astype(str).str.split('-').str[0]
        df['Age'] = pd.to_numeric(df['Age'], errors='coerce')

    # Padronizar Posição (ex: "FW,MF" -> "FW")
    if 'Pos' in df.columns:
        df['Pos_Primary'] = df['Pos'].astype(str).str.split(',').str[0].str.strip()
        mapa_pos = {'GK': 'Goleiro', 'DF': 'Defensor', 'MF': 'Meio Campo', 'FW': 'Atacante'}
        df['Pos_PT'] = df['Pos_Primary'].map(mapa_pos).fillna('Outro')

    # Cortar jogadores com poucos minutos (Outliers)
    df = df[df['Min'] >= min_minutos].copy()
    print(f"  Após corte de >{min_minutos} min: {len(df)} jogadores válidos")

    # Métricas /90 — todas as colunas numéricas relevantes
    cols_excluir = {'Player', 'Nation', 'Pos', 'Pos_Primary', 'Pos_PT', 'Squad',
                    'Comp', 'Age', 'Born', 'Min', 'Ano', 'Divisao_Alvo', 'MP', 'Starts'}
    colunas_metricas = [
        c for c in df.columns
        if c not in cols_excluir
        and df[c].dtype == object  == False  # Tentar apenas numéricas
    ]
    # Forçar conversão numérica em todas as colunas restantes
    for col in df.columns:
        if col not in cols_excluir:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            df[f'{col}_p90'] = (df[col] / df['Min'].replace(0, np.nan)) * 90

    # Coeficiente de Liga (normalização por força da divisão)
    pesos = {'Série A': 1.0, 'Série B': 0.75, 'Série C': 0.50}
    cols_p90 = [c for c in df.columns if c.endswith('_p90')]

    print(f"  Aplicando coeficiente de liga ({df['Divisao_Alvo'].unique()})...")
    for idx, row in df.iterrows():
        peso = pesos.get(row['Divisao_Alvo'], 0.75)
        for col in cols_p90:
            df.at[idx, col] = row[col] * peso

    return df


def rodar_etl_completo():
    """
    Orquestrador principal:
    - Lê todos os arquivos de data/raw/
    - Processa cada um
    - Une tudo e exporta
    """
    pasta_raw = 'data/raw'
    pasta_out = 'data/processed'
    os.makedirs(pasta_out, exist_ok=True)

    # Buscar todos os .txt e .csv (exceto o arquivo de teste antigo)
    arquivos = glob.glob(os.path.join(pasta_raw, 'Serie*.txt'))
    arquivos += glob.glob(os.path.join(pasta_raw, 'Serie*.csv'))
    arquivos = [a for a in arquivos if 'teste' not in a.lower()]

    if not arquivos:
        print("[ERRO] Nenhum arquivo encontrado em data/raw/")
        print("Arquivos esperados: SerieA_2023.txt, SerieB_2019.csv, etc.")
        return

    print(f"[ETL] {len(arquivos)} arquivos encontrados para processar:\n")
    for a in sorted(arquivos):
        print(f"  - {os.path.basename(a)}")

    todos_dfs = []
    for caminho in sorted(arquivos):
        ano, divisao = extrair_meta_do_nome(caminho)
        if not ano:
            print(f"  [SKIP] Não consegui extrair ano de: {caminho}")
            continue
        print(f"\n>>> Processando {os.path.basename(caminho)} ({divisao} {ano})")
        df = ler_arquivo_fbref(caminho, ano, divisao)
        todos_dfs.append(df)

    if not todos_dfs:
        print("[ERRO] Nenhum dado válido processado.")
        return

    # Unificar
    df_total = pd.concat(todos_dfs, ignore_index=True)
    print(f"\n[ETL] Base unificada: {len(df_total)} linhas brutas")

    # Limpeza e normalização
    df_final = limpar_e_normalizar(df_total, min_minutos=300)

    # Exportar
    caminho_final = os.path.join(pasta_out, 'base_treinamento_completa.csv')
    df_final.to_csv(caminho_final, index=False, encoding='utf-8-sig')

    print(f"\n[OK] ETL concluido! Arquivo salvo: {caminho_final}")
    print(f"     Total de jogadores validos: {len(df_final)}")
    print(f"     Anos cobertos: {sorted(df_final['Ano'].unique())}")
    print(f"     Divisoes: {df_final['Divisao_Alvo'].unique()}")

    # Preview
    if 'Player' in df_final.columns:
        print("\nPrimeiros jogadores da base final:")
        cols_view = [c for c in ['Player', 'Squad', 'Pos_PT', 'Divisao_Alvo', 'Ano', 'Min'] if c in df_final.columns]
        print(df_final[cols_view].head(10).to_string(index=False))


if __name__ == '__main__':
    rodar_etl_completo()
