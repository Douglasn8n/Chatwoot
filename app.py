import os
import requests
from flask import Flask, request, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# As variáveis ESPOCRM_URL e ESPOCRM_API_KEY serão lidas do ambiente do Render
ESPOCRM_URL = os.getenv("ESPOCRM_URL")
ESPOCRM_API_KEY = os.getenv("ESPOCRM_API_KEY")

@app.route('/webhook', methods=['POST'])
def chatwoot_webhook():
    # Verifica se as variáveis de ambiente foram carregadas
    if not ESPOCRM_URL or not ESPOCRM_API_KEY:
        error_message = "Erro de configuração no servidor: As variáveis ESPOCRM_URL ou ESPOCRM_API_KEY não foram definidas."
        return render_template('crm_info.html', error=error_message)

    try:
        data = request.json
        contact = data.get('contact', {})
        email = contact.get('email')

        if not email:
            return render_template('crm_info.html', error="Contato sem e-mail no Chatwoot.")

        headers = {
            'X-Api-Key': ESPOCRM_API_KEY,
            'Content-Type': 'application/json'
        }

        search_url = f"{ESPOCRM_URL}Contact?where[0][type]=equals&where[0][attribute]=emailAddress&where[0][value]={email}"

        response = requests.get(search_url, headers=headers)
        response.raise_for_status()

        search_result = response.json()

        espocrm_base_url = ESPOCRM_URL.replace("/api/v1/", "/")

        if search_result.get('total') > 0:
            contact_data = search_result.get('list')[0]
            return render_template('crm_info.html', contact=contact_data, espocrm_base_url=espocrm_base_url)
        else:
            return render_template('crm_info.html', not_found=True, email=email, espocrm_base_url=espocrm_base_url)

    except requests.exceptions.RequestException as e:
        return render_template('crm_info.html', error=f"Erro de comunicação com o EspoCRM: {e}")
    except Exception as e:
        return render_template('crm_info.html', error=f"Ocorreu um erro inesperado: {e}")

# Rota de teste para verificar se o app está no ar
@app.route('/')
def index():
    return "A ponte Chatwoot-EspoCRM está no ar!"
