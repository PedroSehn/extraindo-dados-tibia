import json
from bs4 import BeautifulSoup
import os

def extrair_dados_de_arquivo(arquivo_html, arquivo_json):
    """
    Extrai os dados de uma tabela em um arquivo HTML, incluindo o link da imagem,
    e salva o resultado como um arquivo JSON com chaves sem espaços.
    
    Args:
        arquivo_html (str): O caminho para o arquivo HTML de entrada.
        arquivo_json (str): O caminho para o arquivo JSON de saída.
    """
    print(f"Processando arquivo: {arquivo_html}...")
    try:
        with open(arquivo_html, 'r', encoding='utf-8') as f:
            conteudo = f.read()

        soup = BeautifulSoup(conteudo, 'html.parser')

        tabela = soup.find('table', id='tabelaDPL')
        if not tabela:
            print(f"  -> Aviso: Nenhuma tabela com id 'tabelaDPL' encontrada em {arquivo_html}.")
            return

        cabecalhos_html = tabela.find('thead').find_all('th')
        
        cabecalhos = [
            th.get_text(strip=True).replace('\\n', ' ').replace(' ', '_') 
            for th in cabecalhos_html
        ]

        img_col_index = -1
        for i, th_text in enumerate(cabecalhos):
            if th_text == "":
                cabecalhos[i] = 'Imagem_URL'
                img_col_index = i
                break
    
        dados_finais = []
        tbody = tabela.find('tbody')
        if not tbody:
            print(f"  -> Aviso: Tabela em {arquivo_html} não possui corpo (tbody).")
            return

        for linha in tbody.find_all('tr'):
            celulas = linha.find_all('td')
            item_dados = {}
            
            for i, celula in enumerate(celulas):
                if i < len(cabecalhos):
                    cabecalho = cabecalhos[i]
                    
                    if i == img_col_index:
                        img_tag = celula.find('img')
                        if img_tag and 'src' in img_tag.attrs:
                            item_dados[cabecalho] = f"https://www.tibiawiki.com.br{img_tag['src']}"
                        else:
                            item_dados[cabecalho] = None
                    else:
                        texto_limpo = ' '.join(celula.get_text(separator=' ', strip=True).split())
                        item_dados[cabecalho] = texto_limpo
            
            if item_dados:
                item_dados.pop('', None) 
                dados_finais.append(item_dados)

        with open(arquivo_json, 'w', encoding='utf-8') as f:
            json.dump(dados_finais, f, ensure_ascii=False, indent=4)

        print(f"  -> Sucesso! Dados salvos em '{arquivo_json}'.")

    except FileNotFoundError:
        print(f"  -> Erro: O arquivo {arquivo_html} não foi encontrado.")
    except Exception as e:
        print(f"  -> Erro inesperado ao processar o arquivo {arquivo_html}: {e}")

if __name__ == "__main__":
    diretorio_raiz = '.' 
    
    # --- INÍCIO DA MUDANÇA ---
    # Define o nome da pasta de saída e a cria se não existir.
    pasta_de_saida = "todos_os_jsons"
    os.makedirs(pasta_de_saida, exist_ok=True)
    
    print(f"Iniciando busca por arquivos .txt...")
    print(f"Os arquivos JSON serão salvos na pasta '{pasta_de_saida}'.")

    # Usa os.walk para percorrer a pasta atual e todas as subpastas.
    for pasta_atual, subpastas, arquivos in os.walk(diretorio_raiz):
        # Ignora a própria pasta de saída para não processar arquivos dentro dela
        if pasta_de_saida in pasta_atual:
            continue

        for nome_do_arquivo in arquivos:
            if nome_do_arquivo.endswith(".txt"):
                caminho_completo_txt = os.path.join(pasta_atual, nome_do_arquivo)
                
                # Lógica para criar um nome de arquivo único
                nome_base_arquivo = nome_do_arquivo.replace('.txt', '')
                caminho_relativo = os.path.relpath(pasta_atual, diretorio_raiz)
                
                if caminho_relativo != '.':
                    # Se o arquivo está numa subpasta, adiciona o nome da pasta como prefixo
                    prefixo = caminho_relativo.replace(os.path.sep, '_')
                    nome_json_saida = f"{prefixo}_{nome_base_arquivo}.json"
                else:
                    # Se o arquivo está na pasta raiz, mantém o nome original
                    nome_json_saida = f"{nome_base_arquivo}.json"

                # Monta o caminho completo do arquivo de saída na pasta centralizada
                caminho_completo_json = os.path.join(pasta_de_saida, nome_json_saida)
                
                extrair_dados_de_arquivo(caminho_completo_txt, caminho_completo_json)
    # --- FIM DA MUDANÇA ---
            
    print("\nProcesso concluído.")