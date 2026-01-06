import requests
import zipfile
import os
import bs4

class FetchDadosAbertos:
    def __init__(self, diretorio_dados:str):
        self.diretorio_dados = diretorio_dados

    def download_zip_folder(self, base_url: str, ano: int, mes: int):
        """
        Docstring for download_zip_folder
        
        :param self: Description
        :param base_url: Description
        :type base_url: str
        :param ano: Description
        :type ano: int
        :param mes: Description
        :type mes: int
        """
        # URL da pasta com os arquivos
        url = f'{base_url}/{ano:04d}-{mes:02d}/'

        try:
            # Buscar a página
            response = requests.get(url=url, timeout=30)
            response.raise_for_status()
            
            soup = bs4.BeautifulSoup(response.content, 'html.parser')
            
            # Encontrar todos os links .zip
            link_list = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.endswith('.zip') and (href.startswith('Estabelecimentos') or href.startswith('Cnaes') or href.startswith('Empresas')):
                    link_list.append(href)
            
            if not link_list:
                print(f"⚠ Nenhum arquivo .zip encontrado em {url}")
                return
            
            print(f"Encontrados {len(link_list)} arquivos .zip para {ano}-{mes:02d}")
            
            # Download de cada arquivo
            for link in link_list:
                # Construir URL completa
                if link.startswith('http'):
                    zip_url = link
                    nome_arquivo = link.split('/')[-1]
                else:
                    zip_url = url + link
                    nome_arquivo = link
                
                # Caminho completo para salvar o arquivo
                caminho_arquivo = os.path.join(self.diretorio_dados, nome_arquivo)
                
                # Verificar se já existe
                if os.path.exists(caminho_arquivo):
                    print(f"⊘ {nome_arquivo} já existe, pulando...")
                    continue
                
                print(f"Baixando: {nome_arquivo}...")
                
                try:
                    response = requests.get(zip_url, stream=True, timeout=60)
                    response.raise_for_status()
                    
                    # Salvar o arquivo
                    with open(caminho_arquivo, 'wb') as file:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:  # Filtrar chunks vazios
                                file.write(chunk)
                    
                    # Verificar se o arquivo foi salvo corretamente
                    if os.path.getsize(caminho_arquivo) > 0:
                        print(f"✓ {nome_arquivo} baixado com sucesso")
                    else:
                        print(f"✗ {nome_arquivo} está vazio")
                        os.remove(caminho_arquivo)
                        
                except requests.exceptions.RequestException as e:
                    print(f"✗ Erro ao baixar {nome_arquivo}: {e}")
                    # Remover arquivo parcial se existir
                    if os.path.exists(caminho_arquivo):
                        os.remove(caminho_arquivo)
                except Exception as e:
                    print(f"✗ Erro inesperado com {nome_arquivo}: {e}")
                    if os.path.exists(caminho_arquivo):
                        os.remove(caminho_arquivo)
            
            print(f"Download concluído para {ano}-{mes:02d}")
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Erro ao acessar {url}: {e}")
        except Exception as e:
            print(f"✗ Erro inesperado: {e}")

    def fetch_data_from_zip_folder(self):
        """
        Docstring for fetch_data_from_zip_folder
        
        :param self: Description
        """
        try:
            for zipped_file in os.listdir(self.diretorio_dados):
                with zipfile.ZipFile(os.path.join(self.diretorio_dados, zipped_file), 'r') as zip_ref:
                    zip_ref.extractall(self.diretorio_dados)
        except Exception as e:
            print(f"✗ Erro ao extrair arquivos zip: {e}")

if __name__ == "__main__":
    diretorio = './data/raw/'
    base_url = 'https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/'
    ano = 2025
    mes = 12
    fetcher = FetchDadosAbertos(diretorio_dados=diretorio)
    fetcher.download_zip_folder(base_url=base_url, ano=ano, mes=mes)