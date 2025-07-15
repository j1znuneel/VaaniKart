# views.py
import json
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import os
from dotenv import load_dotenv

load_dotenv()

LEMONFOX_KEY = os.getenv("LEMONFOX_KEY")

def extract_media_url(media_id, access_token):
    # Call Meta's API to get media URL
    url = f"https://graph.facebook.com/v19.0/{media_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get("url")
    return None

def send_reply_to_user(user_number, message, access_token, phone_number_id):
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": user_number,
        "type": "text",
        "text": {
            "body": message
        }
    }

    print("📤 Sending reply to user...")
    print("Payload:", json.dumps(data, indent=2))

    response = requests.post(url, headers=headers, json=data)

    print("📥 Meta API Response:")
    print("Status:", response.status_code)
    print("Response Body:", response.text)

    if response.status_code != 200:
        print("❌ Failed to send message. Check token, permissions, or payload format.")

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == "GET":
        # ✅ Handle Meta verification
        verify_token = os.getenv("VERIFY_TOKEN", "vaanikart_hackathon")
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if mode == "subscribe" and token == verify_token:
            print("WEBHOOK_VERIFIED") 
            return HttpResponse(challenge, status=200)
        else:
            return HttpResponse("Verification failed", status=403)

    elif request.method == "POST":
        # ✅ Handle real message delivery
        try:
            body = json.loads(request.body)
            print("=== Incoming Headers ===")
            print(dict(request.headers))
            print("=== Incoming Body ===")
            print(json.dumps(body, indent=2))
            entry = body["entry"][0]
            change = entry["changes"][0]
            value = change["value"]
            messages = value.get("messages", [])

            if messages:
                message = messages[0]
                user_number = message["from"]
                msg_type = message["type"]
                access_token = os.getenv("META_TOKEN")
                phone_number_id = os.getenv("META_PHONE_NUMBER_ID")
                
                
                if msg_type == "text":
                    user_text = message["text"]["body"]
                    reply_text = user_text.upper()
                    send_reply_to_user(user_number, reply_text, access_token, phone_number_id)
                if msg_type == "audio":
                    media_id = message["audio"]["id"]
                    # access_token = os.getenv("META_TOKEN")
                    # phone_number_id = os.getenv("META_PHONE_NUMBER_ID")

                    # Step 1: Get media URL
                    media_url = extract_media_url(media_id, access_token)

                    # Step 2: Download audio file
                    audio_resp = requests.get(media_url, headers={"Authorization": f"Bearer {access_token}"})

                    # Step 3: Transcribe via Lemonfox
                    lemonfox_key = os.getenv("LEMONFOX_KEY")
                    lemon_response = requests.post(
                        "https://api.lemonfox.ai/v1/audio/transcriptions",
                        headers={"Authorization": f"Bearer {lemonfox_key}"},
                        files={"file": ("audio.ogg", audio_resp.content)},
                        data={"language": "auto", "response_format": "text"}
                    )

                    transcript = lemon_response.json().get("text", "[Unable to transcribe]")

                    # Step 4: Send reply
                    send_reply_to_user(user_number, transcript, access_token, phone_number_id)
                    pass

        except Exception as e:
            print("Webhook error:", str(e))

        return JsonResponse({"status": "received"}, status=200)

    return HttpResponse(status=405)
