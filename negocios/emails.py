import os
import requests

def enviar_correo(destinatario, asunto, contenido):
    url = 'https://api.brevo.com/v3/smtp/email'
    headers = {
        'accept': 'application/json',
        'api-key': os.environ.get('BREVO_API_KEY'),
        'content-type': 'application/json',
    }
    data = {
        'sender': {'email': os.environ.get('DEFAULT_FROM_EMAIL')},
        'to': [{'email': destinatario}],
        'subject': asunto,
        'textContent': contenido,
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response