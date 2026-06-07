"""
Script de exploração da API Free Live Football Data (RapidAPI / FotMob)
Objetivo: Mapear endpoints disponíveis e puxar dados de jogadores brasileiros.
Uso: python src/coleta/explore_api.py
"""
import requests
import json
import time
import pandas as pd
import os

API_KEY = '2583f7d2admsh693169e03ddb263p1f4279jsn6996bf2ece7e'
HOST = 'free-api-live-football-data.p.rapidapi.com'
BASE = f'https://{HOST}'
HEADERS = {'x-rapidapi-host': HOST, 'x-rapidapi-key': API_KEY}

def get(endpoint, params=None):
    url = f'{BASE}{endpoint}'
    res = requests.get(url, headers=HEADERS, params=params)
    time.sleep(0.5)  # Respeitar rate limit
    return res.json()

def explorar_endpoints():
    """Mapeamento de todos os endpoints disponíveis na API"""
    candidatos = [
        '/football-player-statistics',
        '/football-player-stats',
        '/football-get-player',
        '/football-player-profile',
        '/football-player-career',
        '/football-get-player-career',
        '/football-team',
        '/football-get-team',
        '/football-team-squad',
        '/football-get-team-squad',
        '/football-league-players',
        '/football-get-league-players',
        '/football-season-players',
    ]
    print("=== Mapeando endpoints disponíveis ===")
    existentes = []
    for ep in candidatos:
        data = get(ep, {'playerid': '19533'})
        msg = data.get('message', '')
        if 'does not exist' in msg:
            print(f"  [NAO] {ep}")
        else:
            print(f"  [SIM] {ep} -> {str(data)[:100]}")
            existentes.append(ep)
    return existentes

def buscar_jogadores_brasileiros():
    """
    Busca jogadores brasileiros conhecidos e retorna seus IDs da API.
    Série A (Fla, Palmeiras, Galo) e Série B (Bragantino, Goiás, etc.)
    """
    # Jogadores alvos: mix de série A e jogadores que subiram da B
    nomes_alvo = [
        # Séria A - referência do modelo
        'Gabigol', 'Hulk', 'Raphael Veiga', 'Endrick', 'Gustavo Scarpa',
        'Dudu', 'Rony', 'Calleri', 'Luciano', 'Erison',
        # Goleiros Série A
        'Weverton', 'Everson', 'Cássio', 'John', 'Santos',
        # Defensores Série A
        'Murilo', 'Luan', 'Bruno Alves', 'David Luiz', 'Nino',
        # Meias Série A
        'Raphael Veiga', 'De Arrascaeta', 'Gerson', 'Patrick', 'Rodrigo Dourado',
        # Subindo da Série B (casos clássicos TCC)
        'Claudinho', 'Michael', 'Matheus Nascimento', 'Vitor Roque',
    ]
    
    jogadores_encontrados = []
    print("\n=== Buscando IDs de jogadores ===")
    for nome in nomes_alvo:
        data = get('/football-players-search', {'search': nome.split()[0]})
        sugs = data.get('response', {}).get('suggestions', [])
        for s in sugs:
            if s.get('type') == 'player':
                # Pegar o primeiro resultado relevante
                jogadores_encontrados.append({
                    'nome_busca': nome,
                    'id_api': s['id'],
                    'nome_api': s['name'],
                    'time': s.get('teamName', ''),
                })
                print(f"  {nome} -> id={s['id']} ({s['name']}, {s.get('teamName','')})")
                break
    return jogadores_encontrados

if __name__ == '__main__':
    # PASSO 1: Mapear endpoints
    disponíveis = explorar_endpoints()
    
    # PASSO 2: Buscar jogadores
    jogadores = buscar_jogadores_brasileiros()
    
    # Salvar mapeamento
    os.makedirs('data/raw', exist_ok=True)
    with open('data/raw/api_jogadores_ids.json', 'w', encoding='utf-8') as f:
        json.dump(jogadores, f, ensure_ascii=False, indent=2)
    print(f"\nSalvo: data/raw/api_jogadores_ids.json ({len(jogadores)} jogadores encontrados)")
