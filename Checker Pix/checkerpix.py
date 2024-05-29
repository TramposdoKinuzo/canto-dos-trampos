import requests
import os
from urllib3.exceptions import InsecureRequestWarning
import re
from pathlib import Path
import time

def limparcmd():
    os.system('cls' if os.name == 'nt' else 'clear')

limparcmd()
print("                                                                            ")
print("_________ .__                   __                  __________._______  ___ ")
print("\_   ___ \|  |__   ____   ____ |  | __ ___________  \______   \   \   \/  / ")
print("/    \  \/|  |  \_/ __ \_/ ___\|  |/ // __ \_  __ \  |     ___/   |\     /  ")
print("\     \___|   Y  \  ___/\  \___|    <\  ___/|  | \/  |    |   |   |/     \  ")
print(" \______  /___|  /\___  >\___  >__|_ \\___  >__|     |____|   |___/___/\  \ ")
print("        \/     \/     \/     \/     \/    \/                            \_/ ")
print("                                                                            ")
print("                           Checker PIX by Kinuzo                            ")
print("                                                                            ")

def separar_ghy(biscoito):
    with open(biscoito, 'r', encoding='utf-8') as file:
        content = file.read()

    batendo = re.findall(r'ghy-\S+', content)

    pasta_cookies = 'Cookies'
    Path(pasta_cookies).mkdir(exist_ok=True)

    for i, match in enumerate(batendo, 1):
        output_file = os.path.join(pasta_cookies, f'{i}.txt')
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(match)

biscoito = 'cookies.txt'
separar_ghy(biscoito)

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

api_url = 'https://www.mercadopago.com.br/money-out/transfer/api/pix-account-unified-p2p/search?type=cpf&id={}&action=da_pix_search_account'

pasta_cookies = 'Cookies'
pasta_arquivos = [f for f in os.listdir(pasta_cookies) if f.endswith('.txt')]

with open('dados.txt', 'r') as file:
    ids = file.readlines()

resultado_com_cor = []
resultado_sem_cor = []

rate_limit = False

for id in ids:
    id = id.strip()

    while True:
        if rate_limit and not pasta_arquivos:
            print("Sem mais cookies na lista, parando o checker.")
            break

        cookie_encontrado = False
        for arquivo_cookie in pasta_arquivos:
            diretorio = os.path.join(pasta_cookies, arquivo_cookie)

            with open(diretorio, 'r') as file:
                ssid = file.read().replace('\n', '')

            ssid_header = f'ssid={ssid}'

            session = requests.Session()
            session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0'})

            url = api_url.format(id)
            response = session.get(url, verify=False, headers={'Cookie': ssid_header})

            try:
                json_response = response.json()

                if 'status' in json_response:
                    status = json_response['status']

                    if status == 'success':
                        account_info = json_response['model']['accounts'][0]['data']
                        cpf = account_info['key_value']
                        details = json_response['model']['accounts'][0]['details']

                        if len(details) >= 2:
                            name = details[0]['value']
                            bank = details[1]['value']
                            result_text = f'{cpf} - {name} - {bank} > Com chave PIX'
                        else:
                            result_text = f'{cpf} > Com chave PIX'

                        result_text = result_text
                        resultado_com_cor.append(result_text)
                        resultado_sem_cor.append(result_text)

                        print(result_text)
                        pasta_arquivos.remove(arquivo_cookie)
                        cookie_encontrado = True
                        break

                    elif status == 'error' and json_response.get('texts', {}).get('message') == 'A conta não foi encontrada.':
                        result_text = f'{id} > Sem chave PIX - Erro: A conta não foi encontrada.'
                        resultado_com_cor.append(result_text)
                        resultado_sem_cor.append(result_text)
                        print(result_text)
                        pasta_arquivos.remove(arquivo_cookie)
                        cookie_encontrado = True
                        break

                    elif status == 'warning' and 'rate_limit_pix' in json_response.get('model', {}).get('labels', {})[0].get('text', '').lower():
                        pasta_arquivos.remove(arquivo_cookie)
                        print(f'Removendo o arquivo de cookie: {arquivo_cookie}')
                        rate_limit = True

                else:
                    print(f"Resposta invalida: {json_response}")

            except ValueError:
                print(f"Resposta JSON invalida: {response.text}")

            time.sleep(1)

        if cookie_encontrado or rate_limit:
            break

with open('resultados.txt', 'w', encoding='utf-8') as file:
    file.write('\n'.join(resultado_sem_cor))
