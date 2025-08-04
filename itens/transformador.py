import json
import os
import re
import copy

def obter_molde_item_v2():
    """Retorna um dicionário com a estrutura V2 padrão para um novo item."""
    return {
      "id": None, "nome": None, "nome_arquivo_origem": None, "imagem_url": None,
      "tipo": None, "level_minimo": 0, "vocacoes": [], "peso": 0.0,
      "atributos": {
        "armadura": 0, "defesa": 0, "slots": 0,
        "dano": {
          "fisico": 0, "terra": 0, "fogo": 0, "gelo": 0,
          "energia": 0, "sagrado": 0, "morte": 0
        },
        "resistencias": {
          "fisico":   { "flat": 0, "percent": 0 }, "terra":    { "flat": 0, "percent": 0 },
          "fogo":     { "flat": 0, "percent": 0 }, "gelo":     { "flat": 0, "percent": 0 },
          "energia":  { "flat": 0, "percent": 0 }, "sagrado":  { "flat": 0, "percent": 0 },
          "morte":    { "flat": 0, "percent": 0 }
        },
        "bonus": {
          "aumento_cura": 0,
          "skills": {
            "axe_fighting": 0, "club_fighting": 0, "sword_fighting": 0,
            "distance_fighting": 0, "fist_fighting": 0, "shielding": 0
          },
          "stats": { "magic_level": 0, "velocidade": 0 },
          "efeitos_especiais": { "life_drain": 0, "mana_drain": 0 }
        }
      },
      "texto_original": {}
    }

# Mapeamento de nomes nos JSONs para as chaves da nossa estrutura V2
MAPA_ATRIBUTOS = {
    'physical': 'fisico', 'fire': 'fogo', 'earth': 'terra', 'energy': 'energia',
    'ice': 'gelo', 'holy': 'sagrado', 'death': 'morte', 'healing': 'aumento_cura',
    'sword fighting': 'sword_fighting', 'axe fighting': 'axe_fighting',
    'club fighting': 'club_fighting', 'distance fighting': 'distance_fighting',
    'fist fighting': 'fist_fighting', 'shielding': 'shielding',
    'magic level': 'magic_level', 'speed': 'velocidade', 'velocidade': 'velocidade',
    'life drain': 'life_drain', 'mana drain': 'mana_drain'
}

def parse_atributos(item_antigo, item_novo):
    """Lê as strings de atributos e preenche a estrutura do novo item."""
    
    for campo in ['Atq', 'Dano_Elemental']:
        dano_str = item_antigo.get(campo, '')
        if dano_str:
            matches = re.findall(r'(\d+)\s*([a-zA-Z]*)', dano_str, re.IGNORECASE)
            for value, element in matches:
                if not element or element.lower() == 'physical':
                    item_novo['atributos']['dano']['fisico'] += int(value)
                else:
                    element_key = MAPA_ATRIBUTOS.get(element.lower())
                    if element_key and element_key in item_novo['atributos']['dano']:
                        item_novo['atributos']['dano'][element_key] += int(value)

    protecao_str = item_antigo.get('Proteção', '')
    if protecao_str:
        matches = re.findall(r'([a-zA-Z]+)\s*([+\-]\d+)%', protecao_str, re.IGNORECASE)
        for element, value in matches:
            element_key = MAPA_ATRIBUTOS.get(element.lower())
            if element_key and element_key in item_novo['atributos']['resistencias']:
                item_novo['atributos']['resistencias'][element_key]['percent'] += int(value)

    bonus_str = item_antigo.get('Bônus', '')
    if bonus_str:
        partes = bonus_str.split(',')
        for parte in partes:
            match = re.search(r'([a-zA-Z\s]+)\s*\+(\d+)', parte, re.IGNORECASE)
            if match:
                nome_bonus = match.group(1).strip().lower()
                valor_bonus = int(match.group(2))
                
                chave_bonus = MAPA_ATRIBUTOS.get(nome_bonus)
                if chave_bonus:
                    if chave_bonus in item_novo['atributos']['bonus']['skills']:
                        item_novo['atributos']['bonus']['skills'][chave_bonus] += valor_bonus
                    elif chave_bonus in item_novo['atributos']['bonus']['stats']:
                        item_novo['atributos']['bonus']['stats'][chave_bonus] += valor_bonus
    
    return item_novo

def transformar_item(item_antigo, tipo_item, nome_arquivo):
    """Converte um objeto de item do formato antigo para a nova estrutura V2."""
    item_novo = obter_molde_item_v2()

    # Mapeia os campos básicos
    item_novo['nome'] = item_antigo.get('Nome')
    item_novo['nome_arquivo_origem'] = nome_arquivo
    item_novo['imagem_url'] = item_antigo.get('Imagem_URL')
    item_novo['tipo'] = tipo_item
    
    # --- INÍCIO DA CORREÇÃO ---
    # Usando blocos try-except para a conversão mais segura possível.
    try:
        item_novo['level_minimo'] = int(item_antigo.get('Lvl', 0))
    except (ValueError, TypeError):
        item_novo['level_minimo'] = 0
    
    try:
        item_novo['peso'] = float(item_antigo.get('Peso', 0.0))
    except (ValueError, TypeError):
        item_novo['peso'] = 0.0

    try:
        item_novo['atributos']['armadura'] = int(item_antigo.get('Arm', 0))
    except (ValueError, TypeError):
        item_novo['atributos']['armadura'] = 0

    try:
        item_novo['atributos']['defesa'] = int(item_antigo.get('Def', 0))
    except (ValueError, TypeError):
        item_novo['atributos']['defesa'] = 0

    try:
        item_novo['atributos']['slots'] = int(item_antigo.get('Slots', 0))
    except (ValueError, TypeError):
        item_novo['atributos']['slots'] = 0
    # --- FIM DA CORREÇÃO ---

    voc_str = item_antigo.get('Voc', 'Todas')
    item_novo['vocacoes'] = [v.strip() for v in voc_str.replace(' and ', ',').split(',')] if voc_str != 'Todas' else ['Todas']
    
    item_novo['texto_original']['atq'] = item_antigo.get('Atq')
    item_novo['texto_original']['bonus'] = item_antigo.get('Bônus')
    item_novo['texto_original']['protecao'] = item_antigo.get('Proteção')
    item_novo['texto_original']['dano_elemental'] = item_antigo.get('Dano_Elemental')

    item_novo = parse_atributos(item_antigo, item_novo)

    return item_novo


if __name__ == "__main__":
    diretorio_de_entrada = 'todos_os_jsons'
    arquivo_de_saida = 'banco_de_dados_itens.json'
    lista_final_de_itens = []
    item_id_counter = 1

    print(f"Iniciando transformação dos arquivos em '{diretorio_de_entrada}'...")

    if not os.path.isdir(diretorio_de_entrada):
        print(f"ERRO: Diretório de entrada '{diretorio_de_entrada}' não encontrado.")
        print("Certifique-se de que o script está na mesma pasta que o diretório 'todos_os_jsons'.")
    else:
        for nome_arquivo in os.listdir(diretorio_de_entrada):
            if nome_arquivo.endswith(".json"):
                caminho_arquivo = os.path.join(diretorio_de_entrada, nome_arquivo)
                
                tipo_item = nome_arquivo.replace('.json', '').split('_')[-1]

                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    dados_antigos = json.load(f)
                    
                    print(f"Processando {len(dados_antigos)} itens de '{nome_arquivo}'...")
                    
                    for item_antigo in dados_antigos:
                        item_transformado = transformar_item(item_antigo, tipo_item, nome_arquivo)
                        item_transformado['id'] = item_id_counter
                        lista_final_de_itens.append(item_transformado)
                        item_id_counter += 1

        with open(arquivo_de_saida, 'w', encoding='utf-8') as f:
            json.dump(lista_final_de_itens, f, ensure_ascii=False, indent=4)

        print(f"\nProcesso concluído! {len(lista_final_de_itens)} itens foram processados.")
        print(f"O banco de dados final foi salvo em '{arquivo_de_saida}'.")