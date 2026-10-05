import csv
import math

def run_analysis():
    jog_path = 'data/processed_tcc/jogadores_consolidado.csv'
    camp_path = 'data/processed_tcc/campeonato_consolidado.csv'
    
    with open(jog_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        jogadores = list(reader)
        
    with open(camp_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        campeonatos = list(reader)
        
    print(f"Total registros jogadores: {len(jogadores)}")
    print(f"Total registros campeonatos: {len(campeonatos)}")
    
    # Map campeonatos by (Time, Ano, Divisao)
    camp_map = {}
    for c in campeonatos:
        key = (c['Squad'], c['Ano'], c['Divisao'])
        camp_map[key] = c
        
    pos_counts = {}
    valid_count = 0
    discarded_count = 0
    
    train_count = 0
    test_count = 0
    
    for j in jogadores:
        try:
            minutos = float(j.get('Min', 0))
        except:
            minutos = 0.0
            
        pos = j.get('Pos', '').split(',')[0]
        pos_map = {'FW': 'Atacante', 'MF': 'Meio Campo', 'DF': 'Defensor', 'GK': 'Goleiro'}
        pos_grupo = pos_map.get(pos, 'Outros')
        
        if minutos < 300:
            discarded_count += 1
            continue
            
        valid_count += 1
        pos_counts[pos_grupo] = pos_counts.get(pos_grupo, 0) + 1
        
        try:
            ano = int(j.get('Ano', 0))
        except:
            ano = 0
            
        if ano <= 2020:
            train_count += 1
        else:
            test_count += 1
            
    print(f"Descartados (Min < 300): {discarded_count}")
    print(f"Retidos (Min >= 300): {valid_count}")
    print(f"Por posição: {pos_counts}")
    print(f"Treino (<=2020): {train_count}, Teste (>=2021): {test_count}")

if __name__ == '__main__':
    run_analysis()
