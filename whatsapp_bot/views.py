from django.http import JsonResponse, HttpResponse
import json
import os
import requests
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

load_dotenv()

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
ACCESS_TOKEN = os.environ.get("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")

@csrf_exempt
def whatsapp_webhook(request):

    # ---- Verification ----
    if request.method == "GET":
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return HttpResponse(challenge)
        return HttpResponse("Verification failed", status=403)

    # ---- Incoming Message ----
    if request.method == "POST":
        body = json.loads(request.body)

        try:
            entry = body["entry"][0]
            changes = entry["changes"][0]
            value = changes["value"]

            print('Value',value)

            if "messages" in value:
                message = value["messages"][0]
                sender = message["from"]
                text = message["text"]["body"]

                print("Sender:", sender)
                print("Message:", text)

                send_whatsapp_message(sender, "Hello 👋 I received your message!")

        except Exception as e:
            print("Error:", e)

        return JsonResponse({"status": "received"})


def send_whatsapp_message(to, message):

    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(url, headers=headers, json=data)

    print("Reply Status:", response.status_code)
    print("Reply Response:", response.text)