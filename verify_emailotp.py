import requests, os
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

# 🕒 Paso 2: Consultar logs de MFA de la última hora
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
    "filter": "eventType eq MFA"
}

try:
    logs_response = requests.get(logs_url, headers=headers_logs, params=params)
    print("📡 Código de respuesta:", logs_response.status_code)
    logs_response.raise_for_status()
    logs = logs_response.json()
except ValueError:
    print("❌ La respuesta no es JSON válido:")
    print(logs_response.text)
    exit()
except Exception as e:
    print("❌ Error al consultar logs:", e)
    exit()

# 📊 Paso 3: Contar resultados por estado
success_count = 0
failure_count = 0

for event in logs:
    result = event.get("result", "").lower()
    if result == "success":
        success_count += 1
    elif result == "failure":
        failure_count += 1

# 📢 Paso 4: Enviar resumen a Slack
slack_webhook = os.environ.get("SLACK_WEBHOOK")
message = {
    "text": (
        f"📊 *Resumen de actividad MFA (última hora)*\n"
        f"✅ Éxitos: {success_count}\n"
        f"❌ Fallos: {failure_count}"
    )
}

try:
    slack_response = requests.post(slack_webhook, json=message)
    slack_response.raise_for_status()
    print("✅ Resumen enviado a Slack")
except Exception as e:
    print("❌ Error al enviar alerta:", e)
