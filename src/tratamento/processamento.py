import pandas as pd
import numpy as np
import os
import glob

def unificar_csvs(pasta_entrada: str) -> pd.DataFrame:
    """Lê todos os CSVs brutos da pasta de Data Raw e concatena num único Dataset"""
    arquivos = glob.glob(os.path.join(pasta_entrada, "*.csv"))
    if not arquivos:
        print("Aviso: Nenhum arquivo CSV encontrado para processar.")
        return pd.DataFrame()
        
    df_list = [pd.read_csv(arq) for arq in arquivos]
    df_consolidado = pd.concat(df_list, ignore_index=True)
    return df_consolidado

def limpar_dados_fbref(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove colunas inúteis, converte tipos de dados, 
    trata nomes de posições variados (FW, MF, DF, GK)
    """
    print("Iniciando limpeza da base de dados...")
    # Remover linha inútil de cabeçalho duplo
    if 'Player' in df.columns:
        df = df[df['Player'] != 'Player']
        
    # Manter só onde o jogador existe
    df = df.dropna(subset=['Player'])

    # Padronização de Idade (Removendo o formato 24-123)
    if 'Age' in df.columns:
        df['Age'] = df['Age'].astype(str).str.split('-').str[0]
        df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
        
    # Limpar a Posição (Ex: DF,MF para DF) - Pegamos a primeira sigla predominante
    if 'Pos' in df.columns:
        df['Pos_Primary'] = df['Pos'].astype(str).str.split(',').str[0]
        
    # Preencher NaN com 0 para métricas de jogo.
    cols_numericas = df.select_dtypes(include=[np.number]).columns
    df[cols_numericas] = df[cols_numericas].fillna(0)
    
    return df

def padronizar_p90(df: pd.DataFrame, min_limite: int = 150) -> pd.DataFrame:
    """
    Aplica a normalização /90.
    Corta (remove) jogadores que jogaram menos que 'min_limite' para 
    evitar 'outliers' bizarros (como quem jogou 2 minutos e fez 1 gol -> 45 Gols/90)
    """
    print("Criando estatísticas P90 (per 90 minutes)...")
    if 'Min' not in df.columns:
        print("Atributo Min_Playing não encontrado para formar a base de P90.")
        return df

    # Converte para numerico forcadamente para lidar com vestigios do CSV
    df['Min'] = pd.to_numeric(df['Min'], errors='coerce').fillna(0)
    
    # Cortando outliers brutos (Nós queremos validar jogadores titulares ou reservas rotineiros)
    df = df[df['Min'] >= min_limite].copy()
    
    # Colunas de métricas alvo que precisaremos tratar (gols, assitências, chutes, desarmes)
    # Exemplo: 'Gls', 'Ast', 'Sh', 'Tkl', 'Int', etc. (Se existirem na base raw)
    metricas = [c for c in df.columns if c not in ['Player', 'Nation', 'Pos', 'Pos_Primary', 'Squad', 'Comp', 'Age', 'Born', 'Min', 'Season', 'Divisao_Alvo']]
    
    for col in metricas:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        nova_col = f"{col}_p90"
        df[nova_col] = (df[col] / df['Min']) * 90
        
    return df

def aplicar_coeficiente_liga(df: pd.DataFrame) -> pd.DataFrame:
    """
    Padronização por Coeficiente de Força Organizacional (Level of Opposition).
    Multiplica as métricas duras (Gols, Desarmes) pelo peso da liga atual do jogador.
    Assim, os Gols na Série C sofrem um "deságio", deixando-os justos ao se comparar com a Série A.
    Vamos nos basear APENAS nas divisões estruturadas (A, B, C) e ignorar campeonatos paralelos
    como o 'Carioca' ou 'Copa do Nordeste' para otimizar os recursos do modelo.
    """
    print("Aplicando Ponderação Específica por Força da Divisão (Série A/B/C)...")
    
    # Dicionário acadêmico de Pesos Sugeridos
    pesos = {
        'Série A': 1.0,
        'Série B': 0.75,
        'Série C': 0.50
    }
    
    # Mapeando os atributos que precisam de ajuste de Força
    # Assistências de Goleiros, Gols de Zagueiros estão inclusos pois 'Gols' afeta universalmente.
    cols_para_pesar = [c for c in df.columns if c.endswith('_p90')]
    
    for _, row in df.iterrows():
        peso = pesos.get(row.get('Divisao_Alvo', 'Série C'), 0.50) # C fallback
        for col in cols_para_pesar:
            df.at[_, col] = row[col] * peso
            
    return df

if __name__ == "__main__":
    print("\\n=== Módulo de Processamento ETL (TCC) ===")
    
    # 1. Agrupar Base Bruta
    df_raw = unificar_csvs("data/raw")
    if not df_raw.empty:
        # 2. Limpeza Primária
        df_limpo = limpar_dados_fbref(df_raw)
        
        # 3. Normalização Per 90 e Corte de Outliers (< 300 minutos descartados)
        df_p90 = padronizar_p90(df_limpo, min_limite=300)
        
        # 4. Feature Engineering: Coeficiente de Força
        df_processado = aplicar_coeficiente_liga(df_p90)
        
        # Exportação
        os.makedirs("data/processed", exist_ok=True)
        caminho_final = "data/processed/dados_finais_treinamento.csv"
        df_processado.to_csv(caminho_final, index=False)
        print(f"\\n[OK] ETL Concluido com Sucesso! Arquivo final salvo ({len(df_processado)} linhas validas): {caminho_final}")
        
        print("\\nDemonstracao das Metricas apos Pipeline (Gols Ajustados pela Liga):")
        if 'Gls_p90' in df_processado.columns:
            print(df_processado[['Player', 'Divisao_Alvo', 'Pos_Primary', 'Min', 'Gls_p90']].head())
