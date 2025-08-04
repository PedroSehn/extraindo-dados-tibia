import json
from bs4 import BeautifulSoup
import os

def parse_html_file(file_path):
    """
    Analisa um único arquivo HTML para extrair as tarefas.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    
    # Encontra o nome da sala
    try:
        room_name = soup.find('div', class_='Text').text.strip()
    except AttributeError:
        print(f"Aviso: Não foi possível encontrar o nome da sala no arquivo {file_path}")
        room_name = "Sala Desconhecida"

    # Encontra a tabela de tarefas. A tabela correta é a segunda com a classe 'TableContent'.
    task_tables = soup.find_all('table', class_='TableContent')
    if len(task_tables) < 2:
        print(f"Aviso: Nenhuma tabela de tarefas encontrada no arquivo {file_path}")
        return []

    task_table = task_tables[1] 
    
    # Itera sobre as linhas da tabela, pulando o cabeçalho
    rows = task_table.find_all('tr')[1:]
    
    extracted_tasks = []
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) != 5:
            continue
        
        # Extrai os dados de cada célula
        try:
            task_number = int(cells[0].text.strip())
            task_name = cells[1].find('b').text.strip()
            amount = int(cells[2].text.strip().replace('.', ''))
            creatures = cells[3].text.strip()
            
            # Processa as recompensas
            rewards_cell = cells[4]
            primary_rewards = []
            secondary_rewards = []
            
            # Usa find_all com uma função lambda para encontrar as tags de recompensa
            reward_fonts = rewards_cell.find_all('font', color=lambda c: c in ['#27ae60', '#e74c3c'])

            for font_tag in reward_fonts:
                reward_text = font_tag.next_sibling
                if reward_text:
                    # Limpa o texto da recompensa
                    cleaned_text = reward_text.strip().replace('•', '').strip()
                    if cleaned_text:
                        if font_tag['color'] == '#27ae60':
                            primary_rewards.append(cleaned_text)
                        elif font_tag['color'] == '#e74c3c':
                            secondary_rewards.append(cleaned_text)

            task_data = {
                "room_name": room_name,
                "task_number": task_number,
                "task_name": task_name,
                "amount": amount,
                "creatures": creatures,
                "rewards": {
                    "primary": primary_rewards,
                    "secondary": secondary_rewards
                }
            }
            extracted_tasks.append(task_data)

        except (AttributeError, ValueError, IndexError) as e:
            print(f"Aviso: Pulando linha mal formatada no arquivo {file_path}. Erro: {e}")
            continue
            
    return extracted_tasks

def main():
    """
    Função principal para executar a extração e salvar o JSON.
    """
    # Lista dos arquivos a serem processados
    files_to_process = [
        'lothloriens-room.txt',
        'executioneer-room.txt',
        'morguls-room.txt',
        'corrupteds-room.txt',
        'nzoths-room.txt'
    ]
    
    all_tasks = []
    
    for filename in files_to_process:
        if os.path.exists(filename):
            print(f"Processando arquivo: {filename}...")
            all_tasks.extend(parse_html_file(filename))
        else:
            print(f"Erro: Arquivo {filename} não encontrado. Pulando.")
    
    # Salva todos os dados extraídos em um único arquivo JSON
    output_filename = 'tasks.json'
    with open(output_filename, 'w', encoding='utf-8') as json_file:
        # ensure_ascii=False para salvar caracteres especiais corretamente
        # indent=2 para uma formatação legível
        json.dump(all_tasks, json_file, ensure_ascii=False, indent=2)
        
    print(f"\nExtração concluída! Os dados foram salvos em '{output_filename}'.")

# Executa o script
if __name__ == "__main__":
    main()