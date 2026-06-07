import pandas as pd
import os
import glob

def clean_fbref_df(df, ano, divisao):
    """
    Cleans a dataframe extracted from a FBRef-style Excel sheet.
    """
    # 1. Identify where the data starts
    # We look for a row that contains both 'Player' and 'Squad' for player stats
    # or 'Squad' and 'MP' for team stats.
    header_row_idx = None
    
    # Priority for Players if we expect players
    target_headers = ['player', 'rk', 'squad', 'mp']
    
    for i in range(len(df)):
        row_values = [str(x).lower() for x in df.iloc[i].values]
        # For players, we definitely want the row with 'Player'
        if 'player' in row_values and 'rk' in row_values:
            header_row_idx = i
            break
            
    # Fallback/Team stats logic
    if header_row_idx is None:
        for i in range(min(20, len(df))):
            row_values = [str(x).lower() for x in df.iloc[i].values]
            if 'squad' in row_values and 'mp' in row_values:
                header_row_idx = i
                break
    
    if header_row_idx is None:
        # Fallback to previous logic if the specific combo isn't found
        for i in range(min(15, len(df))):
            row_values = [str(x).lower() for x in df.iloc[i].values]
            if 'player' in row_values or 'rk' in row_values:
                header_row_idx = i
                break
    
    if header_row_idx is None:
        return pd.DataFrame() # Skip if no header found
    
    # 2. Set the identified row as header
    new_header = df.iloc[header_row_idx]
    df = df.iloc[header_row_idx + 1:].copy()
    df.columns = new_header
    
    # 3. Basic cleaning
    # Remove rows that are repetitions of the header (FBRef does this every 25 rows)
    if 'Player' in df.columns:
        df = df[df['Player'] != 'Player']
        # Filter out aggregate/metadata rows
        df = df[~df['Player'].astype(str).str.contains('Squad Stats|Totals|Opponent Stats', case=False, na=False)]
    elif 'Squad' in df.columns:
        df = df[df['Squad'] != 'Squad']
        df = df[~df['Squad'].astype(str).str.contains('Squad Stats|Totals|Opponent Stats', case=False, na=False)]
        
    # Remove rows where the first column is NaN or 'Glossary'
    df = df[df.iloc[:, 0].notna()]
    df = df[df.iloc[:, 0].astype(str).str.lower() != 'glossary']
    
    # 5. Clean column names (strip whitespace, remove \n)
    cols = [str(c).replace('\n', ' ').strip() for c in df.columns]
    
    # Handle duplicate column names
    seen = {}
    new_cols = []
    for c in cols:
        if c in seen:
            seen[c] += 1
            new_cols.append(f"{c}_{seen[c]}")
        else:
            seen[c] = 0
            new_cols.append(c)
    df.columns = new_cols
    
    # Remove 'nan' columns
    df = df.loc[:, [c for c in df.columns if str(c).lower() != 'nan']]
    
    # 6. Add metadata
    df['Ano'] = ano
    df['Divisao'] = divisao
    
    # 7. Final cleaning: convert object columns to string and try to fix numeric columns
    for col in df.columns:
        # Specific fix for Age (FBRef uses "24-123")
        if col == 'Age':
            df[col] = df[col].astype(str).str.split('-').str[0]
            
        # Convert to string first to handle mixed types
        df[col] = df[col].astype(str).str.strip()
        
        # Try to convert to numeric if it looks like a number
        # Remove commas and dots (thousands separators) and check
        temp_col = df[col].astype(str).str.replace(',', '', regex=False).str.replace('.', '', regex=False).str.replace('%', '', regex=False)
        numeric_col = pd.to_numeric(temp_col, errors='coerce')
        
        # Specific check for 90s column (which SHOULD have a decimal dot)
        if col == '90s':
            temp_col_90s = df[col].astype(str).str.replace(',', '.', regex=False) # Ensure decimal dot
            numeric_col = pd.to_numeric(temp_col_90s, errors='coerce')
        
        # If most of the column is numeric (more than 80%), keep it as numeric
        if numeric_col.notna().sum() > 0.8 * len(df):
            df[col] = numeric_col
            
    # 8. Encoding fix for team names and strings
    def fix_encoding(text):
        if not isinstance(text, str): return text
        # Remove the \ufffd (replacement character) and try to reconstruct
        text = text.replace('\ufffd', '') 
        
        replacements = {
            'Amrica': 'América',
            'Atltico': 'Atlético',
            'Grmio': 'Grêmio',
            'So Paulo': 'São Paulo',
            'Vitria': 'Vitória',
            'Cuiab': 'Cuiabá',
            'Ava': 'Avaí',
            'Gois': 'Goiás',
            'Cear': 'Ceará',
            'Srie': 'Série',
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        return text.strip()

    if 'Squad' in df.columns:
        df['Squad'] = df['Squad'].apply(fix_encoding)
    if 'Player' in df.columns:
        df['Player'] = df['Player'].apply(fix_encoding)
        
    return df

def process_excel_file(file_path, divisao):
    print(f"Processando {file_path}...")
    xl = pd.ExcelFile(file_path)
    all_years = []
    
    for sheet_name in xl.sheet_names:
        if sheet_name.isdigit():
            ano = int(sheet_name)
            df_sheet = xl.parse(sheet_name)
            df_clean = clean_fbref_df(df_sheet, ano, divisao)
            if not df_clean.empty:
                all_years.append(df_clean)
                print(f"  - Ano {ano}: {len(df_clean)} registros")
    
    if all_years:
        return pd.concat(all_years, ignore_index=True)
    return pd.DataFrame()

def main():
    output_dir = 'data/processed_tcc'
    os.makedirs(output_dir, exist_ok=True)
    
    # Paths to the files provided by the user
    path_jogadores_a = 'data/base_TCC/jogadores/jogadores-serieA.xlsx'
    path_jogadores_b = 'data/base_TCC/jogadores/jogadores-serieB.xlsx'
    path_camp_a = 'data/base_TCC/campeonato/SerieA-classificacao.xlsx'
    path_camp_b = 'data/base_TCC/campeonato/SerieB-classificacao.xlsx'
    
    # Process Players
    print("\n--- PROCESSANDO JOGADORES ---")
    df_jog_a = process_excel_file(path_jogadores_a, 'Série A')
    df_jog_b = process_excel_file(path_jogadores_b, 'Série B')
    
    df_jogadores_total = pd.concat([df_jog_a, df_jog_b], ignore_index=True)
    
    # Process Championship
    print("\n--- PROCESSANDO CAMPEONATO ---")
    df_camp_a = process_excel_file(path_camp_a, 'Série A')
    df_camp_b = process_excel_file(path_camp_b, 'Série B')
    
    df_camp_total = pd.concat([df_camp_a, df_camp_b], ignore_index=True)
    
    # Save results
    print("\n--- SALVANDO RESULTADOS ---")
    
    # Jogadores
    df_jogadores_total.to_parquet(os.path.join(output_dir, 'jogadores_consolidado.parquet'), index=False)
    df_jogadores_total.to_csv(os.path.join(output_dir, 'jogadores_consolidado.csv'), index=False, encoding='utf-8-sig')
    print(f"Jogadores: {len(df_jogadores_total)} registros salvos.")
    
    # Campeonato
    df_camp_total.to_parquet(os.path.join(output_dir, 'campeonato_consolidado.parquet'), index=False)
    df_camp_total.to_csv(os.path.join(output_dir, 'campeonato_consolidado.csv'), index=False, encoding='utf-8-sig')
    print(f"Campeonato: {len(df_camp_total)} registros salvos.")

if __name__ == "__main__":
    main()
