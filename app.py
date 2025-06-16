import os
import requests
from flask import Flask, request, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

ESPOCRM_URL = os.getenv("ESPOCRM_URL")
ESPOCRM_API_KEY = os.getenv("ESPOCRM_API_KEY")

@app.route('/webhook', methods=['GET', 'POST'])
def chatwoot_webhook():
    if request.method == 'GET':
        return render_template('crm_info.html', loading=True)

    # A partir daqui é a lógica do POST
    print("--- LOG DE DEPURAÇÃO: REQUISIÇÃO POST RECEBIDA ---")

    if not ESPOCRM_URL or not ESPOCRM_API_KEY:
        error_message = "Erro de configuração no servidor: As variáveis ESPOCRM_URL ou ESPOCRM_API_KEY não foram definidas."
        print(f"LOG DE ERRO: {error_message}")
        return render_template('crm_info.html', error=error_message)
        
    try:
        # Tenta pegar o JSON. Se falhar, é um grande indício.
        data = request.json
        print(f"LOG DE DEPURAÇÃO: Dados recebidos do Chatwoot -> {data}")

        contact = data.get('contact', {})
        email = contact.get('email')
        print(f"LOG DE DEPURAÇÃO: Email extraído -> {email}")

        if not email:
            print("LOG DE ERRO: Contato no Chatwoot não possui email.")
            return render_template('crm_info.html', error="Contato sem e-mail no Chatwoot.")

        headers = {
            'X-Api-Key': ESPOCRM_API_KEY,
            'Content-Type': 'application/json'
        }
        
        search_url = f"{ESPOCRM_URL}Contact?where[0][type]=equals&where[0][attribute]=emailAddress&where[0][value]={email}"
        print(f"LOG DE DEPURAÇÃO: Consultando a URL -> {search_url}")
        
        response = requests.get(search_url, headers=headers)
        print(f"LOG DE DEPURAÇÃO: Resposta do EspoCRM (Status Code) -> {response.status_code}")
        
        response.raise_for_status()

        search_result = response.json()
        print(f"LOG DE DEPURAÇÃO: Resultado da busca -> {search_result}")
        
        espocrm_base_url = ESPOCRM_URL.replace("/api/v1/", "/")

        if search_result.get('total') > 0:
            print("LOG DE DEPURAÇÃO: Contato encontrado. Renderizando dados.")
            contact_data = search_result.get('list')[0]
            return render_template('crm_info.html', contact=contact_data, espocrm_base_url=espocrm_base_url)
        else:
            print("LOG DE DEPURAÇÃO: Contato não encontrado. Renderizando aviso.")
            return render_template('crm_info.html', not_found=True, email=email, espocrm_base_url=espocrm_base_url)

    except Exception as e:
        # Captura qualquer erro no processo e o exibe no log e na tela
        print(f"--- LOG DE ERRO INESPERADO: {e} ---")
        return render_template('crm_info.html', error=f"Ocorreu um erro inesperado no servidor: {e}")
