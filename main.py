import requests

request = requests.get('https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/')

print(request.status_code)
print(request.text)