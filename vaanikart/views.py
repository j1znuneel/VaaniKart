import json
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import os
from dotenv import load_dotenv

load_dotenv()

LEMONFOX_KEY = os.getenv("LEMONFOX_KEY")


def extract_media_url(media_id, access_token):
    print(f"🎧 Extracting media URL for media_id: {media_id}")
    url = f"https://graph.facebook.com/v19.0/{media_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    print(f"🔗 Media URL Response: {response.status_code} {response.text}")
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
        verify_token = os.getenv("VERIFY_TOKEN", "vaanikart_hackathon")
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if mode == "subscribe" and token == verify_token:
            print("✅ WEBHOOK_VERIFIED")
            return HttpResponse(challenge, status=200)
        else:
            print("❌ Webhook verification failed.")
            return HttpResponse("Verification failed", status=403)

    elif request.method == "POST":
        try:
            body = json.loads(request.body)
            print("=== 📩 Incoming Headers ===")
            print(dict(request.headers))
            print("=== 📦 Incoming Body ===")
            print(json.dumps(body, indent=2))

            entry = body["entry"][0]
            change = entry["changes"][0]
            value = change["value"]

            # 🧠 Debug: Log entire value block
            print("🧠 Message block:", json.dumps(value, indent=2))

            messages = value.get("messages", [])
            if messages:
                print("✅ Message received.")

                message = messages[0]
                user_number = message.get("from", "unknown")
                msg_type = message.get("type", "none")
                access_token = os.getenv("META_TOKEN")
                phone_number_id = os.getenv("META_PHONE_NUMBER_ID")

                print(f"👤 From: {user_number}")
                print(f"📝 Message Type: {msg_type}")

                if msg_type == "text":
                    user_text = message["text"]["body"]
                    print(f"✉️ Text Message: {user_text}")
                    reply_text = user_text.upper()
                    send_reply_to_user(user_number, reply_text, access_token, phone_number_id)

                elif msg_type == "audio":
                    print("🎤 Audio message detected.")
                    media_id = message["audio"]["id"]
                    print(f"🎧 Media ID: {media_id}")

                    media_url = extract_media_url(media_id, access_token)
                    if media_url is None:
                        print("❌ Could not get media URL.")
                        send_reply_to_user(user_number, "[Error: Couldn't access audio]", access_token, phone_number_id)
                        return JsonResponse({"status": "failed"}, status=500)

                    # 🔽 Download audio
                    print(f"⬇️ Downloading audio from: {media_url}")
                    audio_resp = requests.get(media_url, headers={"Authorization": f"Bearer {access_token}"})
                    print(f"📥 Audio Response: {audio_resp.status_code}")

                    # 🦊 Lemonfox API
                    lemonfox_key = os.getenv("LEMONFOX_KEY")
                    print("🦊 Sending audio to Lemonfox for transcription...")

                    lemon_response = requests.post(
                    "https://api.lemonfox.ai/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {lemonfox_key}"},
                    files={"file": ("audio.ogg", audio_resp.content)},
                    data={"language": "hi", "response_format": "text"}  # CHANGE HERE
                )


                    print(f"🦊 Lemonfox Status: {lemon_response.status_code}")
                    print("🦊 Lemonfox Response:", lemon_response.text)

                    if lemon_response.status_code == 200:
                        transcript = lemon_response.text.strip()
                    else:
                        transcript = "[Unable to transcribe]"

                    send_reply_to_user(user_number, transcript, access_token, phone_number_id)

                else:
                    print(f"❓ Unsupported message type: {msg_type}")
            else:
                print("ℹ️ No 'messages' array found in webhook payload.")

        except Exception as e:
            print("❗ Webhook processing error:", str(e))

        return JsonResponse({"status": "received"}, status=200)

    return HttpResponse(status=405)
