import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import io

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Configurações para Respeitar os Rate Limits do FBRef
FB_REF_DELAY = 4.0 # Em Segundos (Mínimo recomendado para FBref evitar IP Block)

# Mapeamento básico das rotas do FBref para as divisões brasileiras.
# O id da competição (Ex: 24 = Serie A) não costuma mudar, mas o ano varia.
COMPETITIONS = {
    'Serie_A': '24',
    'Serie_B': '38',
}

def get_league_url(comp_id: str, season_year: int, comp_name: str) -> str:
    """Constrói a URL de estatísticas gerais da temporada no FBRef."""
    # Exemplo: https://fbref.com/en/comps/24/2023/2023-Campeonato-Brasileiro-Serie-A-Stats
    return f"https://fbref.com/en/comps/{comp_id}/{season_year}/stats/{season_year}-{comp_name}-Stats"

def scrape_players_season(url: str, season: int, divisao: str) -> pd.DataFrame:
    print(f"[{season} - {divisao}] Extraindo dados de: {url}")
    time.sleep(FB_REF_DELAY) 
    
DELAY_REQUESTS = 6  # FBRef pune acessos em massa, Selenium mascara, mas atraso é essencial

# Mapeando URLs historicas (padrao mudou um pouco ao longo dos anos, assumindo padrao atual)
def get_league_url(comp_id: str, season: int, comp_name: str) -> str:
    # FBRef URL pattern: https://fbref.com/en/comps/{id}/{season}/stats/{season}-{name}-Stats
    return f"https://fbref.com/en/comps/{comp_id}/{season}/stats/{season}-{comp_name}-Stats"

def inicilizar_driver():
    """Inicializa o bot do Google Chrome em modo de fundo (Healdess) para não pipocar telas"""
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Roda invisível
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("window-size=1920,1080")
    # Disfarce absoluto (User-Agent real de Windows)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/120.0.0.0")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def extract_standard_stats(url: str, ano: int, divisao: str, driver) -> pd.DataFrame:
    """Extrai estaticas via navegação controlada pelo bot evitando Error 403"""
    try:
        driver.get(url)
        time.sleep(DELAY_REQUESTS) # Espera Cloudflare processar JS (crucial)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        tabela = soup.find('table', {'id': 'stats_standard'})
        
        if not tabela:
            print(f"  [Aviso] Nenhuma tabela encontrada para {ano} na {divisao}.")
            return pd.DataFrame()
            
        # O Pandas consegue parsear a tabela do HTML se ela for passada como string do BeautifulSoup
        df = pd.read_html(str(tabela), header=1)[0]
        
        df['Ano'] = ano
        df['Divisao_Alvo'] = divisao
        
        return df
    except Exception as e:
        print(f"  [Erro Severo] Falha ao tentar varrer {url}. Detalhe: {e}")
        return pd.DataFrame()

def rodar_extracao(nome_projeto: str, anos_lista: list):
    """Orquestrador do web scraping com Selenium WebDriver"""
    print(f"=== Iniciando Pipeline de Extração: {nome_projeto} ===")
    
    past_raw = os.path.join("data", "raw")
    os.makedirs(past_raw, exist_ok=True)
    
    driver = inicilizar_driver()
    
    try:
        for ano in anos_lista:
            # Serie A (1a divisão)
            print(f"[{ano} - Série A] Preparando...")
            url_a = get_league_url(COMPETITIONS['Serie_A'], ano, "Campeonato-Brasileiro-Serie-A")
            df_a = extract_standard_stats(url_a, ano, "Série A", driver)
            if not df_a.empty:
                df_a.to_csv(os.path.join(past_raw, f"dataset_bruto_SerieA_{ano}.csv"), index=False)
                print(f"  -> Salvo dataset_bruto_SerieA_{ano}.csv")
            
            # Serie B (2a divisão)
            print(f"[{ano} - Série B] Preparando...")
            url_b = get_league_url(COMPETITIONS['Serie_B'], ano, "Campeonato-Brasileiro-Serie-B")
            df_b = extract_standard_stats(url_b, ano, "Série B", driver)
            if not df_b.empty:
                df_b.to_csv(os.path.join(past_raw, f"dataset_bruto_SerieB_{ano}.csv"), index=False)
                print(f"  -> Salvo dataset_bruto_SerieB_{ano}.csv")
                
    finally:
        driver.quit() # Fecha o processo do motor Chromium
        print("=== Finalizado ===")

if __name__ == "__main__":
    # Teste de Inicialização do Bot Selenium (O Escopo pedido foi de 2014 a 2024 apenas Série A e B)
    anos_estudo = list(range(2014, 2025))
    rodar_extracao("Backtesting TCC 2014-2024", anos_estudo)
    
    print("Abra o código, desmarque as execuções de `rodar_extracao()` e execute este script para gerar a base de dados.")
