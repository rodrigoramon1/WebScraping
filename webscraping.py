import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from pprint import pprint
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Definir o e-mail cadastrado pra teste
emailcadastrado = 'xxxxxxx1@xxxxx.xxxxx'  # Substitua pelo seu e-mail cadastrado

# Definir as funções e utilitários
def getListFromElements(caminho):
    Elemento = driver.find_elements(By.XPATH, caminho)
    Lista = []
    for item in Elemento:
        Lista.append(item.text)
    return Lista

def isLastPage():
    Web = driver.find_elements(By.XPATH, '//*[@id="row"]/div/div/nav/ul/li/a')
    close = True
    time.sleep(1)
    for item in Web:
        if item.text == '>':
            print('Aguarde por favor')
            item.click()
            close = False
            break
        else:
            close = True
    return close

def itensSeveros(Severidades, SeveridadeCritica=8):
    itens = 0
    for Severidade in Severidades:
        Test = (Severidade >= SeveridadeCritica)
        if Test:
            itens += 1
    return itens

# Configurar o webdriver do Chrome
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get('https://nvd.nist.gov/vuln/search')
driver.execute_cdp_cmd('Performance.enable', {})
t = driver.execute_cdp_cmd('Performance.getMetrics', {})
print(t)

# Definir os XPaths
XpathCVE = '//*/tbody/tr/th/strong/a'
XpathCVSS_v20 = '//*/tbody/tr/td[2]/span[2]'
XpathCVSS_v31 = '//*/tbody/tr/td[2]/span[1]'
XpathDescr = '//*/tbody/tr/td[1]/p'
XpathPubli = '//*/table/tbody/tr/td[1]/span'
xpathReferencia = '//*/table/tbody/tr/td/div/div[1]/div/div[1]/table/tbody/tr/td'
xpathConfig = '//*[@id="config-div-1"]/table/tbody/tr/td[1]/b'

# Buscar vulnerabilidades
print('Busca Avançada')
AdvavancedSearch = driver.find_element(value='SearchTypeAdvanced')
AdvavancedSearch.click()

print('Encontrando elementos da página')
Keyword = driver.find_element(value='Keywords')
Keyword.clear()

# Data de início e fim
StartDate = driver.find_element(value='published-start-date')
StartDate.clear()

EndDate = driver.find_element(value='published-end-date')
EndDate.clear()
# Nesse local coloque o que quer procurar no site, atenção com as datas não podem ser maiores de 120 dias de diferença
#A Data tambem precisa ser feita DIA\MES\ANO 
software = 'teams'
data_inicio = '01-01-2023'
data_fim = '01-30-2023'
time.sleep(5)

print('Busca')
Keyword.send_keys(software)
StartDate.send_keys(data_inicio)
EndDate.send_keys(data_fim)

# Definir listas para armazenar os dados das vulnerabilidades
lstCVE = []
lstCVSS_v20 = []
lstCVSS_v31 = []
lstDescr = []
lstPubli = []
sistema = []
Links = []
Referencia = []
Configs = []

# Clicar em Search
SubmitSearch = driver.find_element(value='vuln-search-submit')
SubmitSearch.click()
time.sleep(1)

LastPage = False
while not LastPage:
    lstCVE += getListFromElements(XpathCVE)
    lstCVSS_v20 += getListFromElements(XpathCVSS_v20)
    lstCVSS_v31 += getListFromElements(XpathCVSS_v31)
    lstDescr += getListFromElements(XpathDescr)
    lstPubli += getListFromElements(XpathPubli)
    LastPage = isLastPage()

if len(lstCVE) == 0:
    print('Nenhuma vulnerabilidade encontrada para', software)
elif len(lstCVE) == 1:
    print('Há uma nova vulnerabilidade encontrada')
else:
    print('Existem', len(lstCVE), 'novas vulnerabilidades encontradas')

# Realizar ações para cada vulnerabilidade encontrada
for i in lstCVE:
    Links.append('http://nvd.nist.gov/vuln/detail/' + i)
    sistema.append(software)

contador = len(Links)
print('Buscando referências das vulnerabilidades encontradas')
for link in Links:
    driver.get(link)

    lstConfig = getListFromElements(xpathConfig)
    lstReferencia = getListFromElements(xpathReferencia)

    print(contador, '|', end=' ')
    Referencia.append(lstReferencia)
    Configs.append(lstConfig)

    contador = contador - 1

    if len(lstCVE) > 0 and itensSeveros([1, 2, 3, 4, 8, 2.5, 9, 10], 8):
        print('Enviar e-mail para resumo:', emailcadastrado)
    else:
        print('\nNenhuma vulnerabilidade crítica encontrada')

Tabela = {
    'CVE': lstCVE,
    'CVSS_v20': lstCVSS_v20,
    'CVSS_v31': lstCVSS_v31,
    'Descrição': lstDescr,
    'Publicação': lstPubli,
    'Link': Links,
    'Sistema': sistema,
    'Referências': Referencia,
    'Configurações': Configs
}

print("Tabela final:\n")
print(Tabela)
# NESSE LOCAL CRIAMOS UMA CONTA SMTP no ELASTIC
# Configurar as informações de autenticação
SMTP_USERNAME = 'xxxxxx@xxxxx.com'
SMTP_PASSWORD = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
SMTP_HOST = 'smtp.elasticemail.com'
SMTP_PORT = 2525

# Configurar os detalhes do e-mail
sender_email = 'xxxxxxxxxxxxx@xxxxxxxxxx.com'
receiver_email = 'xxxxxxxxxxxxxxx@xxxxxxxx.com'
subject = 'Vulnerabilidade'
message = 'Anexo as Vulnerabilidades encontrada na data especificada'

# Configurar o caminho e o nome do arquivo de anexo
attachment_path = 'C:/Users/RodrigoRamon/AppData/Local/Programs/Python/Python311/resultado.xlsx'
attachment_name = 'resultado.xlsx'

# Criar o objeto MIMEMultipart para construir o e-mail
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = subject

# Adicionar o conteúdo do e-mail
msg.attach(MIMEText(message, 'plain'))

# Adicionar o anexo
with open(attachment_path, 'rb') as attachment:
    mime_attachment = MIMEBase('application', 'octet-stream')
    mime_attachment.set_payload(attachment.read())
    mime_attachment.add_header('Content-Disposition', f'attachment; filename="{attachment_name}"')
    encoders.encode_base64(mime_attachment)
    msg.attach(mime_attachment)

try:
    # Conectar ao servidor SMTP do Elastic Email
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    server.login(SMTP_USERNAME, SMTP_PASSWORD)

    # Enviar o e-mail
    server.sendmail(sender_email, receiver_email, msg.as_string())
    print('E-mail enviado com sucesso!')

except Exception as e:
    print('Erro ao enviar o e-mail:', str(e))

finally:
    # Encerrar a conexão com o servidor SMTP
    server.quit()
    print('Fim')
    driver.quit()
