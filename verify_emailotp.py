import requests, json, os
from datetime import datetime, timedelta

# 🔐 Paso 1: Obtener token de acceso
token_url = os.environ.get("VERIFY_TOKEN_URL")
client_id = os.environ.get("VERIFY_CLIENT_ID")
client_secret = os.environ.get("VERIFY_CLIENT_SECRET")

payload = {
    "grant_type": "client_credentials",
    "scope": "openid",
    "client_id": client_id,
    "client_secret": client_secret
}
headers_token = {
    "accept": "application/json",
    "content-type": "application/x-www-form-urlencoded"
}

try:
    response = requests.post(token_url, data=payload, headers=headers_token)
    response.raise_for_status()
    access_token = response.json()["access_token"]
    print("✅ Token obtenido")
except Exception as e:
    print("❌ Error al obtener token:", e)
    exit()

# 🕒 Paso 2: Consultar logs de la última hora
logs_url = os.environ.get("VERIFY_LOGS_URL")
end_time = datetime.utcnow()
start_time = end_time - timedelta(hours=1)

headers_logs = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}
params = {
    "start": start_time.isoformat() + "Z",
    "end": end_time.isoformat() + "Z",
    "filter": "EmailOTP AND success"
}

try:
    logs_response = requests.get(logs_url, headers=headers_logs, params=params)
    logs_response.raise_for_status()
    logs = logs_response.json()
except Exception as e:
    print("❌ Error al consultar logs:", e)
    exit()

# 📢 Paso 3: Enviar alerta si hay eventos
if logs:
    slack_webhook = os.environ.get("SLACK_WEBHOOK")
    message = {
        "text": f"🚨 Se detectaron {len(logs)} eventos exitosos de EmailOTP en la última hora."
    }
    try:
        slack_response = requests.post(slack_webhook, json=message)
        slack_response.raise_for_status()
        print("✅ Alerta enviada")
    except Exception as e:
        print("❌ Error al enviar alerta:", e)
else:
    print("ℹ️ Sin eventos EmailOTP exitosos")
