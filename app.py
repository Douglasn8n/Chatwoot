import os
import requests
from flask import Flask, request, render_template

app = Flask(__name__)

# As variáveis de ambiente continuam as mesmas
ESPOCRM_URL = os.getenv("ESPOCRM_URL")
ESPOCRM_API_KEY = os.getenv("ESPOCRM_API_KEY")

@app.route('/webhook', methods=['GET']) # Agora só precisamos de GET
def chatwoot_webhook():
    # Verifica se as variáveis de configuração existem
    if not ESPOCRM_URL or not ESPOCRM_API_KEY:
        error_message = "Erro de configuração no servidor: As variáveis de ambiente do EspoCRM não foram definidas."
        return render_template('crm_info.html', error=error_message)

    try:
        # Pega o email diretamente do parâmetro da URL (?email=...)
        email = request.args.get('email')

        # Se o Chatwoot não enviar o email (contato sem email), mostra um aviso
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

    except Exception as e:
        return render_template('crm_info.html', error=f"Ocorreu um erro inesperado: {e}")
